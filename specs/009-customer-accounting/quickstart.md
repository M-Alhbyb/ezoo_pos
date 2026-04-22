# Quickstart: Customer Accounting

## Setup
1. Run migrations: `alembic upgrade head`
2. Backend starts automatically with `npm run dev` (running uvicorn).

## Common Tasks

### 1. Register a New Customer
Use the sidebar navigation to **Customers** and click **Add Customer**. Set a credit limit if they are allowed to buy on credit.

### 2. Perform a Credit Sale
In the **POS** screen:
1. Select items.
2. Search and select a **Customer** from the dropdown.
3. If the sale exceeds the credit limit, a warning will appear. Click **Confirm** to proceed.
4. Complete the sale. The balance will update instantly.

### 3. Record a Payment
Go to **Customers > [Customer Name]** and click **Add Payment**. Enter the amount and method. This reduces the outstanding balance.

### 4. View Statement
From the customer detail page, view the **Ledger** table. You can filter by date and use the **Print Statement** button to generate a PDF.

## Troubleshooting
- **Balance mismatch**: Ensure all sales/returns have corresponding ledger entries. The balance is derived dynamically.
- **Credit limit not enforcing**: Verify the `customer_id` is being passed correctly in the POS API request.
