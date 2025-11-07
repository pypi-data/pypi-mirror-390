"""Integration tests for LNMarkets SDK v3"""

import asyncio
import os

import pytest
from dotenv import load_dotenv

from lnmarkets_sdk.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.v3.models.account import (
    AddBitcoinAddressParams,
    DepositLightningParams,
    GetInternalDepositsParams,
    GetInternalWithdrawalsParams,
    GetLightningDepositsParams,
    GetLightningWithdrawalsParams,
    GetOnChainDepositsParams,
    WithdrawInternalParams,
    WithdrawLightningParams,
    WithdrawOnChainParams,
)
from lnmarkets_sdk.v3.models.futures_isolated import FuturesOrder

load_dotenv()


# Add delay between tests to avoid rate limiting
@pytest.fixture
async def public_rate_limit_delay():
    """Add delay between tests for public endpoints to avoid rate limiting."""
    await asyncio.sleep(0.5)  # 0.5s delay between tests (2 requests per second)


@pytest.fixture
async def auth_rate_limit_delay():
    """Add delay between tests for authentication endpoints to avoid rate limiting."""
    await asyncio.sleep(0.1)  # 0.1s delay between tests (10 requests per second)


def create_public_config() -> APIClientConfig:
    """Create config for testnet4."""
    return APIClientConfig(network="testnet4")


def create_auth_config() -> APIClientConfig:
    """Create authenticated config for testnet4."""
    return APIClientConfig(
        network="testnet4",
        authentication=APIAuthContext(
            key=os.environ.get("V3_API_KEY", "test-key"),
            secret=os.environ.get("V3_API_KEY_SECRET", "test-secret"),
            passphrase=os.environ.get("V3_API_KEY_PASSPHRASE", "test-passphrase"),
        ),
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestBasicsIntegration:
    """Integration tests for basic API endpoints."""

    async def test_ping(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.ping()
            assert "pong" in result

    async def test_time(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.request("GET", "/time")
            assert "time" in result
            assert isinstance(result["time"], str)


@pytest.mark.asyncio
@pytest.mark.usefixtures("auth_rate_limit_delay")
class TestAccountIntegration:
    """Integration tests for account endpoints (require authentication)."""

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_account(self):
        async with LNMClient(create_auth_config()) as client:
            account = await client.account.get_account()
            assert account.balance >= 0
            assert isinstance(account.email, str)
            assert isinstance(account.username, str)
            assert account.fee_tier >= 0
            assert account.id is not None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_bitcoin_address(self):
        async with LNMClient(create_auth_config()) as client:
            result = await client.account.get_bitcoin_address()
            assert result.address is not None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_add_bitcoin_address(self):
        async with LNMClient(create_auth_config()) as client:
            params = AddBitcoinAddressParams(format="p2wpkh")
            try:
                result = await client.account.add_bitcoin_address(params)
                assert result.address is not None
                assert result.created_at is not None
            except Exception as e:
                assert (
                    "You have too many unused addresses. Please use one of them."
                    in str(e)
                )

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_deposit_lightning(self):
        async with LNMClient(create_auth_config()) as client:
            params = DepositLightningParams(amount=100_000)
            result = await client.account.deposit_lightning(params)
            assert result.deposit_id is not None
            assert result.payment_request.startswith("ln")

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_withdraw_lightning(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawLightningParams(invoice="test_invoice")
            try:
                result = await client.account.withdraw_lightning(params)
                assert result.id is not None
                assert result.amount is not None
                assert result.max_fees is not None
            except Exception as e:
                assert "Send a correct BOLT 11 invoice" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_withdraw_internal(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawInternalParams(amount=100_000, to_username="test_username")
            try:
                result = await client.account.withdraw_internal(params)
                assert result.id is not None
                assert result.amount is not None
                assert result.created_at is not None
                assert result.from_uid is not None
                assert result.to_uid is not None
            except Exception as e:
                assert "User not found" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_withdraw_on_chain(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawOnChainParams(amount=100_000, address="test_address")
            try:
                result = await client.account.withdraw_on_chain(params)
                assert result.id is not None
                assert result.amount is not None
                assert result.created_at is not None
            except Exception as e:
                assert "Invalid address" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_lightning_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetLightningDepositsParams(limit=2)
            result = await client.account.get_lightning_deposits(params)
            assert len(result) <= params.limit
            if len(result) > 0:
                assert result[0].id is not None
                assert result[0].created_at is not None
                assert result[0].amount is not None
                assert result[0].comment is None
                assert result[0].settled_at is None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_lightning_withdrawals(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetLightningWithdrawalsParams(limit=2)
            result = await client.account.get_lightning_withdrawals(params)
            assert len(result) <= params.limit
            if len(result) > 0:
                assert result[0].id is not None
                assert result[0].created_at is not None
                assert result[0].amount is not None
                assert result[0].fee is not None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_internal_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetInternalDepositsParams(limit=2)
            result = await client.account.get_internal_deposits(params)
            assert len(result) <= params.limit
            if len(result) > 0:
                assert result[0].id is not None
                assert result[0].created_at is not None
                assert result[0].amount is not None
                assert result[0].from_username is not None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_internal_withdrawals(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetInternalWithdrawalsParams(limit=2)
            result = await client.account.get_internal_withdrawals(params)
            assert len(result) <= params.limit
            if len(result) > 0:
                assert result[0].id is not None
                assert result[0].created_at is not None
                assert result[0].amount is not None
                assert result[0].to_username is not None

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_on_chain_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetOnChainDepositsParams(limit=2)
            try:
                result = await client.account.get_on_chain_deposits(params)
                assert len(result) <= params.limit
                if len(result) > 0:
                    assert result[0].id is not None
                    assert result[0].created_at is not None
                    assert result[0].amount is not None
                    assert result[0].block_height is not None
            except Exception as e:
                assert "HTTP 404: Not found" in str(e)


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestFuturesIntegration:
    """Integration tests for futures data endpoints."""

    async def test_get_ticker(self):
        async with LNMClient(create_public_config()) as client:
            ticker = await client.futures.get_ticker()
            assert ticker.index > 0
            assert ticker.last_price > 0

    async def test_get_leaderboard(self):
        async with LNMClient(create_public_config()) as client:
            leaderboard = await client.futures.get_leaderboard()
            assert isinstance(leaderboard.daily, list)

    async def test_get_candles(self):
        from lnmarkets_sdk.v3.models.futures_data import GetCandlesParams

        async with LNMClient(create_public_config()) as client:
            params = GetCandlesParams(
                from_="2023-05-23T09:52:57.863Z", range="1m", limit=1
            )
            candles = await client.futures.get_candles(params)
            assert isinstance(candles, list)
            assert len(candles) > 0
            assert candles[0].open > 0
            assert candles[0].high > 0
            assert candles[0].low > 0
            assert candles[0].close > 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("auth_rate_limit_delay")
class TestFuturesIsolatedIntegration:
    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_futures_isolated(self):
        async with LNMClient(create_auth_config()) as client:
            # Create a new trade
            params = FuturesOrder(
                type="l",  # limit order
                side="b",  # buy
                price=100_000,
                quantity=1,
                leverage=100,
            )
            trade = await client.futures.isolated.new_trade(params)
            assert trade.id is not None
            assert trade.side == "b"
            assert trade.type == "l"
            assert trade.leverage == 100

            # Get open trades
            open_trades = await client.futures.isolated.get_open_trades()
            assert isinstance(open_trades, list)
            # Our trade should be in the list
            trade_ids = [t.id for t in open_trades]
            assert trade.id in trade_ids

            # Cancel the trade
            from lnmarkets_sdk.v3.models.futures_isolated import CancelTradeParams

            cancel_params = CancelTradeParams(id=trade.id)
            canceled = await client.futures.isolated.cancel(cancel_params)
            assert canceled.id == trade.id
            assert canceled.canceled is True


@pytest.mark.asyncio
class TestFuturesCrossIntegration:
    """Integration tests for cross margin futures."""

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_position(self):
        async with LNMClient(create_auth_config()) as client:
            position = await client.futures.cross.get_position()
            assert position.margin >= 0
            assert position.leverage > 0

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_cross_orders(self):
        async with LNMClient(create_auth_config()) as client:
            # Get open orders
            open_orders = await client.futures.cross.get_open_orders()
            assert isinstance(open_orders, list)

            # Get filled orders
            from lnmarkets_sdk.v3.models.futures_cross import GetFilledOrdersParams

            params = GetFilledOrdersParams(limit=5)
            filled_orders = await client.futures.cross.get_filled_orders(params)
            assert isinstance(filled_orders, list)


@pytest.mark.asyncio
class TestOracleIntegration:
    """Integration tests for oracle endpoints."""

    async def test_get_last_price(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.oracle.get_last_price()
            assert result[0].last_price > 0
            assert result[0].time is not None

    async def test_get_index(self):
        from lnmarkets_sdk.v3.models.oracle import GetIndexParams

        async with LNMClient(create_public_config()) as client:
            params = GetIndexParams(limit=5)
            result = await client.oracle.get_index(params)
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].index > 0


@pytest.mark.asyncio
class TestSyntheticUSDIntegration:
    """Integration tests for synthetic USD endpoints."""

    async def test_get_best_price(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.synthetic_usd.get_best_price()
            assert result.ask_price

    @pytest.mark.skipif(
        not os.environ.get("V3_API_KEY"),
        reason="V3_API_KEY not set in environment",
    )
    async def test_get_swaps(self):
        from lnmarkets_sdk.v3.models.synthetic_usd import GetSwapsParams

        async with LNMClient(create_auth_config()) as client:
            params = GetSwapsParams(limit=5)
            result = await client.synthetic_usd.get_swaps(params)
            assert isinstance(result, list)
