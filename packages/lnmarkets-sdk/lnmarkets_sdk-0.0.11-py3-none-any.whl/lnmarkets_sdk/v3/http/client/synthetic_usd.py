from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.synthetic_usd import (
    BestPriceResponse,
    CreateSwapOutput,
    GetSwapsParams,
    NewSwapParams,
    Swap,
)


class SyntheticUSDClient:
    """Client for Synthetic USD swap endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def get_best_price(self):
        """Get best price for USD swaps."""
        return await self._client.request(
            "GET",
            "/synthetic-usd/best-price",
            credentials=False,
            response_model=BestPriceResponse,
        )

    async def get_swaps(self, params: GetSwapsParams | None = None):
        """Get swap history."""
        return await self._client.request(
            "GET",
            "/synthetic-usd/swaps",
            params=params,
            credentials=True,
            response_model=list[Swap],
        )

    async def new_swap(self, params: NewSwapParams):
        """Create a new USD swap."""
        return await self._client.request(
            "POST",
            "/synthetic-usd/swap",
            params=params,
            credentials=True,
            response_model=CreateSwapOutput,
        )
