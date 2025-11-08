from abc import abstractmethod
from asyncio.tasks import gather
from collections import defaultdict

from playwright.async_api import async_playwright
from pydantic import BaseModel
from pyro_client.client.file import FileClient
from x_client import df_hdrs
from x_client.aiohttp import Client as HttpClient
from xync_bot import XyncBot
from xync_client.Abc.PmAgent import PmAgentClient
from xync_schema.enums import UserStatus

from xync_client.Abc.InAgent import BaseInAgentClient

from xync_client.Bybit.etype.order import TakeAdReq
from xync_schema import models
from xync_schema.models import OrderStatus, Coin, Cur, Ad, AdStatus, Actor, Agent
from xync_schema.xtype import BaseAd

from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.xtype import CredExOut, BaseOrderReq, BaseAdUpdate, AdUpd
from xync_client.Gmail import GmClient


class BaseAgentClient(HttpClient, BaseInAgentClient):
    actor: Actor
    agent: Agent
    bbot: XyncBot
    fbot: FileClient
    ex_client: BaseExClient
    pm_clients: dict[int, PmAgentClient]  # {pm_id: PmAgentClient}

    def __init__(
        self,
        agent: Agent,
        ex_client: BaseExClient,
        fbot: FileClient,
        bbot: XyncBot,
        headers: dict[str, str] = df_hdrs,
        cookies: dict[str, str] = None,
    ):
        self.bbot = bbot
        self.fbot = fbot
        self.agent: Agent = agent
        self.actor: Actor = agent.actor
        self.gmail = agent.actor.person.user.gmail and GmClient(agent.actor.person.user)
        self.ex_client: BaseExClient = ex_client
        self.pm_clients: dict[int, PmAgentClient] = defaultdict()
        super().__init__(self.actor.ex.host_p2p, headers, cookies)

    async def start(self, debug: bool = False):
        tasks = []
        if not self.is_started:
            if self.agent.status & 1:  # race
                tasks.append(self.start_race())

            if self.agent.status & 2:  # in agent
                if not self.pm_clients:
                    pm_agents = await models.PmAgent.filter(
                        active=True,
                        auth__isnull=False,
                        user__status=UserStatus.ACTIVE,
                    ).prefetch_related("pm", "user__gmail")
                    # payeer_cl = Client(actor.person.user.username_id)
                    pw = await async_playwright().start()
                    browser = await pw.chromium.launch(
                        channel="chrome-beta" if debug else "chromium-headless-shell", headless=not debug
                    )
                    self.pm_clients = {pma.pm_id: pma.client(browser, self.bbot) for pma in pm_agents}
                    [tasks.append(pmcl.start()) for pmcl in self.pm_clients.values()]
                # tasks.append(self.start_listen())

            if self.agent.status & 4:  # for further
                ...
            self.is_started = True
        return await gather(*tasks)

    # 0: Получшение ордеров в статусе status, по монете coin, в валюте coin, в направлении is_sell: bool
    @abstractmethod
    async def get_orders(
        self, status: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> list: ...

    # 1: [T] Запрос на старт сделки
    @abstractmethod
    async def order_request(self, order_req: BaseOrderReq) -> dict: ...

    # async def start_order(self, order: Order) -> OrderOutClient:
    #     return OrderOutClient(self, order)

    # 1N: [M] - Запрос мейкеру на сделку
    @abstractmethod
    async def order_request_ask(self) -> dict: ...  # , ad: Ad, amount: float, pm: Pm, taker: Agent

    # 2N: [M] - Уведомление об отмене запроса на сделку
    @abstractmethod
    async def request_canceled_notify(self) -> int: ...  # id

    # # # Cred
    @property
    @abstractmethod
    def fiat_pyd(self) -> BaseModel.__class__: ...

    @abstractmethod
    def fiat_args2pyd(
        self, exid: int | str, cur: str, detail: str, name: str, fid: int, typ: str, extra=None
    ) -> fiat_pyd: ...

    # 25: Список реквизитов моих платежных методов
    @abstractmethod
    async def creds(self) -> list[CredExOut]: ...  # {credex.exid: {cred}}

    # Создание реквизита на бирже
    async def cred_new(self, cred: models.Cred) -> models.CredEx: ...

    # await models.Actor.get_or_create({"name": cred.exid}, ex=self.ex_client.ex, exid=self.agent.actor.exid)
    # cred_db: Cred = (await self.cred_pyd2db(cred, self.agent.user_id))[0]
    # if not (credex := models.CredEx.get_or_none(cred=cred_db, ex=self.agent.ex)):
    #     credex, _ = models.CredEx.update_or_create({}, cred=cred_db, ex=self.agent.ex)
    # return credex

    # 27: Редактирование реквизита моего платежного метода
    @abstractmethod
    async def cred_upd(self, cred: models.Cred, exid: int) -> models.CredEx: ...

    # 28: Удаление реквизита моего платежного метода
    @abstractmethod
    async def cred_del(self, exid: int) -> int: ...

    # # # Ad
    # 29: Список моих объявлений
    @abstractmethod
    async def my_ads(self, status: AdStatus = None) -> list[BaseAd]: ...

    # 30: Создание объявления
    @abstractmethod
    async def ad_new(self, ad: BaseAd) -> Ad: ...

    async def ad_upd(self, ad_upd_req: AdUpd) -> Ad:
        pmex_exids = await models.PmEx.filter(ex_id=self.actor.ex_id, pm_id__in=ad_upd_req.pm_ids).values_list(
            "exid", flat=True
        )
        credexs = await models.CredEx.filter(
            ex_id=self.actor.ex_id,
            cred__pmcur__pm_id__in=ad_upd_req.pm_ids,
            cred__pmcur__cur_id=ad_upd_req.cur_id,
            cred__person_id=self.actor.person_id,
        ).prefetch_related("cred__pmcur")
        coinex = await models.CoinEx.get(coin_id=ad_upd_req.coin_id, ex=self.ex_client.ex)
        curex = await models.CurEx.get(cur_id=ad_upd_req.cur_id, ex=self.ex_client.ex)
        # override
        ad_upd_req.coin_id = coinex.exid
        ad_upd_req.cur_id = curex.exid
        ad_upd_req.pm_ids = pmex_exids
        ad_upd_req.credexs = credexs
        ad_upd_req.price = round(ad_upd_req.price, curex.scale)
        ad_upd_req.amount = round(ad_upd_req.amount, curex.scale)
        ad_upd_req.quantity = round(ad_upd_req.amount / ad_upd_req.price, coinex.scale)
        return await self._ad_upd(ad_upd_req)

    # 31: Редактирование объявления
    @abstractmethod
    async def _ad_upd(self, ad: BaseAdUpdate) -> Ad: ...

    # 32: Удаление
    @abstractmethod
    async def ad_del(self, ad_id: int) -> bool: ...

    # 33: Вкл/выкл объявления
    @abstractmethod
    async def ad_switch(self, offer_id: int, active: bool) -> bool: ...

    # 34: Вкл/выкл всех объявлений
    @abstractmethod
    async def ads_switch(self, active: bool) -> bool: ...

    # # # User
    # 35: Получить объект юзера по его ид
    @abstractmethod
    async def get_user(self, user_id) -> dict: ...

    # 36: Отправка сообщения юзеру с приложенным файлом
    @abstractmethod
    async def send_user_msg(self, msg: str, file=None) -> bool: ...

    # 37: (Раз)Блокировать юзера
    @abstractmethod
    async def block_user(self, is_blocked: bool = True) -> bool: ...

    # 38: Поставить отзыв юзеру
    @abstractmethod
    async def rate_user(self, positive: bool) -> bool: ...

    # 39: Балансы моих монет
    @abstractmethod
    async def my_assets(self) -> dict: ...

    @abstractmethod
    async def take_ad(self, req: TakeAdReq): ...

    # Сохранение объявления (с Pm/Cred-ами) в бд
    # async def ad_pydin2db(self, ad_pydin: AdSaleIn | AdBuyIn) -> Ad:
    #     ad_db = await self.ex_client.ad_pydin2db(ad_pydin)
    #     await ad_db.credexs.add(*getattr(ad_pydin, "credexs_", []))
    #     await ad_db.pmexs.add(*getattr(ad_pydin, "pmexs_", []))
    #     return ad_db

    # @staticmethod
    # async def cred_e2db(cred_in: BaseUpd, banks: list[str] = None) -> bool:
    #     cred_db, _ = await models.Cred.update_or_create(**cred_in.df_unq())
    #     credex_in = models.CredEx.validate({"exid": cred_in.id, "cred_id": cred_db.id})
    #     credex_db, _ = await models.CredEx.update_or_create(**credex_in.df_unq())
    #     if banks:  # only for SBP
    #         await cred_db.banks.add(*[await PmExBank.get(exid=b) for b in banks])
    #     return True
