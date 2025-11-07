from pydantic import BaseModel, Field

from lnmarkets_sdk.v3._internal.models import BaseConfig, FromToLimitParams


class OracleIndex(BaseModel, BaseConfig):
    index: float = Field(..., description="Index value")
    time: str = Field(..., description="Time as a string value in ISO format")


class OracleLastPrice(BaseModel, BaseConfig):
    last_price: float = Field(..., description="Last price value")
    time: str = Field(..., description="Timestamp as a string value in ISO format")


class GetIndexParams(FromToLimitParams): ...


class GetLastPriceParams(FromToLimitParams): ...
