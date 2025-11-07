from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.funding_fees import FundingFees
from lnmarkets_sdk.v3.models.futures_isolated import (
    AddMarginParams,
    CancelTradeParams,
    CashInParams,
    CloseTradeParams,
    FuturesCanceledTrade,
    FuturesClosedTrade,
    FuturesOpenTrade,
    FuturesOrder,
    FuturesRunningTrade,
    GetClosedTradesParams,
    GetIsolatedFundingFeesParams,
    UpdateStoplossParams,
    UpdateTakeprofitParams,
)


class FuturesIsolatedClient:
    """Client for isolated futures margin endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def new_trade(self, params: FuturesOrder):
        """Open a new isolated margin futures trade."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trade",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade | FuturesOpenTrade,
        )

    async def get_running_trades(self):
        """Get all running isolated margin trades."""
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/running",
            credentials=True,
            response_model=list[FuturesRunningTrade],
        )

    async def get_open_trades(self):
        """Get all open isolated margin trades."""
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/open",
            credentials=True,
            response_model=list[FuturesOpenTrade],
        )

    async def get_closed_trades(self, params: GetClosedTradesParams | None = None):
        """Get closed isolated margin trades history."""
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/closed",
            params=params,
            credentials=True,
            response_model=list[FuturesClosedTrade],
        )

    async def close(self, params: CloseTradeParams):
        """Close an isolated margin trade."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/close",
            params=params,
            credentials=True,
            response_model=FuturesClosedTrade,
        )

    async def cancel(self, params: CancelTradeParams):
        """Cancel an isolated margin trade."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/cancel",
            params=params,
            credentials=True,
            response_model=FuturesCanceledTrade,
        )

    async def cancel_all(self):
        """Cancel all isolated margin trades."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trades/cancel-all",
            credentials=True,
            response_model=list[FuturesCanceledTrade],
        )

    async def add_margin(self, params: AddMarginParams):
        """Add margin to an isolated trade."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/add-margin",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def cash_in(self, params: CashInParams):
        """Cash in on an isolated trade."""
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/cash-in",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def update_stoploss(self, params: UpdateStoplossParams):
        """Update stop loss for an isolated trade."""
        return await self._client.request(
            "PUT",
            "/futures/isolated/trade/stoploss",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def update_takeprofit(self, params: UpdateTakeprofitParams):
        """Update take profit for an isolated trade."""
        return await self._client.request(
            "PUT",
            "/futures/isolated/trade/takeprofit",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def get_funding_fees(
        self, params: GetIsolatedFundingFeesParams | None = None
    ):
        """Get funding fees for isolated trades."""
        return await self._client.request(
            "GET",
            "/futures/isolated/funding-fees",
            params=params,
            credentials=True,
            response_model=list[FundingFees],
        )
