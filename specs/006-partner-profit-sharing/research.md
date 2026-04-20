# Research: Real-time Partner Profit from Product Sales

## Tech Stack Context

**Decision**: Use existing Python/FastAPI + TypeScript/Next.js + PostgreSQL stack

**Rationale**: Project already uses this stack per AGENTS.md. No new technologies required.

## Integration Points

### POS Sale Flow Integration

**Decision**: Backend triggers profit calculation via service call after sale confirmation

**Rationale**: Backend is authoritative for all business logic per Constitution Principle VII. The POS service will call partner profit service on sale completion.

### Product-Partner Linking

**Decision**: New `product_assignments` table with foreign keys to products and partners

**Rationale**: Required by Constitution Principle II (PostgreSQL as single source of truth). Simple one-to-one or one-to-none relationship.

### Profit Transaction Storage

**Decision**: New `partner_wallet_transactions` table to record each profit credit

**Rationale**: Required by Constitution Principle I (financial accuracy), IV (immutable records), and VI (data integrity). Each transaction stored with full audit trail.

### Dashboard Data

**Decision**: Backend API returns aggregated profit data; frontend renders only

**Rationale**: Per Constitution Principle II and VII, backend is sole source of truth. Frontend consumes API responses only.

## No Additional Research Needed

All unknowns resolved from:
- Existing project stack (Python/FastAPI/PostgreSQL)
- Existing POS flow pattern for integration
- Existing partner/auth patterns to reuse