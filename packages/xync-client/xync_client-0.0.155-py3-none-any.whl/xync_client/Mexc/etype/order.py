"""
MEXC P2P OpenAPI v1.2 Async Client
"""

import hmac
import hashlib
import time
from typing import Optional, List, Literal
from decimal import Decimal

import aiohttp
from pydantic import BaseModel, Field


# ============ Enums ============


class Side(str):
    BUY = "BUY"
    SELL = "SELL"


class AdvStatus(str):
    CLOSE = "CLOSE"
    OPEN = "OPEN"
    DELETE = "DELETE"
    LOW_STOCK = "LOW_STOCK"


class OrderDealState(str):
    NOT_PAID = "NOT_PAID"
    PAID = "PAID"
    WAIT_PROCESS = "WAIT_PROCESS"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    CANCEL = "CANCEL"
    INVALID = "INVALID"
    REFUSE = "REFUSE"
    TIMEOUT = "TIMEOUT"


class NotifyType(str):
    SMS = "SMS"
    MAIL = "MAIL"
    GA = "GA"


# ============ Request Models ============


class CreateUpdateAdRequest(BaseModel):
    advNo: Optional[str] = None
    payTimeLimit: int
    initQuantity: Decimal
    supplyQuantity: Optional[Decimal] = None
    price: Decimal
    coinId: str
    countryCode: Optional[str] = None
    side: str
    advStatus: Optional[str] = None
    allowSys: Optional[bool] = None
    fiatUnit: str
    payMethod: str
    autoReplyMsg: Optional[str] = None
    tradeTerms: Optional[str] = None
    minSingleTransAmount: Decimal
    maxSingleTransAmount: Decimal
    kycLevel: Optional[str] = None
    requireMobile: Optional[bool] = None
    userAllTradeCountMin: int
    userAllTradeCountMax: int
    exchangeCount: Optional[int] = None
    maxPayLimit: Optional[int] = None
    buyerRegDaysLimit: Optional[int] = None
    creditAmount: Optional[Decimal] = None
    blockTrade: Optional[bool] = None
    deviceId: Optional[str] = None


class CreateOrderRequest(BaseModel):
    advNo: str
    amount: Optional[Decimal] = None
    tradableQuantity: Optional[Decimal] = None
    userConfirmPaymentId: int
    userConfirmPayMethodId: Optional[int] = None
    deviceId: Optional[str] = None


class ConfirmPaidRequest(BaseModel):
    advOrderNo: str
    payId: int


class ReleaseCoinRequest(BaseModel):
    advOrderNo: str
    notifyType: Optional[str] = None
    notifyCode: Optional[str] = None


class ServiceSwitchRequest(BaseModel):
    open: bool


# ============ Response Models ============


class BaseResponse(BaseModel):
    code: int
    msg: str


class PaymentInfo(BaseModel):
    id: int
    payMethod: int
    bankName: str
    account: str
    bankAddress: str
    payee: str
    extend: str


class MerchantInfo(BaseModel):
    nickName: str
    imId: str
    memberId: str
    registry: int
    vipLevel: int
    greenDiamond: bool
    emailAuthentication: bool
    smsAuthentication: bool
    identityVerification: bool
    lastOnlineTime: int
    badge: str
    merchantType: str


class MerchantStatistics(BaseModel):
    totalBuyCount: int
    totalSellCount: int
    doneLastMonthCount: int
    avgBuyHandleTime: int
    avgSellHandleTime: int
    lastMonthCompleteRate: str
    completeRate: str
    avgHandleTime: int


class Advertisement(BaseModel):
    advNo: str
    payTimeLimit: int
    quantity: int
    price: Decimal
    initAmount: Decimal
    frozenQuantity: Decimal
    availableQuantity: Decimal
    coinId: str
    coinName: str
    countryCode: str
    commissionRate: Decimal
    advStatus: str
    side: str
    createTime: int
    updateTime: int
    fiatUnit: str
    feeType: int
    autoReplyMsg: str
    tradeTerms: str
    payMethod: str
    paymentInfo: List[PaymentInfo]
    minSingleTransAmount: Decimal
    maxSingleTransAmount: Decimal
    kycLevel: int
    requireMobile: bool
    userAllTradeCountMax: int
    userAllTradeCountMin: int
    exchangeCount: int
    maxPayLimit: int
    buyerRegDaysLimit: int
    blockTrade: bool


class MarketAdvertisement(Advertisement):
    merchant: MerchantInfo
    merchantStatistics: MerchantStatistics
    orderPayCount: int
    tags: str


class PageInfo(BaseModel):
    total: int
    currPage: int
    pageSize: int
    totalPage: int


class UserInfo(BaseModel):
    nickName: str


class Order(BaseModel):
    advNo: str
    advOrderNo: str
    tradableQuantity: Decimal
    price: Decimal
    amount: Decimal
    coinName: str
    state: int
    payTimeLimit: int
    side: str
    fiatUnit: str
    createTime: int
    updateTime: int
    userInfo: UserInfo
    complained: bool
    blockUser: bool
    unreadCount: int
    complainId: Optional[str] = None


class OrderDetail(Order):
    paymentInfo: List[PaymentInfo]
    allowComplainTime: int
    confirmPaymentInfo: PaymentInfo
    userInfo: dict
    userFiatStatistics: dict
    spotCount: int


class CreateAdResponse(BaseResponse):
    data: str  # advNo


class AdListResponse(BaseResponse):
    data: List[Advertisement]
    page: PageInfo


class MarketAdListResponse(BaseResponse):
    data: List[MarketAdvertisement]
    page: PageInfo


class CreateOrderResponse(BaseResponse):
    data: str  # advOrderNo


class OrderListResponse(BaseResponse):
    data: List[Order]
    page: PageInfo


class OrderDetailResponse(BaseResponse):
    data: OrderDetail


class ListenKeyResponse(BaseResponse):
    listenKey: str


class ConversationResponse(BaseResponse):
    data: dict


class ChatMessage(BaseModel):
    id: int
    content: Optional[str] = None
    createTime: str
    fromNickName: str
    fromUserId: str
    type: int
    imageUrl: Optional[str] = None
    imageThumbUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    fileUrl: Optional[str] = None
    self_: bool = Field(alias="self")
    conversationId: int


class ChatMessagesResponse(BaseResponse):
    data: dict


class UploadFileResponse(BaseResponse):
    data: dict


# ============ Client ============


class MEXCP2PClient:
    """Асинхронный клиент для MEXC P2P API v1.2"""

    BASE_URL = "https://api.mexc.com"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _generate_signature(self, query_string: str) -> str:
        """Генерация HMAC SHA256 подписи"""
        return hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _get_timestamp(self) -> int:
        """Получение текущего timestamp в миллисекундах"""
        return int(time.time() * 1000)

    async def _request(
        self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[BaseModel] = None
    ) -> dict:
        """Базовый метод для HTTP запросов"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        timestamp = self._get_timestamp()

        # Формирование query string для подписи
        query_params = params.copy() if params else {}
        query_params["timestamp"] = timestamp

        query_string = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))
        signature = self._generate_signature(query_string)

        query_params["signature"] = signature

        headers = {"X-MEXC-APIKEY": self.api_key, "Content-Type": "application/json"}

        url = f"{self.BASE_URL}{endpoint}"

        json_data = data.model_dump(exclude_none=True) if data else None

        async with self.session.request(method, url, params=query_params, json=json_data, headers=headers) as response:
            return await response.json()

    # ============ Advertisement Methods ============

    async def create_or_update_ad(self, request: CreateUpdateAdRequest) -> CreateAdResponse:
        """Создание или обновление объявления"""
        result = await self._request("POST", "/api/v3/fiat/merchant/ads/save_or_update", data=request)
        return CreateAdResponse(**result)

    async def get_my_ads(
        self,
        coin_id: Optional[str] = None,
        adv_status: Optional[str] = None,
        merchant_id: Optional[str] = None,
        fiat_unit: Optional[str] = None,
        side: Optional[str] = None,
        kyc_level: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
    ) -> AdListResponse:
        """Получение списка моих объявлений с пагинацией"""
        params = {"page": page, "limit": limit}

        if coin_id:
            params["coinId"] = coin_id
        if adv_status:
            params["advStatus"] = adv_status
        if merchant_id:
            params["merchantId"] = merchant_id
        if fiat_unit:
            params["fiatUnit"] = fiat_unit
        if side:
            params["side"] = side
        if kyc_level:
            params["kycLevel"] = kyc_level
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        result = await self._request("GET", "/api/v3/fiat/merchant/ads/pagination", params=params)
        return AdListResponse(**result)

    async def get_market_ads(
        self,
        fiat_unit: str,
        coin_id: str,
        country_code: Optional[str] = None,
        side: Optional[str] = None,
        amount: Optional[Decimal] = None,
        quantity: Optional[Decimal] = None,
        pay_method: Optional[str] = None,
        block_trade: Optional[bool] = None,
        allow_trade: Optional[bool] = None,
        have_trade: Optional[bool] = None,
        follow: Optional[bool] = None,
        page: int = 1,
    ) -> MarketAdListResponse:
        """Получение рыночных объявлений"""
        params = {"fiatUnit": fiat_unit, "coinId": coin_id, "page": page}

        if country_code:
            params["countryCode"] = country_code
        if side:
            params["side"] = side
        if amount:
            params["amount"] = str(amount)
        if quantity:
            params["quantity"] = str(quantity)
        if pay_method:
            params["payMethod"] = pay_method
        if block_trade is not None:
            params["blockTrade"] = block_trade
        if allow_trade is not None:
            params["allowTrade"] = allow_trade
        if have_trade is not None:
            params["haveTrade"] = have_trade
        if follow is not None:
            params["follow"] = follow

        result = await self._request("GET", "/api/v3/fiat/market/ads/pagination", params=params)
        return MarketAdListResponse(**result)

    # ============ Order Methods ============

    async def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        """Создание ордера (захват объявления)"""
        result = await self._request("POST", "/api/v3/fiat/merchant/order/deal", data=request)
        return CreateOrderResponse(**result)

    async def get_my_orders(
        self,
        start_time: int,
        end_time: int,
        coin_id: Optional[str] = None,
        adv_order_no: Optional[str] = None,
        side: Optional[str] = None,
        order_deal_state: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> OrderListResponse:
        """Получение моих ордеров (только как maker)"""
        params = {"startTime": start_time, "endTime": end_time, "page": page, "limit": limit}

        if coin_id:
            params["coinId"] = coin_id
        if adv_order_no:
            params["advOrderNo"] = adv_order_no
        if side:
            params["side"] = side
        if order_deal_state:
            params["orderDealState"] = order_deal_state

        result = await self._request("GET", "/api/v3/fiat/merchant/order/pagination", params=params)
        return OrderListResponse(**result)

    async def get_market_orders(
        self,
        coin_id: Optional[str] = None,
        adv_order_no: Optional[str] = None,
        side: Optional[str] = None,
        order_deal_state: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
    ) -> OrderListResponse:
        """Получение всех ордеров (как maker и taker)"""
        params = {"page": page, "limit": limit}

        if coin_id:
            params["coinId"] = coin_id
        if adv_order_no:
            params["advOrderNo"] = adv_order_no
        if side:
            params["side"] = side
        if order_deal_state:
            params["orderDealState"] = order_deal_state
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        result = await self._request("GET", "/api/v3/fiat/market/order/pagination", params=params)
        return OrderListResponse(**result)

    async def confirm_paid(self, request: ConfirmPaidRequest) -> BaseResponse:
        """Подтверждение оплаты"""
        result = await self._request("POST", "/api/v3/fiat/confirm_paid", data=request)
        return BaseResponse(**result)

    async def release_coin(self, request: ReleaseCoinRequest) -> BaseResponse:
        """Релиз криптовалюты"""
        result = await self._request("POST", "/api/v3/fiat/release_coin", data=request)
        return BaseResponse(**result)

    async def get_order_detail(self, adv_order_no: str) -> OrderDetailResponse:
        """Получение деталей ордера"""
        params = {"advOrderNo": adv_order_no}

        result = await self._request("GET", "/api/v3/fiat/order/detail", params=params)
        return OrderDetailResponse(**result)

    # ============ Service Methods ============

    async def switch_service(self, request: ServiceSwitchRequest) -> BaseResponse:
        """Открытие/закрытие торговли"""
        result = await self._request("POST", "/api/v3/fiat/merchant/service/switch", data=request)
        return BaseResponse(**result)

    # ============ WebSocket Methods ============

    async def generate_listen_key(self) -> ListenKeyResponse:
        """Генерация listenKey для WebSocket"""
        result = await self._request("POST", "/api/v3/userDataStream")
        return ListenKeyResponse(**result)

    async def get_listen_key(self) -> ListenKeyResponse:
        """Получение существующего listenKey"""
        result = await self._request("GET", "/api/v3/userDataStream")
        return ListenKeyResponse(**result)

    # ============ Chat Methods ============

    async def get_chat_conversation(self, order_no: str) -> ConversationResponse:
        """Получение ID чат-сессии для ордера"""
        params = {"orderNo": order_no}

        result = await self._request("GET", "/api/v3/fiat/retrieveChatConversation", params=params)
        return ConversationResponse(**result)

    async def get_chat_messages(
        self,
        conversation_id: int,
        page: int = 1,
        limit: int = 20,
        chat_message_type: Optional[str] = None,
        message_id: Optional[int] = None,
        sort: Literal["DESC", "ASC"] = "DESC",
    ) -> ChatMessagesResponse:
        """Получение истории чата с пагинацией"""
        params = {"conversationId": conversation_id, "page": page, "limit": limit, "sort": sort}

        if chat_message_type:
            params["chatMessageType"] = chat_message_type
        if message_id:
            params["id"] = message_id

        result = await self._request("GET", "/api/v3/fiat/retrieveChatMessageWithPagination", params=params)
        return ChatMessagesResponse(**result)

    async def upload_file(self, file_data: bytes, filename: str) -> UploadFileResponse:
        """Загрузка файла"""
        if not self.session:
            raise RuntimeError("Client not initialized.")

        timestamp = self._get_timestamp()
        query_string = f"timestamp={timestamp}"
        signature = self._generate_signature(query_string)

        url = f"{self.BASE_URL}/api/v3/fiat/uploadFile"
        params = {"timestamp": timestamp, "signature": signature}

        headers = {"X-MEXC-APIKEY": self.api_key}

        form = aiohttp.FormData()
        form.add_field("file", file_data, filename=filename)

        async with self.session.post(url, params=params, data=form, headers=headers) as response:
            result = await response.json()

        return UploadFileResponse(**result)

    async def download_file(self, file_id: str) -> dict:
        """Скачивание файла"""
        params = {"fileId": file_id}

        result = await self._request("GET", "/api/v3/fiat/downloadFile", params=params)
        return result


# ============ Usage Example ============


async def main():
    """Пример использования клиента"""

    api_key = "your_api_key"
    api_secret = "your_api_secret"

    async with MEXCP2PClient(api_key, api_secret) as client:
        # Создание объявления
        ad_request = CreateUpdateAdRequest(
            payTimeLimit=15,
            initQuantity=Decimal("100"),
            price=Decimal("70000"),
            coinId="5989b56ba96a43599dbeeca5bb053f43",
            side=Side.BUY,
            fiatUnit="USD",
            payMethod="1",
            minSingleTransAmount=Decimal("10"),
            maxSingleTransAmount=Decimal("1000"),
            userAllTradeCountMin=0,
            userAllTradeCountMax=100,
        )

        ad_response = await client.create_or_update_ad(ad_request)
        print(f"Created ad: {ad_response.data}")

        # Получение рыночных объявлений
        market_ads = await client.get_market_ads(
            fiat_unit="USD", coin_id="5989b56ba96a43599dbeeca5bb053f43", side=Side.SELL, page=1
        )

        print(f"Found {len(market_ads.data)} ads")

        # Создание ордера
        if market_ads.data:
            first_ad = market_ads.data[0]
            order_request = CreateOrderRequest(advNo=first_ad.advNo, amount=Decimal("100"), userConfirmPaymentId=123)

            order_response = await client.create_order(order_request)
            print(f"Created order: {order_response.data}")

        # Получение деталей ордера
        order_detail = await client.get_order_detail("order_id_here")
        print(f"Order state: {order_detail.data.state}")

        # Генерация listenKey для WebSocket
        listen_key = await client.generate_listen_key()
        print(f"ListenKey: {listen_key.listenKey}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
