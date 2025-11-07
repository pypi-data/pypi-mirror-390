from pydantic import BaseModel, Field

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig


class FundingFees(BaseModel, BaseConfig):
    """Funding fee entry."""

    fee: float = Field(..., description="Funding fee amount")
    settlement_id: UUID = Field(..., description="Funding settlement ID")
    time: str = Field(..., description="Timestamp in ISO format")
    trade_id: UUID | None = Field(default=None, description="Associated trade ID")


class FundingSettlement(BaseModel, BaseConfig):
    """Funding settlement entry."""

    funding_rate: float = Field(..., description="Funding rate")
    id: UUID = Field(..., description="Funding settlement ID")
    fixing_price: float = Field(..., description="Fixing price")
    time: str = Field(..., description="Funding settlement time")


class GetFundingSettlementsResponse(BaseModel, BaseConfig):
    """Funding settlement response."""

    data: list[FundingSettlement] = Field(
        ..., description="List of funding settlements"
    )
    count: int = Field(..., description="Number of items returned")
