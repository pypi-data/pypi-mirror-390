from typing import Literal

from pydantic import BaseModel, Field

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class Account(BaseModel, BaseConfig):
    username: str = Field(..., description="Username of the user")
    synthetic_usd_balance: float = Field(
        ..., description="Synthetic USD balance of the user (in dollars)"
    )
    balance: float = Field(..., description="Balance of the user (in satoshis)")
    fee_tier: int = Field(..., description="Fee tier of the user")
    email: str | None = Field(default=None, description="Email of the user")
    id: UUID = Field(..., description="Unique identifier for this account")
    linking_public_key: str | None = Field(
        default=None, description="Public key of the user"
    )


class GetOnChainDepositsResponse(BaseModel, BaseConfig):
    amount: float = Field(..., description="The amount of the deposit")
    block_height: int | None = Field(
        default=None, description="The block height of the deposit"
    )
    confirmations: int = Field(
        ..., description="The number of confirmations of the deposit"
    )
    created_at: str = Field(..., description="The date the deposit was created")
    id: UUID = Field(..., description="The unique identifier for the deposit")
    status: Literal["MEMPOOL", "CONFIRMED", "IRREVERSIBLE"] = Field(
        ..., description="The status of the deposit"
    )
    tx_id: str = Field(..., description="The transaction ID of the deposit")


class GetInternalDepositsResponse(BaseModel, BaseConfig):
    amount: float = Field(..., description="Amount of the deposit (in satoshis)")
    created_at: str = Field(..., description="Timestamp when the deposit was created")
    from_username: str = Field(..., description="Username of the sender")
    id: UUID = Field(..., description="Unique identifier for this deposit")


class GetInternalWithdrawalsResponse(BaseModel, BaseConfig):
    amount: float = Field(..., description="Amount of the transfer (in satoshis)")
    created_at: str = Field(..., description="Timestamp when the transfer was created")
    id: UUID = Field(..., description="Unique identifier for this transfer")
    to_username: str = Field(..., description="Username of the recipient")


class GetLightningDepositsResponse(BaseModel, BaseConfig):
    amount: float | None = Field(
        None, description="Amount of the deposit (in satoshis)"
    )
    comment: str | None = Field(default=None, description="Comment of the deposit")
    created_at: str = Field(..., description="Timestamp when the deposit was created")
    id: UUID = Field(..., description="Unique identifier for this deposit")
    payment_hash: str | None = Field(
        default=None, description="Payment hash of the deposit"
    )
    settled_at: str | None = Field(
        default=None, description="Timestamp when the deposit was settled"
    )


class GetLightningWithdrawalsResponse(BaseModel, BaseConfig):
    amount: float = Field(..., description="Amount of the withdrawal (in satoshis)")
    created_at: str = Field(
        ..., description="Timestamp when the withdrawal was created"
    )
    fee: float = Field(..., description="Fee of the withdrawal (in satoshis)")
    id: UUID = Field(..., description="Unique identifier for the withdrawal")
    payment_hash: str = Field(..., description="Payment hash of the withdrawal")
    status: Literal["failed", "processed", "processing"] = Field(
        ..., description="Status of the withdrawal"
    )


class GetOnChainWithdrawalsResponse(BaseModel, BaseConfig):
    address: str = Field(..., description="Address to withdraw to")
    amount: float = Field(..., description="Amount to withdraw")
    created_at: str = Field(
        ..., description="Timestamp when the withdrawal was created"
    )
    fee: float | None = Field(
        default=None, description="Fee of the withdrawal (in satoshis)"
    )
    id: UUID = Field(..., description="Unique identifier for the withdrawal")
    status: Literal["canceled", "pending", "processed", "processing", "rejected"] = (
        Field(..., description="Status of the withdrawal")
    )
    tx_id: str | None = Field(
        default=None, description="Transaction ID of the withdrawal"
    )


class InternalTransfer(BaseModel, BaseConfig):
    amount: float
    created_at: str
    from_uid: UUID
    from_username: str
    id: UUID
    settled_at: str | None
    success: bool | None
    to_uid: UUID
    to_username: str


class PendingOnChainWithdrawalRequest(BaseModel, BaseConfig):
    address: str
    amount: float
    created_at: str
    fee: float | None
    id: UUID
    status: Literal["pending"]
    tx_id: None = None
    updated_at: str


class DepositLightningResponse(BaseModel, BaseConfig):
    deposit_id: UUID = Field(..., description="Deposit ID")
    payment_request: str = Field(..., description="Lightning payment request invoice")


class WithdrawInternalResponse(BaseModel, BaseConfig):
    id: UUID
    created_at: str
    from_uid: UUID
    to_uid: UUID
    amount: float


class WithdrawOnChainResponse(BaseModel, BaseConfig):
    id: UUID
    uid: UUID
    amount: float
    address: str
    created_at: str
    updated_at: str
    block_id: str | None
    confirmation_height: int | None
    fee: float | None
    status: Literal["pending"]
    tx_id: None = None


class GetBitcoinAddressResponse(BaseModel, BaseConfig):
    address: str = Field(..., description="Bitcoin address")


class AddBitcoinAddressResponse(BaseModel, BaseConfig):
    address: str = Field(..., description="The generated Bitcoin address")
    created_at: str = Field(..., description="The creation time of the address")


class AddBitcoinAddressParams(BaseModel, BaseConfig):
    format: Literal["p2tr", "p2wpkh"] | None = Field(
        None, description="The format of the Bitcoin address"
    )


class DepositLightningParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to deposit (in satoshis)")
    comment: str | None = Field(default=None, description="Comment for the deposit")
    description_hash: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
        description="Description hash for the deposit",
    )


class WithdrawLightningParams(BaseModel, BaseConfig):
    invoice: str = Field(..., description="Lightning invoice to pay")


class WithdrawLightningResponse(BaseModel, BaseConfig):
    amount: float = Field(..., description="Amount of the withdrawal (in satoshis)")
    id: UUID = Field(..., description="Unique identifier for the withdrawal")
    max_fees: float = Field(
        ..., description="Maximum fees of the withdrawal (in satoshis)"
    )
    payment_hash: str = Field(..., description="Payment hash of the withdrawal")


class WithdrawInternalParams(BaseModel, BaseConfig):
    amount: float = Field(..., gt=0, description="Amount to withdraw (in satoshis)")
    to_username: str = Field(..., description="Username of the recipient")


class WithdrawOnChainParams(BaseModel, BaseConfig):
    address: str = Field(..., description="Bitcoin address to withdraw to")
    amount: float = Field(..., gt=0, description="Amount to withdraw (in satoshis)")


class GetLightningDepositsParams(FromToLimitParams): ...


class GetLightningWithdrawalsParams(FromToLimitParams): ...


class GetInternalDepositsParams(FromToLimitParams): ...


class GetInternalWithdrawalsParams(FromToLimitParams): ...


class GetOnChainDepositsParams(FromToLimitParams): ...


class GetOnChainWithdrawalsParams(FromToLimitParams): ...
