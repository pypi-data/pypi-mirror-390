from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.oracle import (
    GetIndexParams,
    GetLastPriceParams,
    OracleIndex,
    OracleLastPrice,
)


class OracleClient:
    """Client for oracle data endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def get_index(self, params: GetIndexParams | None = None):
        """Get index data."""
        return await self._client.request(
            "GET",
            "/oracle/index",
            params=params,
            credentials=False,
            response_model=list[OracleIndex],
        )

    async def get_last_price(
        self, params: GetLastPriceParams | None = None
    ) -> list[OracleLastPrice]:
        """Get last price data."""
        return await self._client.request(
            "GET",
            "/oracle/last-price",
            params=params,
            credentials=False,
            response_model=list[OracleLastPrice],
        )
