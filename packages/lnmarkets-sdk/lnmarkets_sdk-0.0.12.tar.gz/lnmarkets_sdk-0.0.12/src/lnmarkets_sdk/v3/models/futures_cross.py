from typing import Literal

from pydantic import BaseModel, Field

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class FuturesCrossOrderSideQuantity(BaseModel, BaseConfig):
    side: Literal["b", "s"] = Field(
        ..., description="Trade side: b (buy/long) or s (sell/short)"
    )
    quantity: int = Field(..., gt=0, description="Quantity of the position")


class FuturesCrossOrderLimit(FuturesCrossOrderSideQuantity):
    type: Literal["limit"] = Field(..., description="Trade type: limit")
    price: float = Field(
        ..., gt=0, multiple_of=0.5, description="Price of the limit order"
    )


class FuturesCrossOrderMarket(FuturesCrossOrderSideQuantity):
    type: Literal["market"] = Field(..., description="Trade type: market")
    price: None = None


class FuturesCrossOpenOrder(BaseModel, BaseConfig):
    canceled: Literal[False] = False
    canceled_at: None = None
    created_at: str
    filled: Literal[False] = False
    filled_at: None = None
    id: UUID
    open: Literal[True] = True
    price: float
    quantity: float
    side: Literal["b", "s"]
    trading_fee: float
    type: Literal["limit"]


class FuturesCrossFilledOrder(BaseModel, BaseConfig):
    canceled: Literal[False] = False
    canceled_at: None = None
    created_at: str
    filled: Literal[True] = True
    filled_at: str
    id: UUID
    open: Literal[False] = False
    price: float
    quantity: float
    side: Literal["b", "s"]
    trading_fee: float
    type: Literal["limit", "liquidation", "market"]


class FuturesCrossCanceledOrder(BaseModel, BaseConfig):
    canceled: Literal[True] = True
    canceled_at: str
    created_at: str
    filled: Literal[False] = False
    filled_at: None = None
    id: UUID
    open: Literal[False] = False
    price: float
    quantity: float
    side: Literal["b", "s"]
    trading_fee: float
    type: Literal["limit"]


class FuturesCrossPosition(BaseModel, BaseConfig):
    delta_pl: float = Field(..., description="Delta P&L")
    entry_price: float | None = Field(default=None, description="Entry price")
    funding_fees: float = Field(..., description="Funding fees")
    id: UUID = Field(..., description="Position ID")
    initial_margin: float = Field(..., description="Initial margin")
    leverage: int = Field(..., gt=0, description="Leverage")
    liquidation: float | None = Field(default=None, description="Liquidation price")
    maintenance_margin: float = Field(..., description="Maintenance margin")
    margin: float = Field(..., description="Current margin")
    quantity: float = Field(..., description="Position quantity")
    running_margin: float = Field(..., description="Running margin")
    total_pl: float = Field(..., description="Total P&L")
    trading_fees: float = Field(..., description="Trading fees")
    updated_at: str = Field(..., description="Last update timestamp")


class FuturesCrossTransfer(BaseModel, BaseConfig):
    amount: float
    id: UUID
    time: str


class DepositParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to deposit (in satoshis)")


class WithdrawParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to withdraw (in satoshis)")


class SetLeverageParams(BaseModel, BaseConfig):
    leverage: float = Field(
        ..., ge=1, le=100, description="Leverage (between 1 and 100)"
    )


class CancelOrderParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Cross order ID to cancel")


class GetFilledOrdersParams(FromToLimitParams): ...


class GetTransfersParams(FromToLimitParams): ...


class GetCrossFundingFeesParams(FromToLimitParams): ...
