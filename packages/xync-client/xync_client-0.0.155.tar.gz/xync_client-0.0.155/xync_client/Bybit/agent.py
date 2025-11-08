import asyncio
import logging
import re
from asyncio import sleep, gather
from asyncio.tasks import create_task
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from enum import IntEnum
from hashlib import sha256
from http.client import HTTPException
from math import floor
from typing import Literal

import pyotp
from aiohttp.http_exceptions import HttpProcessingError
from asyncpg import ConnectionDoesNotExistError
from bybit_p2p import P2P
from bybit_p2p._exceptions import FailedRequestError
from payeer_api import PayeerAPI
from pyro_client.client.file import FileClient
from tortoise import BaseDBAsyncClient
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q
from tortoise.functions import Count
from tortoise.signals import post_save
from tortoise.timezone import now
from urllib3.exceptions import ReadTimeoutError
from x_client import df_hdrs
from x_model import init_db
from x_model.func import ArrayAgg
from xync_bot import XyncBot
from xync_client.Bybit.InAgent import InAgentClient

from xync_client.Bybit.ex import ExClient
from xync_schema import models
from xync_schema.enums import OrderStatus, AgentStatus

from xync_schema.models import Actor, PmCur, Agent

from xync_client.Abc.Agent import BaseAgentClient
from xync_client.Abc.xtype import FlatDict, BaseOrderReq
from xync_client.Bybit.etype.ad import AdPostRequest, AdUpdateRequest, Ad, AdStatus, MyAd
from xync_client.Bybit.etype.cred import CredEpyd
from xync_client.Bybit.etype.order import (
    OrderRequest,
    PreOrderResp,
    OrderResp,
    CancelOrderReq,
    OrderItem,
    OrderFull,
    Message,
    Status,
    OrderSellRequest,
    TakeAdReq,
)
from xync_client.loader import TORM, NET_TOKEN, PAY_TOKEN


class NoMakerException(Exception):
    pass


class AgentClient(BaseAgentClient, InAgentClient):  # Bybit client
    headers = df_hdrs | {"accept-language": "ru-RU"}
    sec_hdrs: dict[str, str]
    # rewrite token for public methods
    api: P2P
    last_ad_id: list[str] = []
    update_ad_body = {
        "priceType": "1",
        "premium": "118",
        "quantity": "0.01",
        "minAmount": "500",
        "maxAmount": "3500000",
        "paymentPeriod": "30",
        "remark": "",
        "price": "398244.84",
        "paymentIds": ["3162931"],
        "tradingPreferenceSet": {
            "isKyc": "1",
            "hasCompleteRateDay30": "0",
            "completeRateDay30": "",
            "hasOrderFinishNumberDay30": "0",
            "orderFinishNumberDay30": "0",
            "isMobile": "0",
            "isEmail": "0",
            "hasUnPostAd": "0",
            "hasRegisterTime": "0",
            "registerTimeThreshold": "0",
            "hasNationalLimit": "0",
            "nationalLimit": "",
        },
        "actionType": "MODIFY",
        "securityRiskToken": "",
    }

    def __init__(self, agent: Agent, ex_client: ExClient, fbot: FileClient, bbot: XyncBot, **kwargs):
        super().__init__(agent, ex_client, fbot, bbot, **kwargs)
        self.sec_hdrs = {
            "accept-language": "ru,en;q=0.9",
            "gdfp": agent.auth["Risktoken"],
            "tx-id": agent.auth["Risktoken"],
        }
        self.api = P2P(testnet=False, api_key=agent.auth["key"], api_secret=agent.auth["sec"])
        self.hist: dict | None = None
        self.completed_orders: list[int] | None = None

    """ Private METHs"""

    async def fiat_new(self, payment_type: int, real_name: str, account_number: str) -> FlatDict | None:
        method1 = await self._post(
            "/x-api/fiat/otc/user/payment/new_create",
            {"paymentType": payment_type, "realName": real_name, "accountNo": account_number, "securityRiskToken": ""},
        )
        if srt := method1["result"]["securityRiskToken"]:
            await self._check_2fa(srt)
            method2 = await self._post(
                "/x-api/fiat/otc/user/payment/new_create",
                {
                    "paymentType": payment_type,
                    "realName": real_name,
                    "accountNo": account_number,
                    "securityRiskToken": srt,
                },
            )
            return method2
        else:
            return logging.exception(method1)

    def get_payment_method(self, fiat_id: int) -> CredEpyd:
        return self.creds()[fiat_id]

    def creds(self) -> dict[int, CredEpyd]:
        data = self.api.get_user_payment_types()
        if data["ret_code"] > 0:
            return data
        return {credex["id"]: CredEpyd.model_validate(credex) for credex in data["result"]}

    async def cred_epyd2db(self, ecdx: CredEpyd, pers_id: int = None, cur_id: int = None) -> models.CredEx | None:
        if ecdx.paymentType in (416,):  # what is 416??
            return None
        if not (
            pmex := await models.PmEx.get_or_none(exid=ecdx.paymentType, ex=self.ex_client.ex).prefetch_related(
                "pm__curs"
            )
        ):
            raise HTTPException(f"No PmEx {ecdx.paymentType} on ex#{self.ex_client.ex.name}", 404)
        if cred_old := await models.Cred.get_or_none(credexs__exid=ecdx.id, credexs__ex=self.actor.ex).prefetch_related(
            "pmcur"
        ):
            cur_id = cred_old.pmcur.cur_id
        elif not cur_id:  # is new Cred
            cur_id = (
                pmex.pm.df_cur_id
                or await self.guess_cur(ecdx, len(pmex.pm.curs) > 1 and pmex.pm.curs)
                or (pmex.pm.country_id and (await pmex.pm.country).cur_id)
                # or (ecdx.currencyBalance and await models.Cur.get_or_none(ticker=ecdx.currencyBalance[0]))  # это че еще за хуйня?
            )
        if not cur_id:
            raise Exception(f"Set default cur for {pmex.name}")
        if not (pmcur := await models.PmCur.get_or_none(cur_id=cur_id, pm_id=pmex.pm_id)):
            raise HTTPException(f"No PmCur with cur#{cur_id} and pm#{ecdx.paymentType}", 404)
        xtr = ecdx.branchName
        if ecdx.bankName:
            xtr += (" | " if xtr else "") + ecdx.bankName
        elif ecdx.payMessage:
            xtr += (" | " if xtr else "") + ecdx.payMessage
        elif ecdx.qrcode:
            xtr += (" | " if xtr else "") + ecdx.qrcode
        elif ecdx.paymentExt1:
            xtr += (" | " if xtr else "") + ecdx.paymentExt1
        cred_db, _ = await models.Cred.update_or_create(
            {
                "name": ecdx.realName,
                "extra": xtr,
            },
            pmcur=pmcur,
            person_id=pers_id or self.actor.person_id,
            detail=ecdx.accountNo or ecdx.payMessage,
        )
        credex_in = models.CredEx.validate({"exid": ecdx.id, "cred_id": cred_db.id, "ex_id": self.actor.ex.id})
        credex_db, _ = await models.CredEx.update_or_create(**credex_in.df_unq())
        return credex_db

    async def guess_cur(self, ecdx: CredEpyd, curs: list[models.Cur]):
        mbs = ecdx.bankName.split(", ")
        mbs += ecdx.branchName.split(" / ")
        mbs = {mb.lower(): mb for mb in mbs}
        if (
            pms := await models.Pm.filter(Q(join_type="OR", pmexs__name__in=mbs.values(), norm__in=mbs.keys()))
            .group_by("pmcurs__cur_id", "pmcurs__cur__ticker")
            .annotate(ccnt=Count("id"), names=ArrayAgg("norm"))
            .order_by("-ccnt", "pmcurs__cur__ticker")
            .values("pmcurs__cur_id", "names", "ccnt")
        ):
            return pms[0]["pmcurs__cur_id"]
        curs = {c.ticker: c.id for c in curs or await models.Cur.all()}
        for cur, cid in curs.items():
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.bankName):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.branchName):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.accountNo):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.payMessage):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.paymentExt1):
                return cid
        return None

    # 25: Список реквизитов моих платежных методов
    async def set_creds(self) -> list[models.CredEx]:
        credexs_epyd: dict[int, CredEpyd] = self.creds()
        credexs: list[models.CredEx] = [await self.cred_epyd2db(f) for f in credexs_epyd.values()]
        return credexs

    async def ott(self):
        t = await self._post("/x-api/user/private/ott")
        return t

    # 27
    async def fiat_upd(self, fiat_id: int, detail: str, name: str = None) -> dict:
        fiat = self.get_payment_method(fiat_id)
        fiat.realName = name
        fiat.accountNo = detail
        result = await self._post("/x-api/fiat/otc/user/payment/new_update", fiat.model_dump(exclude_none=True))
        srt = result["result"]["securityRiskToken"]
        await self._check_2fa(srt)
        fiat.securityRiskToken = srt
        result2 = await self._post("/fiat/otc/user/payment/new_update", fiat.model_dump(exclude_none=True))
        return result2

    # 28
    async def fiat_del(self, fiat_id: int) -> dict | str:
        data = {"id": fiat_id, "securityRiskToken": ""}
        method = await self._post("/x-api/fiat/otc/user/payment/new_delete", data)
        srt = method["result"]["securityRiskToken"]
        await self._check_2fa(srt)
        data["securityRiskToken"] = srt
        delete = await self._post("/x-api/fiat/otc/user/payment/new_delete", data)
        return delete

    async def switch_ads(self, new_status: AdStatus) -> dict:
        data = {"workStatus": new_status.name}  # todo: переделать на апи, там status 0 -> 1
        res = await self._post("/x-api/fiat/otc/maker/work-config/switch", data)
        return res

    async def ads(
        self,
        cnx: models.CoinEx,
        crx: models.CurEx,
        is_sell: bool,
        pmexs: list[models.PmEx],
        amount: int = None,
        lim: int = 50,
        vm_filter: bool = False,
        post_pmexs: set[models.PmEx] = None,
    ) -> list[Ad]:
        if post_pmexs:
            pm_exids = None
            lim = min(1000, lim * 25)
            post_pmexids = {p.exid for p in post_pmexs}
        else:
            pm_exids = [px.exid for px in pmexs]
            post_pmexids = set()
        ads: list[Ad] = await self.ex_client.ads(cnx.exid, crx.exid, is_sell, pm_exids, amount, lim, vm_filter)
        if post_pmexs:
            ads = [
                ad
                for ad in ads
                if (set(ad.payments) & post_pmexids or [True for px in post_pmexs if px.pm.norm in ad.remark.lower()])
            ]
        return ads

    @staticmethod
    def get_rate(list_ads: list) -> float:
        ads = [ad for ad in list_ads if set(ad["payments"]) - {"5", "51"}]
        return float(ads[0]["price"])

    def my_ads(self, active: bool = True, page: int = 1) -> list[MyAd]:
        resp = self.api.get_ads_list(size="30", page=str(page), status=AdStatus.active if active else AdStatus.sold_out)
        ads = [MyAd.model_validate(ad) for ad in resp["result"]["items"]]
        if resp["result"]["count"] > 30 * page:
            ads.extend(self.my_ads(active, page + 1))
        return ads

    async def export_my_ads(self, active: bool = None) -> int:  # upserted)
        ads = self.my_ads(True)
        if not active:
            ads += self.my_ads(False)
        for ad in ads:
            ad_db = await self.ex_client.ad_load(ad, maker=self.actor)
            mad_db, _ = await models.MyAd.update_or_create(ad=ad_db)
            exids = [pt.id for pt in ad.paymentTerms]
            credexs = await models.CredEx.filter(ex_id=self.actor.ex_id, exid__in=exids)
            await mad_db.credexs.add(*credexs)
        return len(ads)

    def get_security_token_create(self):
        data = self._post("/x-api/fiat/otc/item/create", self.create_ad_body)
        if data["ret_code"] == 912120019:  # Current user can not to create add as maker
            raise NoMakerException(data)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    async def _check_2fa(self, risk_token) -> int:
        data = {"risk_token": risk_token}
        res = await self._post("/x-api/user/public/risk/components", data, hdrs=self.sec_hdrs)
        if res["ret_msg"] != "success":
            raise HTTPException("get")
        cres = sorted(res["result"]["component_list"], key=lambda c: c["component_id"], reverse=True)
        vdata = {
            "risk_token": risk_token,
            "component_list": {c["component_id"]: await self.__get_2fa(c["component_id"], risk_token) for c in cres},
        }
        res = await self._post("/x-api/user/public/risk/verify", vdata, hdrs=self.sec_hdrs)
        if er_code := res["ret_code"] or res["result"]["ret_code"]:  # если код не 0, значит ошибка
            logging.error("Wrong 2fa, wait 5 secs and retry..")
            await sleep(5)
            return await self._check_2fa(risk_token)
        return er_code

    async def __get_2fa(
        self, typ: Literal["google2fa", "email_verify", "payment_password_verify", "phone_verify"], rt: str = None
    ):
        res = {"ret_msg": "success"}
        if typ != "google2fa":
            data = {"risk_token": rt, "component_id": typ}
            res = await self._post("/x-api/user/public/risk/send/code", data, hdrs=self.sec_hdrs)
        if res["ret_msg"] == "success":
            if typ == "google2fa":
                bybit_secret = self.agent.auth["2fa"]
                totp = pyotp.TOTP(bybit_secret)
                return totp.now()
            elif typ == "email_verify":
                return self.gmail.bybit_code()
            elif typ == "payment_password_verify":
                hp = sha256(self.agent.auth["pass"].encode()).hexdigest()
                return hp
        elif cool_down := int(res["result"]["cool_down"]):
            await sleep(cool_down)
            return self.__get_2fa(typ, rt)
        raise Exception("2fa fail")

    def _post_ad(self, risk_token: str):
        self.create_ad_body.update({"securityRiskToken": risk_token})
        data = self._post("/x-api/fiat/otc/item/create", self.create_ad_body)
        return data

    # создание объявлений
    def post_create_ad(self, token: str):
        result__check_2fa = self._check_2fa(token)
        assert result__check_2fa["ret_msg"] == "success", "2FA code wrong"

        result_add_ad = self._post_ad(token)
        if result_add_ad["ret_msg"] != "SUCCESS":
            print("Wrong 2fa on Ad creating, wait 9 secs and retry..")
            sleep(9)
            return self._post_create_ad(token)
        self.last_ad_id.append(result_add_ad["result"]["itemId"])

    def ad_new(self, ad: AdPostRequest):
        data = self.api.post_new_ad(**ad.model_dump())
        return data["result"]["itemId"] if data["ret_code"] == 0 else data

    def ad_upd(self, upd: AdUpdateRequest):
        params = upd.model_dump()
        data = self.api.update_ad(**params)
        return data["result"] if data["ret_code"] == 0 else data

    def get_security_token_update(self) -> str:
        self.update_ad_body["id"] = self.last_ad_id
        data = self._post("/x-api/fiat/otc/item/update", self.update_ad_body)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    def post_update_ad(self, token):
        result__check_2fa = self._check_2fa(token)
        assert result__check_2fa["ret_msg"] == "success", "2FA code wrong"

        result_update_ad = self.update_ad(token)
        if result_update_ad["ret_msg"] != "SUCCESS":
            print("Wrong 2fa on Ad updating, wait 10 secs and retry..")
            sleep(10)
            return self._post_update_ad(token)
        # assert result_update_ad['ret_msg'] == 'SUCCESS', "Ad isn't updated"

    def update_ad(self, risk_token: str):
        self.update_ad_body.update({"securityRiskToken": risk_token})
        data = self._post("/x-api/fiat/otc/item/update", self.update_ad_body)
        return data

    def ad_del(self, ad_id: int):
        data = self.api.remove_ad(itemId=ad_id)
        return data

    async def __preorder_request(self, ad_id: int) -> PreOrderResp:
        res = await self._post("/x-api/fiat/otc/item/simple", json={"item_id": str(ad_id)})
        if res["ret_code"] == 0:
            res = res["result"]
        return PreOrderResp.model_validate(res)

    async def _order_request(self, bor: BaseOrderReq) -> OrderResp:
        por: PreOrderResp = await self.__preorder_request(bor.ad_id)
        req = OrderRequest(
            itemId=por.id,
            tokenId=bor.coin_exid,
            currencyId=bor.cur_exid,
            side="1" if bor.is_sell else "0",
            amount=f"{bor.fiat_amount:.2f}".rstrip("0").rstrip("."),
            curPrice=por.curPrice,
            quantity=str(round(bor.fiat_amount / float(por.price), bor.coin_scale)),
            flag="amount",
            # online="0"
        )
        if bor.is_sell:
            credex = await models.CredEx.get(
                cred__person_id=self.actor.person_id,
                cred__pmcur__pm__pmexs__exid=[pp for pp in por.payments if pp == bor.pmex_exid][0],  # bor.pmex_exid
                cred__pmcur__pm__pmexs__ex_id=self.ex_client.ex.id,
                cred__pmcur__cur__ticker=bor.cur_exid,
            )
            req = OrderSellRequest(**req.model_dump(), paymentType=bor.pmex_exid, paymentId=str(credex.exid))
        # вот непосредственно сам запрос на ордер
        return await self.__order_create(req, bor)

    async def __order_create(self, req: OrderRequest | OrderSellRequest, bor: BaseOrderReq) -> OrderResp:
        hdrs = {"Risktoken": self.sec_hdrs["gdfp"]}
        res: dict = await self._post("/x-api/fiat/otc/order/create", json=req.model_dump(), hdrs=hdrs)
        if res["ret_code"] == 0:
            resp = OrderResp.model_validate(res["result"])
        elif res["ret_code"] == 10001:
            logging.error(req.model_dump(), "POST", self.session._base_url)
            raise HTTPException()
        elif res["ret_code"] == 912120030 or res["ret_msg"] == "The price has changed, please try again later.":
            resp = await self._order_request(bor)
        else:
            logging.exception(res)
        if not resp.orderId and resp.needSecurityRisk:
            if rc := await self._check_2fa(resp.securityRiskToken):
                await self.bbot.send(self.actor.person.user.username_id, f"Bybit 2fa: {rc}")
                raise Exception(f"Bybit 2fa: {rc}")
            # еще раз уже с токеном
            req.securityRiskToken = resp.securityRiskToken
            resp = await self.__order_create(req, bor)
        return resp

    async def cancel_order(self, order_id: str) -> bool:
        cr = CancelOrderReq(orderId=order_id)
        res = await self._post("/x-api/fiat/otc/order/cancel", cr.model_dump())
        return res["ret_code"] == 0

    async def get_order_info(self, order_id: str) -> OrderFull:
        data = await self._post("/x-api/fiat/otc/order/info", json={"orderId": order_id})
        return OrderFull.model_validate(data["result"])

    def get_chat_msg(self, order_id):
        data = self._post("/x-api/fiat/otc/order/message/listpage", json={"orderId": order_id, "size": 100})
        msgs = [
            {"text": msg["message"], "type": msg["contentType"], "role": msg["roleType"], "user_id": msg["userId"]}
            for msg in data["result"]["result"]
            if msg["roleType"] not in ("sys", "alarm")
        ]
        return msgs

    def block_user(self, user_id: str):
        return self._post("/x-api/fiat/p2p/user/add_block_user", {"blockedUserId": user_id})

    def unblock_user(self, user_id: str):
        return self._post("/x-api/fiat/p2p/user/delete_block_user", {"blockedUserId": user_id})

    def user_review_post(self, order_id: str):
        return self._post(
            "/x-api/fiat/otc/order/appraise/modify",
            {
                "orderId": order_id,
                "anonymous": "0",
                "appraiseType": "1",  # тип оценки 1 - хорошо, 0 - плохо. При 0 - обязательно указывать appraiseContent
                "appraiseContent": "",
                "operateType": "ADD",  # при повторном отправлять не 'ADD' -> а 'EDIT'
            },
        )

    def my_reviews(self):
        return self._post(
            "/x-api/fiat/otc/order/appraiseList",
            {"makerUserId": self.actor.exid, "page": "1", "size": "10", "appraiseType": "1"},  # "0" - bad
        )

    async def get_orders_active(
        self, side: int = None, status: int = None, begin_time: int = None, end_time: int = None, token_id: str = None
    ):
        return await self._post(
            "/x-api/fiat/otc/order/pending/simplifyList",
            {
                "status": status,
                "tokenId": token_id,
                "beginTime": begin_time,
                "endTime": end_time,
                "side": side,  # 1 - продажа, 0 - покупка
                "page": 1,
                "size": 10,
            },
        )

    def get_orders_done(self, begin_time: int, end_time: int, status: int, side: int, token_id: str):
        return self._post(
            "/x-api/fiat/otc/order/simplifyList",
            {
                "status": status,  # 50 - завершено
                "tokenId": token_id,
                "beginTime": begin_time,
                "endTime": end_time,
                "side": side,  # 1 - продажа, 0 - покупка
                "page": 1,
                "size": 10,
            },
        )

    async def create_order(self, order: OrderFull) -> models.Order:
        # ad = Ad(**self.api.get_ad_details(itemId=order.itemId)["result"])
        await sleep(1)
        curex = await models.CurEx.get_or_none(ex=self.ex_client.ex, exid=order.currencyId).prefetch_related("cur")
        cur_scale = (curex.scale if curex.scale is not None else curex.cur.scale) if curex else 2
        coinex = await models.CoinEx.get(ex=self.ex_client.ex, exid=order.tokenId).prefetch_related("coin")
        coin_scale = coinex.scale if coinex.scale is not None else coinex.cur.scale
        maker_name = order.sellerRealName, order.buyerRealName
        im_maker = int(order.makerUserId == order.userId)
        taker_id = (order.userId, order.targetUserId)[im_maker]
        taker_person = await self.ex_client.person_name_update(maker_name[::-1][order.side], taker_id)
        seller_person = (
            self.actor.person
            if order.side
            else await self.ex_client.person_name_update(order.sellerRealName, int(order.targetUserId))
        )
        taker_nick = (self.actor.name, order.targetNickName)[im_maker]  # todo: check
        # ad_db, cond_isnew = await self.ex_client.cond_load(ad, force=True, rname=maker_name[order.side])
        ad_db = await models.Ad.get(exid=order.itemId)
        if not ad_db:
            ...
        ecredex: CredEpyd = order.confirmedPayTerm

        if ecredex.paymentType == 0 and im_maker and order.side:
            ecredex = order.paymentTermList[0]
        if ecredex.paymentType:
            if ecredex.paymentType == 51:
                ecredex.accountNo = ecredex.accountNo.replace("p", "P").replace("р", "P").replace("Р", "P")
                # if not re.match(r"^([Pp])\d{7,10}$", ecredex.accountNo):
                #     msgs = self.api.get_chat_messages(orderId=order.id, size=100)["result"]["result"]
                #     msgs = [m["message"] for m in msgs if m["roleType"] == "user" and m["userId"] == order.targetUserId]
                #     msgs = [g.group() for m in msgs if (g := re.match(r"([PpРр])\d{7,10}\b", m))]
                #     crd = await models.Cred.get_or_none(
                #         detail=ecredex.accountNo, credexs__exid=ecredex.id, credexs__ex=self.ex_client.ex
                #     )
                #     if not msgs and re.match(r"^\d{7,10}$", ecredex.accountNo):
                #         ecredex.accountNo = "P" + ecredex.accountNo
                #     elif msgs:
                #         ecredex.accountNo = msgs[-1]
                #     else:
                #         ...
                #     if crd:
                #         crd.detail = ecredex.accountNo
                #         await crd.save(update_fields=["detail"])
            if not (credex := await models.CredEx.get_or_none(exid=ecredex.id, ex=self.ex_client.ex)):
                # cur_id = await Cur.get(ticker=ad.currencyId).values_list('id', flat=True)
                # await self.cred_epyd2db(ecredex, ad_db.maker.person_id, cur_id)
                if (
                    await PmCur.filter(
                        pm__pmexs__ex=self.ex_client.ex,
                        pm__pmexs__exid=ecredex.paymentType,
                        cur__ticker=order.currencyId,
                    ).count()
                    != 1
                ):
                    ...
                if not (
                    pmcur := await PmCur.get_or_none(
                        pm__pmexs__ex=self.ex_client.ex,
                        pm__pmexs__exid=ecredex.paymentType,
                        cur__ticker=order.currencyId,
                    )
                ):
                    ...
                if not (
                    crd := await models.Cred.get_or_none(pmcur=pmcur, person=seller_person, detail=ecredex.accountNo)
                ):
                    extr = ", ".join(
                        x
                        for xtr in [
                            ecredex.bankName,
                            ecredex.branchName,
                            ecredex.qrcode,
                            ecredex.payMessage,
                            ecredex.paymentExt1,
                        ]
                        if (x := xtr.strip())
                    )
                    crd = await models.Cred.create(
                        detail=ecredex.accountNo,
                        pmcur=pmcur,
                        person=seller_person,
                        name=ecredex.realName,
                        extra=extr,
                    )
                credex = await models.CredEx.create(exid=ecredex.id, ex=self.ex_client.ex, cred=crd)
        try:
            taker, _ = await Actor.get_or_create(
                {"name": taker_nick, "person": taker_person}, ex=self.ex_client.ex, exid=taker_id
            )
        except IntegrityError as e:
            logging.error(e)
        odb, _ = await models.Order.update_or_create(
            {
                "amount": float(order.amount) * 10**cur_scale,
                "quantity": float(order.quantity) * 10**coin_scale,
                "status": OrderStatus[Status(order.status).name],
                "created_at": ms2utc(order.createDate),
                "payed_at": order.transferDate != "0" and ms2utc(order.transferDate) or None,
                "confirmed_at": Status(order.status) == Status.completed and ms2utc(order.transferDate) or None,
                "appealed_at": order.status == 30 and ms2utc(order.transferDate) or None,
                "cred_id": ecredex.paymentType and credex.cred_id or None,
                "taker": taker,
                "ad": ad_db,
            },
            exid=order.id,
        )
        if order.status == Status.completed and ecredex.paymentType == 51:
            await odb.fetch_related("cred", "transfer")
            if odb.cred.detail != ecredex.accountNo:
                ...
            frm = (odb.created_at + timedelta(minutes=180 - 1)).isoformat(sep=" ").split("+")[0]
            to = ((odb.payed_at or odb.created_at) + timedelta(minutes=180 + 30)).isoformat(sep=" ").split("+")[0]
            tsa = [
                t
                for tid, t in (self.hist.items() if self.hist else [])
                if (ecredex.accountNo == t["to"] and t["from"] != "@merchant" and frm < t["date"] < to)
            ]
            buyer_person = (
                self.actor.person
                if not order.side
                else await self.ex_client.person_name_update(order.buyerRealName, int(order.targetUserId))
            )
            ts = [t for t in tsa if floor(fa := float(order.amount)) <= float(t["creditedAmount"]) <= round(fa)]
            if len(ts) != 1:
                if len(tsa) > 1:
                    summ = sum(float(t["creditedAmount"]) for t in tsa)
                    if floor(fa) <= summ <= round(fa):
                        for tr in tsa:
                            am = int(float(tr["creditedAmount"]) * 100)
                            await models.Transfer.create(
                                pmid=tr["id"], order=odb, amount=am, sender_acc=tr["from"], created_at=tr["date"]
                            )
            else:
                bcred, _ = await models.Cred.get_or_create(
                    {"detail": ts[0]["from"]}, person=buyer_person, pmcur_id=odb.cred.pmcur_id
                )
                am = int(float(ts[0]["creditedAmount"]) * 100)
                try:
                    await models.Transfer.create(
                        pmid=ts[0]["id"], order=odb, amount=am, sender_acc=ts[0]["from"], created_at=ts[0]["date"]
                    )
                except IntegrityError as e:
                    logging.error(e)
            ...

        await odb.fetch_related("ad")
        return odb

    async def get_api_orders(
        self,
        page: int = 1,
        begin_time: int = None,
        end_time: int = None,
        status: int = None,
        side: int = None,
        token_id: str = None,
    ):
        try:
            lst = self.api.get_orders(
                page=page,
                # status=status,  # 50 - завершено
                # tokenId=token_id,
                # beginTime=begin_time,
                # endTime=end_time,
                # side=side, # 1 - продажа, 0 - покупка
                size=30,
            )
        except FailedRequestError as e:
            if e.status_code == 10000:
                await sleep(9)
                await self.get_api_orders(page, begin_time, end_time)  # , status, side, token_id)
        ords = {int(o["id"]): OrderItem.model_validate(o) for o in lst["result"]["items"]}
        for oid, o in ords.items():
            if o.status != Status.completed.value or oid in self.completed_orders:
                continue
            fo = self.api.get_order_details(orderId=o.id)
            order = OrderFull.model_validate(fo["result"])
            order_db = await self.create_order(order)
            await sleep(1)
            dmsgs = self.api.get_chat_messages(orderId=oid, size=200)["result"]["result"][::-1]
            msgs = [Message.model_validate(m) for m in dmsgs if m["msgType"] in (1, 2, 7, 8)]
            if order_db.ad.auto_msg:
                msgs and msgs.pop(0)
            msgs_db = [
                models.Msg(
                    order=order_db,
                    read=m.isRead,
                    to_maker=m.userId != order.makerUserId,
                    **({"txt": m.message} if m.msgType == 1 else {"file": await self.ex_client.file_upsert(m.message)}),
                    sent_at=int(m.createDate[:-3]),
                )
                for m in msgs
            ]
            _ = await models.Msg.bulk_create(msgs_db, ignore_conflicts=True)
        logging.info(f"orders page#{page} imported ok!")
        if len(ords) == 30:
            await self.get_api_orders(page + 1, begin_time, end_time, status, side, token_id)

    # async def order_stat(self, papi: PayeerAPI):
    #     for t in papi.history():
    #         os = self.api.get_orders(page=1, size=30)

    async def mad_upd(self, mad: Ad, attrs: dict, cxids: list[str]):
        if not [setattr(mad, k, v) for k, v in attrs.items() if getattr(mad, k) != v]:
            print(end="v" if mad.side else "^", flush=True)
            return await sleep(5)
        req = AdUpdateRequest.model_validate({**mad.model_dump(), "paymentIds": cxids})
        try:
            return self.ad_upd(req)
        except FailedRequestError as e:
            if ExcCode(e.status_code) == ExcCode.FixPriceLimit:
                if limits := re.search(
                    r"The fixed price set is lower than ([0-9]+\.?[0-9]{0,2}) or higher than ([0-9]+\.?[0-9]{0,2})",
                    e.message,
                ):
                    return await self.mad_upd(mad, {"price": limits.group(1 if mad.side else 2)}, cxids)
            elif ExcCode(e.status_code) == ExcCode.RareLimit:
                await sleep(180)
            else:
                raise e
        except (ReadTimeoutError, ConnectionDoesNotExistError):
            logging.warning("Connection failed. Restarting..")
        print("-" if mad.side else "+", end=req.price, flush=True)
        await sleep(60)

    def overprice_filter(self, ads: list[Ad], ceil: float, k: Literal[-1, 1]):
        # вырезаем ads с ценами выше потолка
        if ads and (ceil - float(ads[0].price)) * k > 0:
            if int(ads[0].userId) != self.actor.exid:
                ads.pop(0)
                self.overprice_filter(ads, ceil, k)

    def get_cad(self, ads: list[Ad], ceil: float, k: Literal[-1, 1], target_place: int, cur_plc: int) -> Ad:
        if not ads:
            return None
        # чью цену будем обгонять, предыдущей или слещующей объявы?
        # cad: Ad = ads[place] if cur_plc > place else ads[cur_plc]
        # переделал пока на жесткую установку целевого места, даже если текущее выше:
        if len(ads) <= target_place:
            logging.error(f"target place {target_place} not found in ads {len(ads)}-lenght list")
            target_place = len(ads) - 1
        cad: Ad = ads[target_place]
        # а цена обгоняемой объявы не выше нашего потолка?
        if (float(cad.price) - ceil) * k <= 0:
            # тогда берем следующую
            ads.pop(target_place)
            cad = self.get_cad(ads, ceil, k, target_place, cur_plc)
        # todo: добавить фильтр по лимитам min-max
        return cad

    # @staticmethod
    # def premium_up(mad: Ad, cad: Ad, k: Literal[-1, 1]):
    #     mpc, mpm, cpc, cpm = Decimal(mad.price), Decimal(mad.premium), Decimal(cad.price), Decimal(cad.premium)
    #     new_premium = cpm - k * step(mad, cad, 2)
    #     if Decimal(mad.premium) == new_premium:  # Если нужный % и так уже стоит
    #         raise ValueError("wrong premium", mad, cad)
    #     if round(cpc * new_premium / cpm, 2) == m
    #     mad.premium = new_premium.to_eng_string()

    async def start_race(self):
        races = await models.Race.filter(started=True, road__ad__maker_id=self.actor.id).prefetch_related(
            "road__ad__pair_side__pair__cur", "road__credexs__cred", "road__ad__pms__pmexs__pm"
        )
        tasks = [create_task(self.racing(race), name=f"Rc{race.id}") for race in races]
        return await gather(*tasks)

    async def racing(self, race: models.Race):
        coinex: models.CoinEx = await models.CoinEx.get(
            coin_id=race.road.ad.pair_side.pair.coin_id, ex=self.actor.ex
        ).prefetch_related("coin")
        curex: models.CurEx = await models.CurEx.get(
            cur_id=race.road.ad.pair_side.pair.cur_id, ex=self.actor.ex
        ).prefetch_related("cur")
        taker_side: bool = not race.road.ad.pair_side.is_sell
        creds = [c.cred for c in race.road.credexs]
        pmexs: list[models.PmEx] = [pmex for pm in race.road.ad.pms for pmex in pm.pmexs if pmex.ex_id == 4]
        post_pm_ids = {c.cred.ovr_pm_id for c in race.road.credexs if c.cred.ovr_pm_id}
        post_pmexs = set(await models.PmEx.filter(pm_id__in=post_pm_ids, ex=self.actor.ex).prefetch_related("pm"))

        k = (-1) ** int(taker_side)  # on_buy=1, on_sell=-1
        sleep_sec = 3  # 1 if set(pms) & {"volet"} and coinex.coin_id == 1 else 5
        _lstat, volume = None, 0

        while self.actor.person.user.status > 0:
            # обновляем все обновления по текущей гонке из бд
            await race.refresh_from_db()
            if not race.started:
                await sleep(5)
                continue
            # если гонка дольше Х минут не обновлялась, обновляем ее (и ее пары) потолок
            expiration = datetime.now(timezone.utc) - timedelta(minutes=15)
            amt = race.filter_amount * 10**-curex.cur.scale if race.filter_amount else None
            if race.updated_at < expiration:
                ceils, hp, vmf, zplace = await self.get_ceils(coinex, curex, pmexs, 0.003, False, 0, amt, post_pmexs)
                race.ceil = int(ceils[int(taker_side)] * 10**curex.scale)
                await race.save()
                # upd pair race
                if prace := await models.Race.annotate(pms_count=Count("road__ad__pms")).get_or_none(
                    road__ad__pair_side__pair_id=race.road.ad.pair_side.pair_id,
                    road__ad__pair_side__is_sell=taker_side,
                    road__ad__maker=self.actor,
                    updated_at__lt=expiration,
                    road__credexs__id__in=[c.id for c in race.road.credexs],
                    pms_count=len(pmexs),
                ):
                    prace.ceil = int(ceils[int(not taker_side)] * 10**curex.scale)
                    await prace.save()

            last_vol = volume
            if taker_side:  # гонка в стакане продажи - мы покупаем монету за ФИАТ
                fiat = max(await models.Fiat.filter(cred_id__in=[c.id for c in creds]), key=lambda x: x.amount)
                volume = (fiat.amount * 10**-curex.cur.scale) / (race.road.ad.price * 10**-curex.scale)
            else:  # гонка в стакане покупки - мы продаем МОНЕТУ за фиат
                asset = await models.Asset.get(addr__actor=self.actor, addr__coin_id=coinex.coin_id)
                volume = asset.free * 10**-coinex.scale
            volume = str(round(volume, coinex.scale))
            try:
                ads: list[Ad] = await self.ads(coinex, curex, taker_side, pmexs, amt, 50, race.vm_filter, post_pmexs)
            except Exception:
                await sleep(1)
                ads: list[Ad] = await self.ads(coinex, curex, taker_side, pmexs, amt, 50, race.vm_filter, post_pmexs)

            self.overprice_filter(ads, race.ceil * 10**-curex.scale, k)  # обрезаем сверху все ads дороже нашего потолка

            if not ads:
                print(coinex.exid, curex.exid, taker_side, "no ads!")
                await sleep(15)
                continue
            # определяем наше текущее место в уже обрезанном списке ads
            if not (cur_plc := [i for i, ad in enumerate(ads) if int(ad.userId) == self.actor.exid]):
                logging.warning(f"No racing in {pmexs[0].name} {'-' if taker_side else '+'}{coinex.exid}/{curex.exid}")
                await sleep(15)
                continue
            (cur_plc,) = cur_plc  # может упасть если в списке > 1 наш ad
            [(await self.ex_client.cond_load(ad, race.road.ad.pair_side, True))[0] for ad in ads[:cur_plc]]
            # rivals = [
            #     (await models.RaceStat.update_or_create({"place": plc, "price": ad.price, "premium": ad.premium}, ad=ad))[
            #         0
            #     ]
            #     for plc, ad in enumerate(rads)
            # ]
            mad: Ad = ads.pop(cur_plc)
            # if (
            #     not (lstat := lstat or await race.stats.order_by("-created_at").first())
            #     or lstat.place != cur_plc
            #     or lstat.price != float(mad.price)
            #     or set(rivals) != set(await lstat.rivals)
            # ):
            #     lstat = await models.RaceStat.create(race=race, place=cur_plc, price=mad.price, premium=mad.premium)
            #     await lstat.rivals.add(*rivals)
            if not ads:
                await sleep(60)
                continue
            if not (cad := self.get_cad(ads, race.ceil * 10**-curex.scale, k, race.target_place, cur_plc)):
                continue
            new_price = round(float(cad.price) - k * step(mad, cad, curex.scale), curex.scale)
            if (
                float(mad.price) == new_price and volume == last_vol
            ):  # Если место уже нужное или нужная цена и так уже стоит
                print(
                    f"{'v' if taker_side else '^'}{mad.price}",
                    end=f"[{race.ceil * 10**-curex.scale}+{cur_plc}] ",
                    flush=True,
                )
                await sleep(sleep_sec)
                continue
            if cad.priceType:  # Если цена конкурента плавающая, то повышаем себе не цену, а %
                new_premium = (float(mad.premium) or float(cad.premium)) - k * step(mad, cad, 2)
                # if float(mad.premium) == new_premium:  # Если нужный % и так уже стоит
                #     if mad.priceType and cur_plc != race.target_place:
                #         new_premium -= k * step(mad, cad, 2)
                #     elif volume == last_vol:
                #         print(end="v" if taker_side else "^", flush=True)
                #         await sleep(sleep_sec)
                #         continue
                mad.premium = str(round(new_premium, 2))
            mad.priceType = cad.priceType
            mad.quantity = volume
            mad.maxAmount = str(2_000_000 if curex.cur_id == 1 else 40_000)
            req = AdUpdateRequest.model_validate(
                {
                    **mad.model_dump(),
                    "price": str(round(new_price, curex.scale)),
                    "paymentIds": [str(cx.exid) for cx in race.road.credexs],
                }
            )
            try:
                print(
                    f"c{race.ceil * 10**-curex.scale}+{cur_plc} {coinex.coin.ticker}{'-' if taker_side else '+'}{req.price}{curex.cur.ticker}"
                    f"{[pm.norm for pm in race.road.ad.pms]}{f'({req.premium}%)' if req.premium != '0' else ''} "
                    f"t{race.target_place} ;",
                    flush=True,
                )
                _res = self.ad_upd(req)
            except FailedRequestError as e:
                if ExcCode(e.status_code) == ExcCode.FixPriceLimit:
                    if limits := re.search(
                        r"The fixed price set is lower than ([0-9]+\.?[0-9]{0,2}) or higher than ([0-9]+\.?[0-9]{0,2})",
                        e.message,
                    ):
                        req.price = limits.group(1 if taker_side else 2)
                        if req.price != mad.price:
                            _res = self.ad_upd(req)
                    else:
                        raise e
                elif ExcCode(e.status_code) == ExcCode.InsufficientBalance:
                    asset = await models.Asset.get(addr__actor=self.actor, addr__coin_id=coinex.coin_id)
                    req.quantity = str(round(asset.free * 10**-coinex.scale, coinex.scale))
                    _res = self.ad_upd(req)
                elif ExcCode(e.status_code) == ExcCode.RareLimit:
                    if not (
                        sads := [
                            ma
                            for ma in self.my_ads(False)
                            if (
                                ma.currencyId == curex.exid
                                and ma.tokenId == coinex.exid
                                and taker_side != ma.side
                                and set(ma.payments) == set([pe.exid for pe in pmexs])
                            )
                        ]
                    ):
                        logging.error(f"Need reserve Ad {'sell' if taker_side else 'buy'} {coinex.exid}/{curex.exid}")
                        await sleep(90)
                        continue
                    self.ad_del(ad_id=int(mad.id))
                    req.id = sads[0].id
                    req.actionType = "ACTIVE"
                    self.api.update_ad(**req.model_dump())
                    logging.warning(f"Ad#{mad.id} recreated")
                elif ExcCode(e.status_code) == ExcCode.Timestamp:
                    await sleep(3)
                else:
                    raise e
            except (ReadTimeoutError, ConnectionDoesNotExistError):
                logging.warning("Connection failed. Restarting..")
            await sleep(6)

    async def get_books(
        self,
        coinex: models.CoinEx,
        curex: models.CurEx,
        pmexs: list[models.PmEx],
        amount: int,
        post_pmexs: list[models.PmEx] = None,
    ) -> tuple[list[Ad], list[Ad]]:
        buy: list[Ad] = await self.ads(coinex, curex, False, pmexs, amount, 40, False, post_pmexs)
        sell: list[Ad] = await self.ads(coinex, curex, True, pmexs, amount, 30, False, post_pmexs)
        return buy, sell

    async def get_spread(
        self, bb: list[Ad], sb: list[Ad], perc: float, vmf: bool = None, place: int = 0, exact: bool = False
    ) -> tuple[tuple[float, float], float, bool, int]:
        if len(bb) <= place or len(sb) <= place:
            ...
        buy_price, sell_price = float(bb[place].price), float(sb[place].price)
        half_spread = (buy_price - sell_price) / (buy_price + sell_price)
        # if half_spread * 2 < perc:  # todo: aA???
        #     if not exact:
        #         if vmf is None:  # сначала фильтруем только VA
        #             return await self.get_spread(bb, sb, perc, True, place)
        #         # если даже по VA не хватает спреда - увеличиваем место
        #         return await self.get_spread(bb, sb, perc, vmf, place + 1)

        return (buy_price, sell_price), half_spread, vmf, place

    async def get_ceils(
        self,
        coinex: models.CoinEx,
        curex: models.CurEx,
        pmexs: list[models.PmEx],
        min_prof=0.02,
        vmf: bool = False,
        place: int = 0,
        amount: int = None,
        post_pmexs: set[models.PmEx] = None,
    ) -> tuple[tuple[float, float], float, bool, int]:  # todo: refact to Pairex
        bb, sb = await self.get_books(coinex, curex, pmexs, amount, post_pmexs)
        if vmf:
            # ориентируемся на цены объявлений только проверенных мерчантов
            bb = [b for b in bb if "VA" in b.authTag]
            sb = [s for s in sb if "VA" in s.authTag]
        perc = list(post_pmexs or pmexs)[0].pm.fee * 0.0001 + min_prof
        (bf, sf), hp, vmf, zplace = await self.get_spread(bb, sb, perc, vmf, place)
        mdl = (bf + sf) / 2
        bc, sc = mdl + mdl * (perc / 2), mdl - mdl * (perc / 2)
        return (bc, sc), hp, vmf, zplace

    async def take_ad(self, req: TakeAdReq):
        if req.price and req.is_sell and req.cur_:
            ...  # todo call the get_ad_details() only if lack of data
        # res = self.api.get_ad_details(itemId=req.ad_id)["result"]
        # ad: Ad = Ad.model_validate(res)
        # pmexs = await models.PmEx.filter(ex_id=self.actor.ex_id, pm_id=req.pm_id)
        # if len(pmexs) > 1:
        #     pmexs = [p for p in pmexs if p.exid in ad.payments]
        #
        # # todo: map pm->cred_pattern
        # pmexid = exids.pop() if (exids := set(ad.payments) & set(px.exid for px in pmexs)) else "40"
        pmexid = str(req.pm_id)
        coinex = await models.CoinEx.get(coin_id=req.coin_id, ex=self.ex_client.ex)
        curex = await models.CurEx.get(cur_id=req.cur_id, ex=self.ex_client.ex)

        # if ad.side: # продажа, я (тейкер) покупатель
        #     pmexs = await models.PmEx.filter(ex_id=self.actor.ex_id, pm_id=req.pm_id)
        #     if len(pmexs) > 1:
        #         pmexs = [p for p in pmexs if p.name.endswith(f" ({ad.currencyId})")]
        # else:
        #     pmexs = await models.CredEx.filter(
        #         ex_id=self.actor.ex_id, cred__person_id=self.actor.person_id,
        #         cred__pmcur__pm_id=req.pm_id, cred__pmcur__cur__ticker=ad.currencyId
        #    )
        # req.pm_id = pmexs[0].exid
        # req.quantity = round(req.amount / float(ad.price) - 0.00005, 4)  # todo: to get the scale from coinEx

        bor = BaseOrderReq(
            ad_id=str(req.ad_id),
            fiat_amount=req.amount,
            is_sell=req.is_sell,
            cur_exid=curex.exid,
            coin_exid=coinex.exid,
            coin_scale=coinex.scale,
            pmex_exid=pmexid,
        )
        resp: OrderResp = await self._order_request(bor)
        return resp

    async def watch_payeer(self, mcs: dict[int, "AgentClient"]):
        coinex: models.CoinEx = await models.CoinEx.get(coin_id=1, ex=self.actor.ex).prefetch_related("coin")
        curex: models.CurEx = await models.CurEx.get(cur_id=1, ex=self.actor.ex).prefetch_related("cur")
        post_pmexs = set(await models.PmEx.filter(pm_id=366, ex=self.actor.ex).prefetch_related("pm"))
        i = 0
        while True:
            try:
                ss = await self.ads(coinex, curex, True, None, None, 1000, False, post_pmexs)
                ss = [s for s in ss if float(s.price) > 90.42 or int(s.userId) in mcs.keys()]
                if ss:
                    ad: Ad = ss[0]
                    await self.bbot.send(
                        193017646,
                        f"price: {ad.price}\nnick: {ad.nickName}\nprice: {ad.price}"
                        f"\nqty: {ad.quantity} [{ad.minAmount}-{ad.maxAmount}]",
                    )
                    am = min(float(ad.maxAmount), max(1000 + i, float(ad.minAmount)))
                    req = TakeAdReq(
                        ad_id=ad.id,
                        amount=am,
                        pm_id=14,
                        is_sell=True,
                        coin_id=1,
                        cur_id=1,
                    )
                    ord_resp: OrderResp = await self.take_ad(req)
                    # order: OrderFull = OrderFull(**self.api.get_order_details(orderId=ord_resp.orderId)["result"])
                    order: OrderFull = await self.get_order_info(ord_resp.orderId)
                    odb = await self.create_order(order)
                    # t = await models.Transfer(order=odb, amount=odb.amount, updated_at=now())
                    # await t.fetch_related("order__cred__pmcur__cur")
                    # res = await self.pm_clients[366].check_in(t)
                    if int(ad.userId) in mcs:
                        mcs[int(ad.userId)].api.mark_as_paid(
                            orderId=str(odb.exid),
                            paymentType=ad.payments[0],  # pmex.exid
                            paymentId=order.paymentTermList[0].id,  # credex.exid
                        )
                    self.api.release_assets(orderId=order.id)
                ...

                bs = await self.ads(coinex, curex, False, None, None, 1000, False, post_pmexs)
                bs = [b for b in bs if float(b.price) < 89.56 or int(b.userId) in mcs.keys()]
                if bs:
                    ad: Ad = bs[0]
                    await self.bbot.send(
                        193017646,
                        f"price: {ad.price}\nnick: {ad.nickName}\nprice: {ad.price}"
                        f"\nqty: {ad.quantity} [{ad.minAmount}-{ad.maxAmount}]",
                    )
                    am = min(float(ad.maxAmount), max(600 + i, float(ad.minAmount)))
                    req = TakeAdReq(
                        ad_id=ad.id,
                        amount=am,
                        pm_id=14,
                        is_sell=False,
                        coin_id=1,
                        cur_id=1,
                    )
                    ord_resp: OrderResp = await self.take_ad(req)
                    # order: OrderFull = OrderFull(**self.api.get_order_details(orderId=ord_resp.orderId)["result"])
                    order: OrderFull = await self.get_order_info(ord_resp.orderId)
                    odb = await self.create_order(order)
                    t = await models.Transfer(order=odb, amount=odb.amount, updated_at=now())
                    await t.fetch_related("order__cred__pmcur__cur")
                    # res = await self.pm_clients[366].send(t)
                    self.api.mark_as_paid(
                        orderId=str(odb.exid),
                        paymentType=ad.payments[0],  # pmex.exid
                        paymentId=order.paymentTermList[0].id,  # credex.exid
                    )
                    if int(ad.userId) in mcs:
                        mcs[int(ad.userId)].api.release_assets(orderId=order.id)
                    await sleep(1)
                ...
            except Exception as e:
                logging.exception(e)
                await sleep(90)
            except HttpProcessingError as e:
                logging.error(e)
            print(end=".", flush=True)
            i += 1
            await sleep(5)

    async def boost_acc(self):
        await sleep(45)
        for i in range(10):
            am = 500 + i
            req = TakeAdReq(ad_id="1856989782009487360", amount=am, pm_id=366)
            ord_resp: OrderResp = await self.take_ad(req)
            order: OrderFull = OrderFull(**self.api.get_order_details(orderId=ord_resp.orderId)["result"])
            odb = await self.create_order(order)
            t = await models.Transfer(order=odb, amount=odb.amount, updated_at=now())
            await t.fetch_related("order__cred__pmcur__cur")
            await self.pm_clients[366].send(t)
        ...


def ms2utc(msk_ts_str: str):
    return datetime.fromtimestamp(int(msk_ts_str) / 1000, timezone(timedelta(hours=3), name="MSK"))


def detailed_diff(str1, str2):
    matcher = SequenceMatcher(None, str1, str2)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result.append(str1[i1:i2])
        elif tag == "delete":
            result.append(f"[-{str1[i1:i2]}]")
        elif tag == "insert":
            result.append(f"[+{str2[j1:j2]}]")
        elif tag == "replace":
            result.append(f"[{str1[i1:i2]}→{str2[j1:j2]}]")

    return "".join(result)


def step_is_need(mad, cad) -> bool:
    # todo: пока не решен непонятный кейс, почему то конкурент по всем параметрам слабже, но в списке ранжируется выше.
    #  текущая версия: recentExecuteRate округляется до целого, но на бэке байбита его дробная часть больше
    return (
        bool(set(cad.authTag) & {"VA2", "BA"})
        or cad.recentExecuteRate > mad.recentExecuteRate
        or (
            cad.recentExecuteRate
            == mad.recentExecuteRate  # and cad.finishNum > mad.finishNum # пока прибавляем для равных
        )
    )


def step(mad, cad, scale: int = 2) -> float:
    return float(int(step_is_need(mad, cad)) * 10**-scale).__round__(scale)


class ExcCode(IntEnum):
    FixPriceLimit = 912120022
    RareLimit = 912120050
    InsufficientBalance = 912120024
    Timestamp = 10002
    IP = 10010
    Quantity = 912300019
    PayMethod = 912300013
    Unknown = 912300014


@post_save(models.Race)
async def race_upserted(
    _cls: type[models.Race], race: models.Race, created: bool, _db: BaseDBAsyncClient, _updated: list[str]
):
    logging.warning(f"Race {race.id} is now upserted")
    asyncio.all_tasks()
    if created:
        ...
    else:  # параметры гонки изменены
        ...


async def main():
    logging.basicConfig(level=logging.INFO)
    cn = await init_db(TORM)

    agent = (
        await models.Agent.filter(actor__ex_id=4, auth__isnull=False, status__gt=AgentStatus.off, id=8)
        .prefetch_related(
            "actor__ex",
            "actor__person__user__gmail",
            "actor__my_ads__my_ad__race",
            "actor__my_ads__pair_side__pair__cur",
            "actor__my_ads__pms",
        )
        .first()
    )
    filebot = FileClient(NET_TOKEN)
    # await filebot.start()
    # b.add_handler(MessageHandler(cond_start_handler, command("cond")))
    ex = await models.Ex.get(name="Bybit")
    ecl: ExClient = ex.client(filebot)
    abot = XyncBot(PAY_TOKEN, cn)
    cl: AgentClient = agent.client(ecl, filebot, abot)

    # req = TakeAdReq(ad_id=1955696985964089344, amount=504, pm_id=128)
    # await cl.take_ad(req)

    # await cl.actual_cond()
    # cl.get_api_orders(),  # 10, 1738357200000, 1742504399999

    # await cl.ex_client.set_pairs()
    # await cl.ex_client.set_pms()

    # await cl.set_creds()
    # await cl.export_my_ads()

    ms = await models.Agent.filter(
        actor__ex_id=4, auth__isnull=False, status__gt=AgentStatus.off, actor__person__user__id__in=[2]
    ).prefetch_related(
        "actor__ex",
        "actor__person__user__gmail",
        "actor__my_ads__my_ad__race",
        "actor__my_ads__pair_side__pair__cur",
        "actor__my_ads__pms",
    )
    mcs = {m.actor.exid: m.client(ecl, filebot, abot) for m in ms}

    await gather(
        create_task(cl.start(True)),
        create_task(cl.watch_payeer(mcs)),
    )
    # ensure_future(cl.start(True))
    # await cl.boost_acc()

    # создание гонок по мои активным объявам:
    # for ma in cl.my_ads():
    #     my_ad = await models.MyAd.get(ad__exid=ma.id).prefetch_related('ad__pms', 'ad__pair_side__pair')
    #     race, _ = await models.Race.update_or_create(
    #         {"started": True, "vm_filter": True, "target_place": 5},
    #         road=my_ad
    #     )

    # for name in names:
    #     s, _ = await models.Synonym.update_or_create(typ=SynonymType.name, txt=name)
    #     await s.curs.add(rub.cur)

    pauth = (await models.PmAgent[1]).auth
    papi = PayeerAPI(pauth["email"], pauth["api_id"], pauth["api_sec"])
    hist: dict = papi.history(count=1000)
    hist |= papi.history(count=1000, append=list(hist.keys())[-1])
    hist |= papi.history(count=1000, append=list(hist.keys())[-1])
    cl.hist = hist

    # cl.completed_orders = await models.Order.filter(status=OrderStatus.completed, transfer__isnull=False).values_list(
    #     "exid", flat=True
    # )
    # await cl.get_api_orders()  # 43, 1741294800000, 1749157199999)

    # await cl.cancel_order(res.orderId)
    await filebot.stop()
    await cl.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down")
