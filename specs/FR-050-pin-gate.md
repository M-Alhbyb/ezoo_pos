# FR-050: PIN Gate Authentication

## Status
**Proposed** — replaces email/password login page removed in step-2b.

## Motivation
EZOO POS is a single-user/single-station desktop app (Electron). Email/password login is
misleading — there is no network auth, no multi-user RBAC, and the backend is localhost-only.
The login page displayed hardcoded credentials in source. Removing it is a security requirement.

## Design

### User experience
1. On app launch, the POS screen opens directly (no login form).
2. A thin PIN overlay appears on top of the POS screen when the user taps **Settings** or
   **Partners** (anything that modifies financial config).
3. Overlay: 4-digit numeric keypad, "Enter" button, "Cancel" button.
4. PIN is validated against a bcrypt hash stored in the `settings` table
   (`key = "pin_gate_hash"`).
5. On success: overlay dismisses, original navigation proceeds.
6. On failure: shake animation, "Wrong PIN" message, retry allowed.
7. PIN is cached in memory for 5 minutes after successful entry (no re-prompt within window).

### Backend
- `POST /api/auth/pin/verify` — body: `{ "pin": "1234" }` — returns `{ "ok": true }` or 401.
- No JWT. Session is purely client-side (5-minute in-memory cache).
- `GET /api/auth/pin/status` — returns `{ "configured": true/false }` — used by frontend to
  decide whether to show PIN overlay at all (if no PIN is set, skip overlay entirely).
- `PUT /api/auth/pin` — body: `{ "current_pin": "1234", "new_pin": "5678" }` — for initial
  setup and rotation. Requires current_pin if one is already set.

### Database
- `settings` table, key `pin_gate_hash`, value: bcrypt hash of 4-digit PIN.
- No new tables.

### Frontend
- `PinGateOverlay` component: modal overlay with numeric keypad.
- `usePinGate()` hook: returns `{ isVerified, verify, isShowing, show, hide }`.
- `isVerified` resets to `false` after 5-minute timeout.
- Settings and Partners pages wrap their content in `<PinGateOverlay>`.

## Acceptance Criteria
- [ ] No `/login` route exists in the frontend.
- [ ] No email/password fields anywhere in the UI.
- [ ] App opens directly to POS screen.
- [ ] Settings page shows PIN overlay on first visit.
- [ ] PIN overlay accepts 4 digits, validates against backend.
- [ ] Wrong PIN shows error with shake animation.
- [ ] Correct PIN allows access for 5 minutes.
- [ ] PIN can be set/changed from Settings page.
- [ ] If no PIN is configured, overlay is skipped entirely (open access).
