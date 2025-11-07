from typing import Literal

from pydantic import BaseModel, Field, model_validator

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class FuturesOrder(BaseModel, BaseConfig):
    leverage: float = Field(..., description="Leverage of the position")
    side: Literal["b", "s"] = Field(
        ..., description="Trade side: b (buy/long) or s (sell/short)"
    )
    stoploss: float | None = Field(
        default=None,
        ge=0,
        multiple_of=0.5,
        description="Stop loss price level (0 if not set)",
    )
    takeprofit: float | None = Field(
        default=None,
        ge=0,
        multiple_of=0.5,
        description="Take profit price level (0 if not set)",
    )
    margin: int | None = Field(
        default=None, description="Margin of the position (in satoshis)"
    )
    quantity: int | None = Field(
        default=None, description="Quantity of the position (in USD)"
    )
    price: float | None = Field(
        default=None, gt=0, multiple_of=0.5, description="Price of the limit order"
    )
    type: Literal["l", "m"] = Field(
        ..., description="Trade type: l (limit) or m (market)"
    )

    @model_validator(mode="after")
    def validate_schema(self):
        if (self.quantity is None) == (self.margin is None):
            raise ValueError("Exactly one of quantity or margin must be set")
        if self.type == "l" and self.price is None:
            raise ValueError("'price' is required when type='l'")
        if self.type == "m" and self.price is not None:
            raise ValueError("'price' must not be set when type='m'")
        return self


class FuturesTrade(BaseModel, BaseConfig):
    canceled: bool
    closed: bool
    closed_at: str | None = None
    closing_fee: float
    created_at: str
    entry_margin: float | None = None
    entry_price: float | None = None
    exit_price: float | None = None
    filled_at: str | None = None
    id: UUID
    leverage: float
    liquidation: float
    maintenance_margin: float
    margin: float
    open: bool
    opening_fee: float
    pl: float
    price: float
    quantity: float
    running: bool
    side: Literal["b", "s"]
    stoploss: float
    sum_funding_fees: float
    takeprofit: float
    type: Literal["l", "m"]


class FuturesOpenTrade(FuturesTrade):
    canceled: Literal[False] = False
    closed: Literal[False] = False
    closed_at: None = None
    filled_at: None = None
    running: Literal[False] = False
    type: Literal["l"] = "l"


class FuturesRunningTrade(FuturesTrade):
    canceled: Literal[False] = False
    closed: Literal[False] = False
    closed_at: None = None
    filled_at: str = ""
    running: Literal[True] = True


class FuturesClosedTrade(FuturesTrade):
    canceled: Literal[False] = False
    closed: Literal[True] = True
    closed_at: str = ""
    exit_price: float = 0.0
    filled_at: str = ""
    open: Literal[False] = False
    running: Literal[False] = False


class FuturesCanceledTrade(FuturesTrade):
    canceled: Literal[True] = True
    closed: Literal[False] = False
    closed_at: str = ""
    filled_at: None = None
    open: Literal[False] = False
    running: Literal[False] = False
    type: Literal["l"] = "l"


class AddMarginParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount of margin to add (in satoshis)")
    id: UUID = Field(..., description="Trade ID")


class CancelTradeParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID to cancel")


class CashInParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to cash in (in satoshis)")
    id: UUID = Field(..., description="Trade ID")


class CloseTradeParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID to close")


class UpdateStoplossParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID")
    stoploss: float = Field(..., description="New stop loss price level")


class UpdateTakeprofitParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID")
    takeprofit: float = Field(..., description="New take profit price level")


class GetClosedTradesParams(FromToLimitParams): ...


class GetIsolatedFundingFeesParams(FromToLimitParams):
    trade_id: UUID | None = None
