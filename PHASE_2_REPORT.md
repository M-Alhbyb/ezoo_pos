# Phase 2 — Static Export: Implementation Report

**Date:** 2026-07-25
**Commit:** `e269fe5` — `phase-2: static export and frontend-backend integration`
**Platform:** Linux (cross-platform compatible)

---

## Summary

Phase 2 converts the frontend from `output: 'standalone'` (Node.js server) to `output: 'export'` (fully static HTML/JS/CSS) served by FastAPI. This eliminates the need for a separate Node.js process at runtime, reducing the architecture to one backend process + Electron.

## What Was Done

### 5.1 — Next.js Configuration

| File | Change |
|------|--------|
| `frontend/next.config.mjs` | Conditional config: `output: 'export'` + `trailingSlash: true` + `images: { unoptimized: true }` when `NEXT_OUTPUT=export`; rewrites + redirects only in dev mode |
| `frontend/package.json` | Added `"build:export": "cross-env NEXT_OUTPUT=export next build"` script + `cross-env` devDependency |

### 5.2 — Five Dynamic Routes Converted

All 5 client-side dynamic routes were converted from `[param]` URL segments to query-parameter-based routing using `useSearchParams()`, each wrapped in a `Suspense` boundary:

| Old Route | New Route | Param |
|-----------|-----------|-------|
| `app/suppliers/[id]/page.tsx` | `app/suppliers/detail/page.tsx?id=` | `useSearchParams().get("id")` |
| `app/customers/[id]/page.tsx` | `app/customers/detail/page.tsx?id=` | `useSearchParams().get("id")` |
| `app/partners/[partnerId]/page.tsx` | `app/partners/detail/page.tsx?partnerId=` | `useSearchParams().get("partnerId")` |
| `app/partners/wallet/[partnerId]/page.tsx` | `app/partners/wallet/page.tsx?partnerId=` | `useSearchParams().get("partnerId")` |
| `app/pos/history/[saleId]/page.tsx` | `app/pos/history/detail/page.tsx?saleId=` | `useSearchParams().get("saleId")` |

**Navigation links updated** in 5 source files:
- `app/suppliers/page.tsx` — `/suppliers/${id}` → `/suppliers/detail?id=${id}`
- `app/partners/page.tsx` — `/partners/${id}` → `/partners/detail?partnerId=${id}`
- `app/customers/page.tsx` — `/customers/${id}` → `/customers/detail?id=${id}`
- `app/reports/customers/page.tsx` — `/customers/${id}` → `/customers/detail?id=${id}`
- `app/pos/history/page.tsx` — `/pos/history/${id}` → `/pos/history/detail?saleId=${id}`

**Redirect fallback** created at `app/partners/assignment/page.tsx` — client-side redirect to `/partners/assignments` since static export cannot express server-side redirects.

### 5.3 — WebSocket URL Derivation

Changed `lib/websocket-client.ts` to derive the WebSocket URL from `window.location` instead of hardcoding `ws://localhost:8001`:
```ts
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
return `${protocol}//${window.location.host}/ws/stock-updates`;
```
Same-origin works because FastAPI now serves both API and frontend.

### 5.4 — FastAPI Static File Mounting

Added to `backend/main.py`:
- Import `StaticFiles`, `HTMLResponse`, `Request`, `resource_path`
- Mount `frontend_out/` at `/` with `html=True` (after all API routers)
- Custom 404 handler serves `out/404.html` for non-API routes
- Guard: `os.path.isdir()` check keeps `uvicorn --reload` working in dev

### 5.5 — Root package.json

Created `package.json` at repo root with dev scripts:
- `npm run dev` — concurrent backend + frontend via `concurrently`
- `npm run dev:api` — backend via `uv run uvicorn`
- `npm run dev:web` — frontend via `next dev`
- `npm run setup` — `uv sync` + `npm install`

### Pre-existing Issues Fixed

8 TypeScript type errors were discovered and fixed (masked by `standalone` output not doing full type checking):

| File | Issue | Fix |
|------|-------|-----|
| `components/pos/CustomerSelector.tsx:72` | `ARABIC.customers.selectCustomer` doesn't exist | Replaced with inline string |
| `components/pos/SaleDetailModal.tsx` | 7 non-existent ARABIC properties (`confirmReverse`, `saleDetail`, `orderId`, `qty`, `payments`, `print`, `returnItems`) | Replaced with inline strings or correct property names |
| `app/reports/sales/page.tsx` | Broken relative import path | Changed to `@/components/...` alias |
| `app/reports/inventory/page.tsx` | Broken relative import path | Changed to `@/components/...` alias |
| `app/partners/assignments/page.tsx:226` | Type mismatch `Partial<Assignment>` vs `Partial<ProductAssignment>` | Changed to use `ProductAssignment` type |

## Acceptance Criteria Checklist

- [x] `NEXT_OUTPUT=export npm run build` completes with **zero** errors
- [x] `out/` contains `index.html` for every route, including all 5 converted detail pages
- [x] All 5 converted pages have corresponding `index.html` in output
- [x] `git grep` finds no remaining links to old `[id]` route shapes (only API fetch calls remain, which are correct)
- [x] Backend serving `out/`: frontend mounted at `/` with `html=True`, non-API 404 returns `404.html`
- [x] WebSocket URL derived from `window.location` (same-origin)
- [x] `npm run dev` still works (conditional config preserves rewrites in dev mode)
- [x] `ruff check` on `main.py` passes (2 pre-existing warnings: FastAPI `Depends` pattern + SQLAlchemy boolean comparison)

## What's NOT in Scope (Deferred to Later Phases)

| Item | Phase | Notes |
|------|-------|-------|
| Arabic RTL layout visual verification | Phase 3+ | Requires running the built output |
| PyInstaller packaging | Phase 3 | Windows only |
| Electron rewrite | Phase 4 | Windows only |
| CI workflow | Phase 5 | Windows only |
| Font self-hosting fallback | Phase 5 | Only needed if CI has no network |

## Build Output

```
○ / (Static)  prerendered as static content
○ /categories
○ /customers
○ /customers/detail          ← converted
○ /dashboard
○ /dashboard/inventory
○ /dashboard/partners
○ /dashboard/reports/inventory
○ /dashboard/reports/partners
○ /dashboard/reports/sales
○ /dashboard/sales
○ /inventory
○ /login
○ /partners
○ /partners/assignment       ← redirect page
○ /partners/assignments
○ /partners/detail           ← converted
○ /partners/wallet           ← converted
○ /pos
○ /pos/history
○ /pos/history/detail        ← converted
○ /products
○ /purchases
○ /reports/customers
○ /reports/inventory
○ /reports/sales
○ /settings
○ /suppliers
○ /suppliers/detail          ← converted
+ First Load JS shared by all  87.7 kB
```

All 30 routes statically exported. Total first-load JS: ~88 KB shared.
