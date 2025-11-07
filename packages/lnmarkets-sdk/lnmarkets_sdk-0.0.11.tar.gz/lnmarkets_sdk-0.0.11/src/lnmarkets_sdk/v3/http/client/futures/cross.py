from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.funding_fees import FundingFees
from lnmarkets_sdk.v3.models.futures_cross import (
    CancelOrderParams,
    DepositParams,
    FuturesCrossCanceledOrder,
    FuturesCrossFilledOrder,
    FuturesCrossOpenOrder,
    FuturesCrossOrderLimit,
    FuturesCrossOrderMarket,
    FuturesCrossPosition,
    FuturesCrossTransfer,
    GetCrossFundingFeesParams,
    GetFilledOrdersParams,
    GetTransfersParams,
    SetLeverageParams,
    WithdrawParams,
)


class FuturesCrossClient:
    """Client for cross margin futures endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def new_order(
        self, params: FuturesCrossOrderLimit | FuturesCrossOrderMarket
    ) -> FuturesCrossOpenOrder | FuturesCrossFilledOrder | FuturesCrossCanceledOrder:
        """Place a new cross margin order."""
        return await self._client.request(
            "POST",
            "/futures/cross/order",
            params=params,
            credentials=True,
            response_model=FuturesCrossOpenOrder
            | FuturesCrossFilledOrder
            | FuturesCrossCanceledOrder,
        )

    async def get_position(self):
        """Get current cross margin position."""
        return await self._client.request(
            "GET",
            "/futures/cross/position",
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def get_open_orders(self):
        """Get all open cross margin orders."""
        return await self._client.request(
            "GET",
            "/futures/cross/orders/open",
            credentials=True,
            response_model=list[FuturesCrossOpenOrder],
        )

    async def get_filled_orders(self, params: GetFilledOrdersParams | None = None):
        """Get filled cross margin orders history."""
        return await self._client.request(
            "GET",
            "/futures/cross/orders/filled",
            params=params,
            credentials=True,
            response_model=list[FuturesCrossFilledOrder],
        )

    async def close(
        self,
    ) -> FuturesCrossOpenOrder | FuturesCrossFilledOrder | FuturesCrossCanceledOrder:
        """Close cross margin position."""
        return await self._client.request(
            "POST",
            "/futures/cross/position/close",
            credentials=True,
            response_model=FuturesCrossOpenOrder
            | FuturesCrossFilledOrder
            | FuturesCrossCanceledOrder,
        )

    async def cancel(self, params: CancelOrderParams):
        """Cancel a cross margin order."""
        return await self._client.request(
            "POST",
            "/futures/cross/order/cancel",
            params=params,
            credentials=True,
            response_model=FuturesCrossCanceledOrder,
        )

    async def cancel_all(self):
        """Cancel all cross margin orders."""
        return await self._client.request(
            "POST",
            "/futures/cross/orders/cancel-all",
            credentials=True,
            response_model=list[FuturesCrossCanceledOrder],
        )

    async def deposit(self, params: DepositParams):
        """Deposit funds to cross margin account."""
        return await self._client.request(
            "POST",
            "/futures/cross/deposit",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def withdraw(self, params: WithdrawParams):
        """Withdraw funds from cross margin account."""
        return await self._client.request(
            "POST",
            "/futures/cross/withdraw",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def set_leverage(self, params: SetLeverageParams):
        """Set leverage for cross margin trading."""
        return await self._client.request(
            "PUT",
            "/futures/cross/leverage",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def get_transfers(self, params: GetTransfersParams | None = None):
        """Get cross margin transfer history."""
        return await self._client.request(
            "GET",
            "/futures/cross/transfers",
            params=params,
            credentials=True,
            response_model=list[FuturesCrossTransfer],
        )

    async def get_funding_fees(self, params: GetCrossFundingFeesParams | None = None):
        """Get funding fees for cross margin."""
        return await self._client.request(
            "GET",
            "/futures/cross/funding-fees",
            params=params,
            credentials=True,
            response_model=list[FundingFees],
        )
