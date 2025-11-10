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
        """
        Get account information.

        Example:
        ```python
        async with LNMClient(config) as client:
            account = await client.account.get_account()
            print(f"Balance: {account.balance} sats")
            print(f"Username: {account.username}")
        ```
        """
        return await self._client.request(
            "GET",
            "/account",
            credentials=True,
            response_model=Account,
        )

    async def get_bitcoin_address(self):
        """
        Get Bitcoin address for deposits.

        Example:
        ```python
        async with LNMClient(config) as client:
            address = await client.account.get_bitcoin_address()
            print(f"Bitcoin address: {address.address}")
        ```
        """
        return await self._client.request(
            "GET",
            "/account/address/bitcoin",
            credentials=True,
            response_model=GetBitcoinAddressResponse,
        )

    async def add_bitcoin_address(self, params: AddBitcoinAddressParams | None = None):
        """
        Add a new Bitcoin address.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import AddBitcoinAddressParams

        async with LNMClient(config) as client:
            params = AddBitcoinAddressParams(format="p2wpkh")
            address = await client.account.add_bitcoin_address(params)
            print(f"New address: {address.address}")
        ```
        """
        return await self._client.request(
            "POST",
            "/account/address/bitcoin",
            params=params,
            credentials=True,
            response_model=AddBitcoinAddressResponse,
        )

    async def deposit_lightning(self, params: DepositLightningParams):
        """
        Create a Lightning invoice for deposit.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import DepositLightningParams

        async with LNMClient(config) as client:
            params = DepositLightningParams(
                amount=100_000,
                comment="Deposit for trading"
            )
            deposit = await client.account.deposit_lightning(params)
            print(f"Payment request: {deposit.payment_request}")
        ```
        """
        return await self._client.request(
            "POST",
            "/account/deposit/lightning",
            params=params,
            credentials=True,
            response_model=DepositLightningResponse,
        )

    async def withdraw_lightning(self, params: WithdrawLightningParams):
        """
        Withdraw via Lightning Network.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import WithdrawLightningParams

        async with LNMClient(config) as client:
            params = WithdrawLightningParams(invoice="lnbc...")
            withdrawal = await client.account.withdraw_lightning(params)
            print(f"Withdrawal ID: {withdrawal.id}")
        ```
        """
        return await self._client.request(
            "POST",
            "/account/withdraw/lightning",
            params=params,
            credentials=True,
            response_model=WithdrawLightningResponse,
        )

    async def withdraw_internal(self, params: WithdrawInternalParams):
        """
        Withdraw to another LN Markets account.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import WithdrawInternalParams

        async with LNMClient(config) as client:
            params = WithdrawInternalParams(amount=100_000, to_username="user123")
            withdrawal = await client.account.withdraw_internal(params)
            print(f"Withdrawal ID: {withdrawal.id}")
        ```
        """
        return await self._client.request(
            "POST",
            "/account/withdraw/internal",
            params=params,
            credentials=True,
            response_model=WithdrawInternalResponse,
        )

    async def withdraw_on_chain(self, params: WithdrawOnChainParams):
        """
        Withdraw via on-chain Bitcoin transaction.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import WithdrawOnChainParams

        async with LNMClient(config) as client:
            params = WithdrawOnChainParams(
                amount=100_000,
                address="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
            )
            withdrawal = await client.account.withdraw_on_chain(params)
            print(f"Withdrawal ID: {withdrawal.id}")
        ```
        """
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
        """
        Get Lightning deposit history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetLightningDepositsParams

        async with LNMClient(config) as client:
            params = GetLightningDepositsParams(limit=10, settled=True)
            deposits = await client.account.get_lightning_deposits(params)
            for deposit in deposits:
                print(f"Deposit: {deposit.id}, Amount: {deposit.amount}")
        ```
        """
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
        """
        Get Lightning withdrawal history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetLightningWithdrawalsParams

        async with LNMClient(config) as client:
            params = GetLightningWithdrawalsParams(
                limit=10,
                status="processed"
            )
            withdrawals = await client.account.get_lightning_withdrawals(params)
            for withdrawal in withdrawals:
                print(f"Withdrawal: {withdrawal.id}, Status: {withdrawal.status}")
        ```
        """
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
        """
        Get internal deposit history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetInternalDepositsParams

        async with LNMClient(config) as client:
            params = GetInternalDepositsParams(limit=10)
            deposits = await client.account.get_internal_deposits(params)
            for deposit in deposits:
                print(f"From: {deposit.from_username}, Amount: {deposit.amount}")
        ```
        """
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
        """
        Get internal withdrawal history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetInternalWithdrawalsParams

        async with LNMClient(config) as client:
            params = GetInternalWithdrawalsParams(limit=10)
            withdrawals = await client.account.get_internal_withdrawals(params)
            for withdrawal in withdrawals:
                print(f"To: {withdrawal.to_username}, Amount: {withdrawal.amount}")
        ```
        """
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
        """
        Get on-chain deposit history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetOnChainDepositsParams

        async with LNMClient(config) as client:
            params = GetOnChainDepositsParams(
                limit=10,
                status="CONFIRMED"
            )
            deposits = await client.account.get_on_chain_deposits(params)
            for deposit in deposits:
                print(f"TX ID: {deposit.tx_id}, Status: {deposit.status}")
        ```
        """
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
        """
        Get on-chain withdrawal history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.account import GetOnChainWithdrawalsParams

        async with LNMClient(config) as client:
            params = GetOnChainWithdrawalsParams(
                limit=10,
                status="processed"
            )
            withdrawals = await client.account.get_on_chain_withdrawals(params)
            for withdrawal in withdrawals:
                print(f"Address: {withdrawal.address}, Status: {withdrawal.status}")
        ```
        """
        return await self._client.request(
            "GET",
            "/account/withdrawals/bitcoin",
            params=params,
            credentials=True,
            response_model=list[GetOnChainWithdrawalsResponse],
        )
