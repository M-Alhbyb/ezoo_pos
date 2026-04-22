# Research: Customer Accounting System

## Decisions

### 1. Reversal Integration
- **Decision**: Hook into `SaleService.reverse_sale` to create `RETURN` ledger entries.
- **Rationale**: The existing reversal system creates a mirror `Sale` record with `is_reversal=True`. We can either modify `reverse_sale` to call a `CustomerService` method or use a SQLAlchemy event listener (though explicit service calls are preferred for traceability in this project).
- **Alternatives considered**: Manually checking for reversals in the balance derivation query (rejected as it violates the "Explicit over Implicit" principle of storing events in the ledger).

### 2. Balance Derivation Pattern
- **Decision**: Use SQLAlchemy `func.sum` and `case` expressions, similar to `SupplierService`.
- **Rationale**: This pattern is already established in the codebase (Consistency), handles `None` values gracefully with `coalesce`, and is performant for the current scale.
- **Alternatives considered**: Raw SQL (rejected for maintainability), loading all ledger entries and summing in Python (rejected for performance).

### 3. PDF Generation
- **Decision**: Reuse the existing `WeasyPrint` or `ReportLab` logic if found, otherwise use `WeasyPrint` for HTML-to-PDF as it's typically easier to style with the project's existing CSS knowledge.
- **Rationale**: AGENTS.md mentioned these technologies. I will look for a common reporting utility in the codebase.
- **Update**: Found `app.modules.reports` directory; I will check it for existing PDF export patterns.

### 4. Credit Limit Enforcement
- **Decision**: Implement a `check_credit_limit` method in `CustomerService` and call it from `SaleService.create_sale`.
- **Rationale**: Ensures that POS sales are validated against the derived balance + new sale total before persistence.

## Rationale for Dependencies
- **FastAPI/SQLAlchemy**: Core tech stack.
- **Decimal**: Requirement for financial accuracy.
- **Pydantic**: Standard for input validation.

## Best Practices
- **Atomic Transactions**: Ensure ledger entry creation is wrapped in the same transaction as the sale/payment.
- **Pagination**: All ledger listing APIs must support pagination to handle customers with many transactions.
