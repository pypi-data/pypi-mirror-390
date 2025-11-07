from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.funding_fees import GetFundingSettlementsResponse
from lnmarkets_sdk.v3.models.futures_data import (
    Candle,
    GetCandlesParams,
    GetFundingSettlementsParams,
    Leaderboard,
    Ticker,
)

from .cross import FuturesCrossClient
from .isolated import FuturesIsolatedClient


class FuturesClient:
    """Client for futures trading endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client
        self.isolated = FuturesIsolatedClient(client)
        self.cross = FuturesCrossClient(client)

    async def get_ticker(self):
        """Get current futures ticker data."""
        return await self._client.request(
            "GET",
            "/futures/ticker",
            credentials=False,
            response_model=Ticker,
        )

    async def get_leaderboard(self):
        """Get futures trading leaderboard."""
        return await self._client.request(
            "GET",
            "/futures/leaderboard",
            credentials=False,
            response_model=Leaderboard,
        )

    async def get_candles(self, params: GetCandlesParams):
        """Get OHLC candle data."""
        return await self._client.request(
            "GET",
            "/futures/candles",
            params=params,
            credentials=False,
            response_model=list[Candle],
        )

    async def get_funding_settlements(
        self, params: GetFundingSettlementsParams | None = None
    ):
        """Get funding settlement history."""
        return await self._client.request(
            "GET",
            "/futures/funding-settlements",
            params=params,
            credentials=False,
            response_model=GetFundingSettlementsResponse,
        )
