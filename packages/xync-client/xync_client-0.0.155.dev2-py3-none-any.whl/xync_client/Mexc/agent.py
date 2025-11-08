from asyncio import run
from hashlib import md5
from uuid import uuid4

from pyro_client.client.file import FileClient
from xync_bot import XyncBot
from xync_client.Bybit.etype.order import TakeAdReq

from xync_client.loader import PAY_TOKEN, NET_TOKEN
from xync_schema import models
from xync_schema.enums import UserStatus

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


async def main():
    from x_model import init_db
    from xync_client.loader import TORM

    cn = await init_db(TORM, True)

    agent = (
        await models.Agent.filter(
            actor__ex_id=12,
            active=True,
            auth__isnull=False,
            actor__person__user__status=UserStatus.ACTIVE,
            actor__person__user__pm_agents__isnull=False,
        )
        .prefetch_related("actor__ex", "actor__person__user__gmail")
        .first()
    )

    bbot = XyncBot(PAY_TOKEN, cn)
    fbot = FileClient(NET_TOKEN)

    cl = agent.client(fbot, bbot)
    req = TakeAdReq(ad_id="a1574088909645125632", amount=500, pm_id=366, cur_="RUB", price=85.8, is_sell=True)
    res = await cl.take_ad(req)
    print(res)


if __name__ == "__main__":
    run(main())
