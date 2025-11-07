from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.account import (
    Account,
    AddBitcoinAddressParams,
    AddBitcoinAddressResponse,
    DepositLightningParams,
    DepositLightningResponse,
    GetBitcoinAddressResponse,
    GetInternalDepositsParams,
    GetInternalDepositsResponse,
    GetInternalWithdrawalsParams,
    GetInternalWithdrawalsResponse,
    GetLightningDepositsParams,
    GetLightningDepositsResponse,
    GetLightningWithdrawalsParams,
    GetLightningWithdrawalsResponse,
    GetOnChainDepositsParams,
    GetOnChainDepositsResponse,
    GetOnChainWithdrawalsParams,
    GetOnChainWithdrawalsResponse,
    WithdrawInternalParams,
    WithdrawInternalResponse,
    WithdrawLightningParams,
    WithdrawLightningResponse,
    WithdrawOnChainParams,
    WithdrawOnChainResponse,
)


class AccountClient:
    """Client for account-related endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def get_account(self):
        """Get account information."""
        return await self._client.request(
            "GET",
            "/account",
            credentials=True,
            response_model=Account,
        )

    async def get_bitcoin_address(self):
        """Get Bitcoin address for deposits."""
        return await self._client.request(
            "GET",
            "/account/address/bitcoin",
            credentials=True,
            response_model=GetBitcoinAddressResponse,
        )

    async def add_bitcoin_address(self, params: AddBitcoinAddressParams | None = None):
        """Add a new Bitcoin address."""
        return await self._client.request(
            "POST",
            "/account/address/bitcoin",
            params=params,
            credentials=True,
            response_model=AddBitcoinAddressResponse,
        )

    async def deposit_lightning(self, params: DepositLightningParams):
        """Create a Lightning invoice for deposit."""
        return await self._client.request(
            "POST",
            "/account/deposit/lightning",
            params=params,
            credentials=True,
            response_model=DepositLightningResponse,
        )

    async def withdraw_lightning(self, params: WithdrawLightningParams):
        """Withdraw via Lightning Network."""
        return await self._client.request(
            "POST",
            "/account/withdraw/lightning",
            params=params,
            credentials=True,
            response_model=WithdrawLightningResponse,
        )

    async def withdraw_internal(self, params: WithdrawInternalParams):
        """Withdraw to another LN Markets account."""
        return await self._client.request(
            "POST",
            "/account/withdraw/internal",
            params=params,
            credentials=True,
            response_model=WithdrawInternalResponse,
        )

    async def withdraw_on_chain(self, params: WithdrawOnChainParams):
        """Withdraw via on-chain Bitcoin transaction."""
        return await self._client.request(
            "POST",
            "/account/withdraw/on-chain",
            params=params,
            credentials=True,
            response_model=WithdrawOnChainResponse,
        )

    async def get_lightning_deposits(
        self, params: GetLightningDepositsParams | None = None
    ):
        """Get Lightning deposit history."""
        return await self._client.request(
            "GET",
            "/account/deposits/lightning",
            params=params,
            credentials=True,
            response_model=list[GetLightningDepositsResponse],
        )

    async def get_lightning_withdrawals(
        self, params: GetLightningWithdrawalsParams | None = None
    ):
        """Get Lightning withdrawal history."""
        return await self._client.request(
            "GET",
            "/account/withdrawals/lightning",
            params=params,
            credentials=True,
            response_model=list[GetLightningWithdrawalsResponse],
        )

    async def get_internal_deposits(
        self, params: GetInternalDepositsParams | None = None
    ):
        """Get internal deposit history."""
        return await self._client.request(
            "GET",
            "/account/deposits/internal",
            params=params,
            credentials=True,
            response_model=list[GetInternalDepositsResponse],
        )

    async def get_internal_withdrawals(
        self, params: GetInternalWithdrawalsParams | None = None
    ):
        """Get internal withdrawal history."""
        return await self._client.request(
            "GET",
            "/account/withdrawals/internal",
            params=params,
            credentials=True,
            response_model=list[GetInternalWithdrawalsResponse],
        )

    async def get_on_chain_deposits(
        self, params: GetOnChainDepositsParams | None = None
    ):
        """Get on-chain deposit history."""
        return await self._client.request(
            "GET",
            "/account/deposits/bitcoin",
            params=params,
            credentials=True,
            response_model=list[GetOnChainDepositsResponse],
        )

    async def get_on_chain_withdrawals(
        self, params: GetOnChainWithdrawalsParams | None = None
    ):
        """Get on-chain withdrawal history."""
        return await self._client.request(
            "GET",
            "/account/withdrawals/bitcoin",
            params=params,
            credentials=True,
            response_model=list[GetOnChainWithdrawalsResponse],
        )
