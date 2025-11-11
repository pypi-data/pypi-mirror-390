from asyncio import run, sleep
from hashlib import md5
from uuid import uuid4

from pyro_client.client.file import FileClient
from xync_bot import XyncBot
from xync_client.Mexc.etype import ad

from xync_client.Abc.xtype import GetAds, AdUpd
from xync_client.Bybit.etype.order import TakeAdReq

from xync_client.loader import PAY_TOKEN, NET_TOKEN
from xync_schema import models
from xync_schema.enums import UserStatus, AgentStatus

from xync_client.Abc.Agent import BaseAgentClient


class AgentClient(BaseAgentClient):
    i: int = 0
    headers = {
        "accept-language": "ru,en;q=0.9",
        "language:": "ru-RU",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    async def _take_ad(self, req: TakeAdReq):
        self.i = 33 if self.i > 9998 else self.i + 2
        hdrs = self.headers | {"trochilus-trace-id": f"{uuid4()}-{self.i:04d}"}
        auth = {
            "p0": self.actor.agent.auth["p0"],
            "k0": self.actor.agent.auth["k0"],
            "chash": self.actor.agent.auth["chash"],
            "mtoken": self.actor.agent.auth["deviceId"],
            "mhash": md5(self.actor.agent.auth["deviceId"].encode()).hexdigest(),
        }
        data = {
            "scene": "TRADE_BUY",
            "quantity": req.quantity,
            "amount": req.amount,
            "orderId": req.ad_id,
            "authVersion": "v2",
            "deviceId": auth["mtoken"],
        }
        res = await self._post("/api/verify/second_auth/risk/scene", json=data, hdrs=hdrs)
        data = {
            "amount": req.amount,
            "authVersion": "v2",
            "orderId": req.ad_id,
            "price": req.price,
            "ts": int(1761155700.8372989 * 1000),
            "userConfirmPaymentId" if req.is_sell else "userConfirmPayMethodId": req.pm_id,
        }
        self.i = 33 if self.i > 9999 else self.i + 1
        hdrs = self.headers | {"trochilus-trace-id": f"{uuid4()}-{self.i:04d}"}
        res = await self._post("/api/order/deal?mhash=" + auth["mhash"], data=auth | data, hdrs=hdrs)
        return res["data"]

    async def _ad_upd(self, req: AdUpd):
        self.i = 33 if self.i > 9998 else self.i + 2
        data = {
            "adsType": 1,
            "allowSys": "true",
            "apiVersion": "1.0.0",
            "authVersion": "v2",
            "autoResponse": "",  # quote("P1132998804"),
            "blockTrade": "false",
            "coinId": req.coin_id,
            "countryCode": "RU",
            "currency": req.cur_id,
            "deviceId": self.agent.auth["deviceId"],
            "display": 1,
            "exchangeCount": 0,
            "expirationTime": 15,
            "fiatCount": 0,
            "fiatCountLess": 0,
            "id": req.id,
            "kycLevel": "PRIMARY",
            "maxPayLimit": 0,
            "minRegisterDate": 0,
            "minTradeLimit": 500,
            "payment": req.credexs[0].exid,
            "priceType": 0,
            "quantity": 1800,
            "requireMobile": "false",
            "securityOrderPaymentInfo": "",
            "tradeTerms": "",
            "tradeType": "SELL" if req.is_sell else "BUY",
            "maxTradeLimit": 150000,
            "price": req.price,
        }
        self.i = 33 if self.i > 9999 else self.i + 1
        hdrs = self.headers | {"trochilus-trace-id": f"{uuid4()}-{self.i:04d}"}
        res = await self._put("/api/merchant/order", form_data=data, hdrs=hdrs)
        return res["code"]


async def main():
    from x_model import init_db
    from xync_client.loader import TORM

    cn = await init_db(TORM, True)

    ex = await models.Ex[12]
    agent = (
        await models.Agent.filter(
            actor__ex=ex,
            status__gte=AgentStatus.race,
            auth__isnull=False,
            actor__person__user__status=UserStatus.ACTIVE,
            actor__person__user__pm_agents__isnull=False,
        )
        .prefetch_related("actor__ex", "actor__person__user__gmail")
        .first()
    )
    bbot = XyncBot(PAY_TOKEN, cn)
    fbot = FileClient(NET_TOKEN)
    ecl = ex.client(fbot)
    cl = agent.client(ecl, fbot, bbot)

    while True:
        bceil = 89.11
        sceil = 90.83
        breq = GetAds(coin_id=1, cur_id=1, is_sell=False, pm_ids=[366])
        sreq = GetAds(coin_id=1, cur_id=1, is_sell=True, pm_ids=[366])
        breq_upd = AdUpd(id="a1574183931501582340", price=87, **{**breq.model_dump(), "amount": 180001})
        sreq_upd = AdUpd(id="a1574121826274483200", price=93, **{**sreq.model_dump(), "amount": 180001})

        bads: list[ad.Ad] = await cl.ex_client.ads(breq)
        sads: list[ad.Ad] = await cl.ex_client.ads(sreq)
        bads = [a for a in bads if a.price < bceil]
        sads = [a for a in sads if a.price > sceil]

        if bads:
            if bads[0].merchant.nickName == cl.actor.name:
                if round(bads[0].price - bads[1].price, 2) > 0.01:
                    breq_upd.price = bads[1].price + 0.01
                    await cl.ad_upd(breq_upd)
                    print(end="!", flush=True)
            elif bads[0].price < bceil:
                breq_upd.price = bads[0].price + 0.01
                await cl.ad_upd(breq_upd)
                print(end="!", flush=True)

        if sads:
            if sads[0].merchant.nickName == cl.actor.name:
                if round(sads[1].price - sads[0].price, 2) > 0.01:
                    sreq_upd.price = sads[1].price - 0.01
                    await cl.ad_upd(sreq_upd)
                    print(end="!", flush=True)
            elif sads[0].price > sceil:
                sreq_upd.price = sads[0].price - 0.01
                await cl.ad_upd(sreq_upd)
                print(end="!", flush=True)

        print(end=".", flush=True)
        await sleep(5)

    req = TakeAdReq(ad_id="a1574088909645125632", amount=500, pm_id=366, cur_id=1, price=85.8, is_sell=True)
    res = await cl.take_ad(req)
    print(res)


if __name__ == "__main__":
    run(main())
