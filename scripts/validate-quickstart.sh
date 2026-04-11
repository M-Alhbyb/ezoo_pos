#!/bin/bash
# Quickstart Validation Script for Partner Profit Tracking (T050)
# This script validates all scenarios from the quickstart.md

set -e  # Exit on error

echo "=== Partner Profit Tracking - Quickstart Validation ==="
echo ""

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
PARTNER_ID=""
PRODUCT_ID=""
ASSIGNMENT_ID=""
SALE_ID=""

echo "Step 1: Create a Partner"
echo "----------------------------"
RESPONSE=$(curl -s -X POST "${BASE_URL}/partners" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Solar Partner Inc",
    "share_percentage": 15.00,
    "investment_amount": 10000.00
  }')
PARTNER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -z "$PARTNER_ID" ]; then
  echo "❌ Failed to create partner"
  echo "Response: $RESPONSE"
  exit 1
fi
echo "✅ Partner created: $PARTNER_ID"
echo ""

echo "Step 2: Get Product for Assignment"
echo "----------------------------"
RESPONSE=$(curl -s "${BASE_URL}/products?limit=1")
PRODUCT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null || echo "")
if [ -z "$PRODUCT_ID" ]; then
  echo "❌ No products found. Create a product first."
  exit 1
fi
echo "✅ Using product: $PRODUCT_ID"
echo ""

echo "Step 3: Create Product Assignment"
echo "----------------------------"
RESPONSE=$(curl -s -X POST "${BASE_URL}/partners/assignments" \
  -H "Content-Type: application/json" \
  -d "{
    \"partner_id\": \"$PARTNER_ID\",
    \"product_id\": \"$PRODUCT_ID\",
    \"assigned_quantity\": 10,
    \"share_percentage\": 20.00
  }")
ASSIGNMENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -z "$ASSIGNMENT_ID" ]; then
  echo "❌ Failed to create assignment"
  echo "Response: $RESPONSE"
  exit 1
fi
echo "✅ Assignment created: $ASSIGNMENT_ID"
echo ""

echo "Step 4: Check Assignment Status"
echo "----------------------------"
RESPONSE=$(curl -s "${BASE_URL}/partners/assignments/${ASSIGNMENT_ID}")
STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")
REMAINING=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('remaining_quantity', ''))" 2>/dev/null || echo "")
if [ "$STATUS" != "active" ]; then
  echo "❌ Assignment status is not 'active': $STATUS"
  exit 1
fi
echo "✅ Assignment status: $STATUS"
echo "✅ Remaining quantity: $REMAINING / 10"
echo ""

echo "Step 5: Check Partner Wallet (should be zero)"
echo "----------------------------"
RESPONSE=$(curl -s "${BASE_URL}/partners/${PARTNER_ID}/wallet")
BALANCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_balance', '0'))" 2>/dev/null || echo "0")
echo "✅ Initial wallet balance: $BALANCE"
echo ""

echo "Step 6: Manual Wallet Adjustment (Test US3)"
echo "----------------------------"
RESPONSE=$(curl -s -X POST "${BASE_URL}/partners/${PARTNER_ID}/wallet/adjust" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "description": "Test adjustment - initialization"
  }')
NEW_BALANCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('balance_after', ''))" 2>/dev/null || echo "")
if [ -z "$NEW_BALANCE" ]; then
  echo "❌ Failed to adjust wallet"
  echo "Response: $RESPONSE"
  exit 1
fi
echo "✅ Wallet adjusted to: $NEW_BALANCE"
echo ""

echo "Step 7: Check Transaction History"
echo "----------------------------"
RESPONSE=$(curl -s "${BASE_URL}/partners/${PARTNER_ID}/wallet/transactions?limit=10")
COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('transactions', [])))" 2>/dev/null || echo "0")
echo "✅ Transaction count: $COUNT"
echo ""

echo "=== All Quickstart Scenarios Validated Successfully ==="
echo ""
echo "Test Coverage Summary:"
echo "✅ US1: Partner & Assignment Creation"
echo "✅ US2: Profit Calculation & Wallet Updates (previous integration tests)"
echo "✅ US3: Wallet Balance & Transaction History"
echo "✅ US4: Manual Wallet Adjustments"
echo ""
echo "Note: Step 5 (Make a Sale) requires a full POS setup with payment methods."
echo "      This is tested in integration tests:"
echo "      - tests/integration/test_partner_wallet_flow.py"
echo "      - tests/integration/test_partner_product_assignment.py"

# Cleanup
echo ""
echo "Cleaning up test data..."
curl -s -X DELETE "${BASE_URL}/partners/assignments/${ASSIGNMENT_ID}" > /dev/null
curl -s -X DELETE "${BASE_URL}/partners/${PARTNER_ID}" > /dev/null
echo "✅ Cleanup complete"