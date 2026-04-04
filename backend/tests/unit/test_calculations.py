"""
Unit tests for the financial calculation engine.
Tests cover edge cases for currency rounding, VAT calculations, and fee calculations.
"""

import pytest
from decimal import Decimal
from app.core.calculations import (
    round_currency,
    calculate_line_total,
    calculate_fee_amount,
    calculate_vat,
    calculate_sale_total,
)


class TestRoundCurrency:
    """Test cases for currency rounding function."""

    def test_round_half_up_basic(self):
        """Test ROUND_HALF_UP with basic values."""
        assert round_currency(Decimal("3.335")) == Decimal("3.34")
        assert round_currency(Decimal("3.334")) == Decimal("3.33")

    def test_round_half_up_exact_value(self):
        """Test rounding when value is already at 2 decimal places."""
        assert round_currency(Decimal("100.50")) == Decimal("100.50")
        assert round_currency(Decimal("0.00")) == Decimal("0.00")

    def test_round_half_up_edge_cases(self):
        """Test rounding at the boundary (0.005)."""
        # 0.005 should round up to 0.01
        assert round_currency(Decimal("0.005")) == Decimal("0.01")
        # 0.0049 should round down to 0.00
        assert round_currency(Decimal("0.004")) == Decimal("0.00")

    def test_round_large_values(self):
        """Test rounding with large monetary values."""
        assert round_currency(Decimal("999999.995")) == Decimal("1000000.00")
        assert round_currency(Decimal("999999.994")) == Decimal("999999.99")

    def test_round_small_values(self):
        """Test rounding with very small values."""
        assert round_currency(Decimal("0.001")) == Decimal("0.00")
        assert round_currency(Decimal("0.009")) == Decimal("0.01")

    def test_round_negative_values(self):
        """Test that negative values are handled (though not typically used in financial calcs)."""
        assert round_currency(Decimal("-3.335")) == Decimal("-3.34")
        assert round_currency(Decimal("-3.334")) == Decimal("-3.33")


class TestCalculateLineTotal:
    """Test cases for line item total calculation."""

    def test_basic_calculation(self):
        """Test basic line total calculation."""
        result = calculate_line_total(2, Decimal("150.00"))
        assert result == Decimal("300.00")

    def test_fractional_unit_price(self):
        """Test with fractional unit price."""
        result = calculate_line_total(5, Decimal("33.33"))
        assert result == Decimal("166.65")

    def test_large_quantity(self):
        """Test with large quantity (requirement: support up to 10,000 units)."""
        result = calculate_line_total(10000, Decimal("1.50"))
        assert result == Decimal("15000.00")

    def test_zero_unit_price(self):
        """Test with zero unit price (should be allowed for free items)."""
        result = calculate_line_total(5, Decimal("0.00"))
        assert result == Decimal("0.00")

    def test_invalid_quantity_zero(self):
        """Test that zero quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            calculate_line_total(0, Decimal("100.00"))

    def test_invalid_quantity_negative(self):
        """Test that negative quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            calculate_line_total(-1, Decimal("100.00"))

    def test_invalid_unit_price_negative(self):
        """Test that negative unit price raises ValueError."""
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            calculate_line_total(1, Decimal("-10.00"))


class TestCalculateFeeAmount:
    """Test cases for fee calculation."""

    def test_fixed_fee(self):
        """Test fixed fee calculation."""
        result = calculate_fee_amount(Decimal("30.00"), "fixed", Decimal("500.00"))
        assert result == Decimal("30.00")

    def test_percentage_fee(self):
        """Test percentage fee calculation against subtotal."""
        result = calculate_fee_amount(Decimal("5.00"), "percent", Decimal("1000.00"))
        assert result == Decimal("50.00")

    def test_percentage_fee_rounding(self):
        """Test percentage fee rounding to 2 decimal places."""
        # 5% of 333.33 = 16.6665 -> should round to 16.67
        result = calculate_fee_amount(Decimal("5.00"), "percent", Decimal("333.33"))
        assert result == Decimal("16.67")

    def test_percentage_fee_with_fractional_percent(self):
        """Test percentage fee with fractional percentage."""
        # 2.5% of 200 = 5.00
        result = calculate_fee_amount(Decimal("2.5"), "percent", Decimal("200.00"))
        assert result == Decimal("5.00")

    def test_zero_fixed_fee(self):
        """Test zero fixed fee (should return 0)."""
        result = calculate_fee_amount(Decimal("0.00"), "fixed", Decimal("500.00"))
        assert result == Decimal("0.00")

    def test_zero_percentage_fee(self):
        """Test zero percentage fee (should return 0)."""
        result = calculate_fee_amount(Decimal("0.00"), "percent", Decimal("500.00"))
        assert result == Decimal("0.00")

    def test_invalid_fee_value_type(self):
        """Test that invalid fee type raises ValueError."""
        with pytest.raises(ValueError, match="Fee value type must be"):
            calculate_fee_amount(Decimal("10.00"), "invalid", Decimal("100.00"))

    def test_negative_fee_value(self):
        """Test that negative fee value raises ValueError."""
        with pytest.raises(ValueError, match="Fee value cannot be negative"):
            calculate_fee_amount(Decimal("-10.00"), "fixed", Decimal("100.00"))

    def test_negative_subtotal(self):
        """Test that negative subtotal raises ValueError."""
        with pytest.raises(ValueError, match="Subtotal cannot be negative"):
            calculate_fee_amount(Decimal("10.00"), "percent", Decimal("-100.00"))


class TestCalculateVAT:
    """Test cases for VAT calculation."""

    def test_vat_enabled_percent(self):
        """Test VAT calculation with percentage type."""
        # VAT 16% on subtotal 500 + fees 30 = 84.80
        vat_amount, vat_rate = calculate_vat(
            Decimal("500.00"), Decimal("30.00"), True, "percent", Decimal("16.00")
        )
        assert vat_amount == Decimal("84.80")
        assert vat_rate == Decimal("16.00")

    def test_vat_enabled_fixed(self):
        """Test VAT calculation with fixed amount."""
        # Fixed VAT of 20.00
        vat_amount, vat_rate = calculate_vat(
            Decimal("500.00"), Decimal("30.00"), True, "fixed", Decimal("20.00")
        )
        assert vat_amount == Decimal("20.00")
        assert vat_rate == Decimal("20.00")

    def test_vat_disabled(self):
        """Test that VAT returns 0 when disabled."""
        vat_amount, vat_rate = calculate_vat(
            Decimal("500.00"), Decimal("30.00"), False, "percent", Decimal("16.00")
        )
        assert vat_amount == Decimal("0")
        assert vat_rate is None

    def test_vat_percentage_rounding(self):
        """Test VAT percentage rounding edge case from spec."""
        # 10% VAT on 33.33 = 3.333 -> should round to 3.33
        vat_amount, vat_rate = calculate_vat(
            Decimal("33.33"), Decimal("0.00"), True, "percent", Decimal("10.00")
        )
        assert vat_amount == Decimal("3.33")

    def test_vat_zero_taxable_amount(self):
        """Test VAT with zero taxable amount."""
        vat_amount, vat_rate = calculate_vat(
            Decimal("0.00"), Decimal("0.00"), True, "percent", Decimal("16.00")
        )
        assert vat_amount == Decimal("0.00")

    def test_vat_large_percentage(self):
        """Test VAT with large percentage (e.g., 27% European rate)."""
        vat_amount, vat_rate = calculate_vat(
            Decimal("100.00"), Decimal("0.00"), True, "percent", Decimal("27.00")
        )
        assert vat_amount == Decimal("27.00")

    def test_vat_invalid_type(self):
        """Test that invalid vat_type raises ValueError."""
        with pytest.raises(ValueError, match="VAT type must be"):
            calculate_vat(
                Decimal("100.00"), Decimal("0.00"), True, "invalid", Decimal("16.00")
            )

    def test_vat_negative_subtotal(self):
        """Test that negative subtotal raises ValueError."""
        with pytest.raises(ValueError, match="Subtotal cannot be negative"):
            calculate_vat(
                Decimal("-100.00"), Decimal("0.00"), True, "percent", Decimal("16.00")
            )

    def test_vat_negative_fees_total(self):
        """Test that negative fees_total raises ValueError."""
        with pytest.raises(ValueError, match="Fees total cannot be negative"):
            calculate_vat(
                Decimal("100.00"), Decimal("-10.00"), True, "percent", Decimal("16.00")
            )

    def test_vat_negative_vat_value(self):
        """Test that negative VAT value raises ValueError when VAT enabled."""
        with pytest.raises(ValueError, match="VAT value cannot be negative"):
            calculate_vat(
                Decimal("100.00"), Decimal("0.00"), True, "percent", Decimal("-16.00")
            )


class TestCalculateSaleTotal:
    """Test cases for full sale calculation."""

    def test_basic_sale_calculation(self):
        """Test basic sale with items, fees, and VAT."""
        items = [
            {"quantity": 2, "unit_price": Decimal("150.00")},
            {"quantity": 1, "unit_price": Decimal("200.00")},
        ]
        fees = [{"fee_value": Decimal("30.00"), "fee_value_type": "fixed"}]

        result = calculate_sale_total(items, fees, True, "percent", Decimal("16.00"))

        # Subtotal: 2*150 + 1*200 = 500
        # Fees: 30
        # Taxable: 530
        # VAT: 530 * 0.16 = 84.80
        # Total: 614.80

        assert result["subtotal"] == Decimal("500.00")
        assert result["fees_total"] == Decimal("30.00")
        assert result["vat_amount"] == Decimal("84.80")
        assert result["vat_rate"] == Decimal("16.00")
        assert result["total"] == Decimal("614.80")

    def test_sale_no_vat(self):
        """Test sale with VAT disabled."""
        items = [{"quantity": 5, "unit_price": Decimal("100.00")}]
        fees = []

        result = calculate_sale_total(items, fees, False, "percent", Decimal("16.00"))

        assert result["subtotal"] == Decimal("500.00")
        assert result["fees_total"] == Decimal("0.00")
        assert result["vat_amount"] == Decimal("0")
        assert result["vat_rate"] is None
        assert result["total"] == Decimal("500.00")

    def test_sale_with_percentage_fee(self):
        """Test sale with percentage-based fee."""
        items = [{"quantity": 1, "unit_price": Decimal("1000.00")}]
        fees = [{"fee_value": Decimal("5.00"), "fee_value_type": "percent"}]

        result = calculate_sale_total(items, fees, False, "percent", Decimal("0.00"))

        # Subtotal: 1000
        # Fee: 5% of 1000 = 50
        # Total: 1050

        assert result["subtotal"] == Decimal("1000.00")
        assert result["fees_total"] == Decimal("50.00")
        assert result["total"] == Decimal("1050.00")

    def test_sale_multiple_fees(self):
        """Test sale with multiple fees."""
        items = [{"quantity": 2, "unit_price": Decimal("150.00")}]
        fees = [
            {"fee_value": Decimal("30.00"), "fee_value_type": "fixed"},
            {"fee_value": Decimal("5.00"), "fee_value_type": "percent"},
        ]

        result = calculate_sale_total(items, fees, False, "percent", Decimal("0.00"))

        # Subtotal: 300
        # Fixed fee: 30
        # Percentage fee: 5% of 300 = 15
        # Total: 345

        assert result["subtotal"] == Decimal("300.00")
        assert result["fees_total"] == Decimal("45.00")
        assert result["total"] == Decimal("345.00")

    def test_sale_empty_items(self):
        """Test that sale with empty items raises ValueError."""
        with pytest.raises((ValueError, TypeError)):
            calculate_sale_total([], [], False, "percent", Decimal("0.00"))

    def test_sale_spec_example(self):
        """Test the spec example from User Story 1 acceptance scenario."""
        # From spec: Panel A (150) x 2 + Battery B (200) x 1 + shipping 30, VAT 16%
        items = [
            {"quantity": 2, "unit_price": Decimal("150.00")},
            {"quantity": 1, "unit_price": Decimal("200.00")},
        ]
        fees = [{"fee_value": Decimal("30.00"), "fee_value_type": "fixed"}]

        result = calculate_sale_total(items, fees, True, "percent", Decimal("16.00"))

        # Subtotal: 500
        # Fees: 30
        # Taxable: 530
        # VAT: 530 * 0.16 = 84.80
        # Total: 614.80

        assert result["subtotal"] == Decimal("500.00")
        assert result["fees_total"] == Decimal("30.00")
        assert result["vat_amount"] == Decimal("84.80")
        assert result["total"] == Decimal("614.80")

    def test_sale_with_all_zero_values(self):
        """Test sale with zero subtotal and fees."""
        items = [{"quantity": 1, "unit_price": Decimal("0.00")}]
        fees = []

        result = calculate_sale_total(items, fees, True, "percent", Decimal("16.00"))

        assert result["subtotal"] == Decimal("0.00")
        assert result["fees_total"] == Decimal("0.00")
        assert result["vat_amount"] == Decimal("0.00")
        assert result["total"] == Decimal("0.00")


class TestEdgeCases:
    """Test edge cases from specification."""

    def test_large_quantity_10000_units(self):
        """Test spec requirement: handle up to 10,000 units."""
        result = calculate_line_total(10000, Decimal("1.50"))
        assert result == Decimal("15000.00")

    def test_price_override_below_base_price(self):
        """Test spec edge case: price override below base price (should be allowed)."""
        # The system allows price_override < base_price with warning
        # This test verifies the calculation works (validation is separate)
        result = calculate_line_total(1, Decimal("50.00"))
        assert result == Decimal("50.00")

    def test_percentage_fee_on_large_subtotal(self):
        """Test percentage fee with large subtotal."""
        result = calculate_fee_amount(Decimal("5.00"), "percent", Decimal("100000.00"))
        assert result == Decimal("5000.00")

    def test_vat_rounding_edge_spec_example(self):
        """Test spec example: 10% VAT on 33.33 should produce 3.33."""
        # Spec: 10% VAT on subtotal of 33.33 must produce 3.33 (ROUND_HALF_UP)
        vat_amount, _ = calculate_vat(
            Decimal("33.33"), Decimal("0.00"), True, "percent", Decimal("10.00")
        )
        assert vat_amount == Decimal("3.33")

    def test_fee_percentage_calculation_spec_example(self):
        """Test spec example: 5% shipping fee on 1000 subtotal = 50.00."""
        result = calculate_fee_amount(Decimal("5.00"), "percent", Decimal("1000.00"))
        assert result == Decimal("50.00")
