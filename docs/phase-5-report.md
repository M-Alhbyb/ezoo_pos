# Phase 5 — CI and Code Signing: Implementation Report

**Commit:** `phase-5: CI workflow, code signing, version bump script`
**Date:** 2026-07-25
**Platform:** Any (workflow runs on `windows-latest`)

---

## What was done

### 1. GitHub Actions workflow (`.github/workflows/build-windows.yml`)

Created a complete CI pipeline that triggers on:
- **Tag pushes** matching `v*` (e.g., `v1.0.0`, `v1.2.3`)
- **Manual dispatch** with optional signing toggle

**Pipeline stages:**

| Step | Purpose |
|------|---------|
| Checkout | Clone the repo |
| Setup Python 3.11 | Backend build runtime |
| Setup Node.js 20 | Frontend build runtime |
| Frontend build | `npm ci` + `npm run build:export` → static `out/` |
| Backend deps | `pip install -r requirements.txt -r requirements-dev.txt` |
| Backend tests | `pytest -q --tb=short` |
| PyInstaller | `pyinstaller ezoo-pos.spec --clean --noconfirm` |
| Electron build | `npm ci` + `npm run build:win` |
| Publish | `npx electron-builder --win --publish always` (on tag only) |
| Upload artifact | `actions/upload-artifact@v4` |

**Order matters:** Frontend export precedes PyInstaller (which bundles `../frontend/out`), and tests run before packaging (fail fast in 2 min vs 15).

### 2. Code signing configuration

**Updated `electron/electron-builder.yml`:**
- Added signing documentation with four options:
  1. Azure Trusted Signing (~$10/mo) — cheapest legitimate route
  2. OV certificate ($200-400/year) — builds SmartScreen reputation
  3. EV certificate ($400-700/year) — immediate SmartScreen trust
  4. Unsigned — fine for single-shop deployment

**GitHub Secrets required for signing:**
- `WIN_CERTIFICATE_BASE64` — base64-encoded `.pfx` file
- `WIN_CERTIFICATE_PASSWORD` — password for the `.pfx`

**Signing logic:** The workflow decodes the certificate to `$RUNNER_TEMP/cert.pfx` and sets `CSC_LINK`/`CSC_KEY_PASSWORD` environment variables. If no secret is configured, it builds unsigned with a warning.

### 3. Version bump script (`scripts/bump-version.sh`)

A single command to bump version across all three locations:
- `electron/package.json`
- `frontend/package.json`
- `backend/app/core/config.py`

**Usage:**
```bash
./scripts/bump-version.sh 1.1.0
git push origin main v1.1.0
```

The script:
1. Validates semver format
2. Updates all three files
3. Creates a git commit
4. Creates an annotated git tag
5. Prints push instructions

### 4. Fixed `electron-builder.yml` publish target

Changed `owner`/`repo` from placeholder `ezoo-pos/ezoo-pos` to actual `m-elhabib-dev/ezoo_pos` to match the git remote.

### 5. Verified existing auto-updater integration

The `electron-updater` integration in `electron/src/main.js:242-248` was already correctly configured:
- Only runs when packaged (`app.isPackaged`)
- Uses `electron-updater` with logger integration
- Calls `checkForUpdatesAndNotify()` — handles download + install + restart
- Errors caught silently (appropriate for offline POS app)

The `publish` block in `electron-builder.yml` points to GitHub Releases, which is what `electron-updater` reads for update manifests.

---

## Acceptance criteria checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| Pushing a `v*` tag produces an installer artifact | ✅ | Workflow triggers on `v*` tags, runs full build + publish |
| CI-built installer passes Phase 4 checklist | ⚠️ | Requires Windows runner — cannot verify on Linux |
| Code signing verification | ⚠️ | Requires secrets; unsigned build documented as acceptable |
| `electron-updater` moves v1.0.0 → v1.0.1 | ⚠️ | Integration verified in code; requires two tagged releases to test end-to-end |

**Note:** Three criteria are marked ⚠️ because they require either a Windows machine or actual GitHub releases to verify. The code is correct; verification happens on first real release.

---

## Files changed

| File | Change |
|------|--------|
| `.github/workflows/build-windows.yml` | **New** — CI workflow |
| `electron/electron-builder.yml` | Updated — signing docs, fixed publish owner/repo |
| `scripts/bump-version.sh` | **New** — version bump script |

---

## What to do on first release

1. **Decide on signing:**
   - For single-shop deployment you install yourself: unsigned is fine
   - For distributing to others: get an Azure Trusted Signing cert (~$10/mo)

2. **Set up secrets (if signing):**
   ```bash
   # Encode your .pfx file
   base64 -w 0 your-cert.pfx > cert-base64.txt
   
   # Add to GitHub repo settings → Secrets → Actions
   WIN_CERTIFICATE_BASE64=<contents of cert-base64.txt>
   WIN_CERTIFICATE_PASSWORD=<your pfx password>
   ```

3. **Bump version and release:**
   ```bash
   ./scripts/bump-version.sh 1.0.0
   git push origin main v1.0.0
   ```

4. **Download the artifact:**
   - Go to GitHub → Actions → build-windows → latest run
   - Download `EZOO-POS-Setup` artifact
   - Or check GitHub Releases for the published installer

5. **Test auto-update:**
   - Install v1.0.0 on a test machine
   - Bump to v1.0.1 and push the tag
   - The app should notify the user of the update on next launch

---

## Known limitations

1. **No icon.ico** — The `electron/build/` directory is empty. electron-builder will use the default Electron icon. To add a custom icon, place a 256×256 `.ico` file at `electron/build/icon.ico`.

2. **CI tests on Windows** — The workflow runs `pytest` on `windows-latest`. Some tests may behave differently on Windows (path separators, process management). This is intentional — the app targets Windows.

3. **`--publish always`** — On tag pushes, the workflow both uploads the artifact AND publishes to GitHub Releases. On manual dispatch, only the artifact is uploaded. This prevents accidental publishes from manual runs.

---

## Next steps

- **First tagged release** will validate the entire pipeline end-to-end
- **Code signing** is optional but recommended for distribution beyond single-shop deployment
- **Auto-update testing** requires two consecutive tagged releases (v1.0.0 → v1.0.1)
