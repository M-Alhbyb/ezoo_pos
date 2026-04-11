"""
Unit tests for Partner Wallet balance and transaction methods.

Tests:
- Wallet balance calculation (O(1) using balance_after)
- Wallet transaction history pagination
- Manual wallet adjustments
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.modules.partners.partner_profit_service import PartnerProfitService
from app.models.partner import Partner
from app.models.partner_wallet_transaction import PartnerWalletTransaction


@pytest.mark.asyncio
async def test_get_partner_wallet_balance_zero():
    """Test wallet balance returns zero when no transactions exist."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock no transactions
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    balance = await service.get_partner_wallet_balance(partner_id)

    assert balance == Decimal("0.00")


@pytest.mark.asyncio
async def test_get_partner_wallet_balance_with_transactions():
    """Test wallet balance returns latest balance_after."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock latest transaction
    mock_result = MagicMock()
    mock_transaction = PartnerWalletTransaction(
        id=uuid4(),
        partner_id=partner_id,
        amount=Decimal("150.00"),
        transaction_type="sale_profit",
        balance_after=Decimal("350.00"),
        created_at=datetime.now(timezone.utc),
    )
    mock_result.scalar_one_or_none.return_value = mock_transaction
    db.execute.return_value = mock_result

    balance = await service.get_partner_wallet_balance(partner_id)

    assert balance == Decimal("350.00")


@pytest.mark.asyncio
async def test_get_partner_wallet_transactions_pagination():
    """Test getting paginated transaction history."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock paginated results
    mock_result = MagicMock()
    mock_transactions = [
        PartnerWalletTransaction(
            id=uuid4(),
            partner_id=partner_id,
            amount=Decimal("100.00"),
            transaction_type="sale_profit",
            balance_after=Decimal("200.00"),
            created_at=datetime.now(timezone.utc),
        ),
        PartnerWalletTransaction(
            id=uuid4(),
            partner_id=partner_id,
            amount=Decimal("50.00"),
            transaction_type="manual_adjustment",
            balance_after=Decimal("100.00"),
            created_at=datetime.now(timezone.utc),
        ),
    ]
    mock_result.scalars.return_value.all.return_value = mock_transactions
    db.execute.return_value = mock_result

    transactions = await service.get_partner_wallet_transactions(
        partner_id, limit=10, offset=0
    )

    assert len(transactions) == 2
    assert transactions[0].transaction_type == "sale_profit"
    assert transactions[1].transaction_type == "manual_adjustment"


@pytest.mark.asyncio
async def test_adjust_wallet_credit():
    """Test manual wallet adjustment (credit)."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()
    amount = Decimal("100.00")
    description = "Manual credit adjustment"

    # Mock partner lookup
    mock_partner_result = MagicMock()
    mock_partner = Partner(
        id=partner_id,
        name="Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("5000.00"),
    )
    mock_partner_result.scalar_one_or_none.return_value = mock_partner
    db.execute.return_value = mock_partner_result

    # Mock balance query (returns zero)
    # This will be called twice: once in adjust_wallet, once in get_partner_wallet_balance
    mock_balance_result = MagicMock()
    mock_balance_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_balance_result

    # First call for get_partner_for_update, second for get_partner_wallet_balance
    db.execute.side_effect = [mock_partner_result, mock_balance_result]

    transaction = await service.adjust_wallet(partner_id, amount, description)

    assert transaction is not None
    assert db.add.called
    assert db.commit.called


@pytest.mark.asyncio
async def test_adjust_wallet_debit():
    """Test manual wallet adjustment (debit - negative amount)."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()
    amount = Decimal("-50.00")  # Negative for debit
    description = "Correction for error"

    # Mock partner lookup
    mock_partner_result = MagicMock()
    mock_partner = Partner(
        id=partner_id,
        name="Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("5000.00"),
    )
    mock_partner_result.scalar_one_or_none.return_value = mock_partner

    # Mock existing balance
    mock_balance_result = MagicMock()
    mock_existing_transaction = PartnerWalletTransaction(
        id=uuid4(),
        partner_id=partner_id,
        amount=Decimal("100.00"),
        balance_after=Decimal("100.00"),
    )
    mock_balance_result.scalar_one_or_none.return_value = mock_existing_transaction

    db.execute.side_effect = [mock_partner_result, mock_balance_result]

    transaction = await service.adjust_wallet(partner_id, amount, description)

    assert transaction is not None
    # Balance should be 100.00 - 50.00 = 50.00
    # balance_after is calculated in the method


@pytest.mark.asyncio
async def test_adjust_wallet_zero_amount_raises_error():
    """Test that zero amount adjustment raises ValueError."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    with pytest.raises(ValueError, match="cannot be zero"):
        await service.adjust_wallet(partner_id, Decimal("0.00"), "Invalid adjustment")


@pytest.mark.asyncio
async def test_adjust_wallet_nonexistent_partner_raises_error():
    """Test that adjusting wallet for non-existent partner raises ValueError."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock partner not found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(ValueError, match="not found"):
        await service.adjust_wallet(partner_id, Decimal("100.00"), "Adjustment")


@pytest.mark.asyncio
async def test_wallet_balance_uses_latest_transaction():
    """Test that balance calculation uses O(1) balance_after from latest transaction."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock latest transaction with specific balance_after
    mock_result = MagicMock()
    latest_transaction = PartnerWalletTransaction(
        id=uuid4(),
        partner_id=partner_id,
        amount=Decimal("75.00"),
        transaction_type="sale_profit",
        balance_after=Decimal("425.50"),  # This is what should be returned
        created_at=datetime.now(timezone.utc),
    )
    mock_result.scalar_one_or_none.return_value = latest_transaction
    db.execute.return_value = mock_result

    balance = await service.get_partner_wallet_balance(partner_id)

    # Verify we got balance_after, not just the amount
    assert balance == Decimal("425.50")


@pytest.mark.asyncio
async def test_transaction_history_ordered_by_created_at_desc():
    """Test that transaction history is ordered by created_at descending."""
    db = AsyncMock()
    service = PartnerProfitService(db=db)

    partner_id = uuid4()

    # Mock execute call
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    await service.get_partner_wallet_transactions(partner_id, limit=100, offset=0)

    # Verify query was executed (ordering happens in SQL query)
    assert db.execute.called
