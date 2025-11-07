from typing import Literal

from pydantic import BaseModel, Field

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams

SwapAssets = Literal["BTC", "USD"]


class Swap(BaseModel, BaseConfig):
    created_at: str
    id: UUID
    in_amount: float
    in_asset: str
    out_amount: float
    out_asset: str


class CreateSwapOutput(BaseModel, BaseConfig):
    in_amount: float = Field(
        ...,
        description="Amount to swap (in satoshis if BTC, in dollars with 2 decimal places if USD)",
    )
    in_asset: SwapAssets = Field(..., description="Asset to swap from")
    out_amount: float = Field(
        ...,
        description="Amount received after conversion (in satoshis if BTC, in dollars with 2 decimal places if USD)",
    )
    out_asset: SwapAssets = Field(..., description="Asset to swap to")


class NewSwapParams(BaseModel, BaseConfig):
    in_amount: float = Field(
        ..., description="Amount to swap (in satoshis if BTC, in cents if USD)"
    )
    in_asset: SwapAssets = Field(..., description="Asset to swap from")
    out_asset: SwapAssets = Field(..., description="Asset to swap to")


class BestPriceParams(BaseModel, BaseConfig):
    in_amount: float
    in_asset: SwapAssets
    out_asset: SwapAssets


class BestPriceResponse(BaseModel, BaseConfig):
    ask_price: float = Field(..., description="Best ask price")
    bid_price: float = Field(..., description="Best bid price")


class GetSwapsParams(FromToLimitParams): ...
