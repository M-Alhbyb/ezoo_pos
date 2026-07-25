#!/usr/bin/env bash
# bump-version.sh — bump version across all package.json files and create a git tag.
#
# Usage:
#   ./scripts/bump-version.sh 1.1.0
#
# Updates:
#   - electron/package.json          (version)
#   - backend/app/core/config.py     (app_version)
#   - frontend/package.json          (version — optional, keep in sync)
#
# Then commits and tags v<version>.

set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"
TAG="v${VERSION}"

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: version must be semver (e.g. 1.2.3)" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Bumping to $VERSION ..."

# ── electron/package.json ──────────────────────────────────────────────
ELECTRON_PKG="$REPO_ROOT/electron/package.json"
if [[ -f "$ELECTRON_PKG" ]]; then
  python3 -c "
import json, sys
with open(sys.argv[1], 'r') as f:
    pkg = json.load(f)
pkg['version'] = sys.argv[2]
with open(sys.argv[1], 'w') as f:
    json.dump(pkg, f, indent=2)
    f.write('\n')
" "$ELECTRON_PKG" "$VERSION"
  echo "  ✓ electron/package.json"
fi

# ── frontend/package.json ──────────────────────────────────────────────
FRONTEND_PKG="$REPO_ROOT/frontend/package.json"
if [[ -f "$FRONTEND_PKG" ]]; then
  python3 -c "
import json, sys
with open(sys.argv[1], 'r') as f:
    pkg = json.load(f)
pkg['version'] = sys.argv[2]
with open(sys.argv[1], 'w') as f:
    json.dump(pkg, f, indent=2)
    f.write('\n')
" "$FRONTEND_PKG" "$VERSION"
  echo "  ✓ frontend/package.json"
fi

# ── backend/app/core/config.py ─────────────────────────────────────────
CONFIG_PY="$REPO_ROOT/backend/app/core/config.py"
if [[ -f "$CONFIG_PY" ]]; then
  python3 -c "
import re, sys
path = sys.argv[1]
ver  = sys.argv[2]
with open(path, 'r') as f:
    content = f.read()
content = re.sub(
    r\"app_version:\\s*str\\s*=\\s*['\\\"][^'\\\"]+['\\\"]\",
    f\"app_version: str = '{ver}'\",
    content,
)
with open(path, 'w') as f:
    f.write(content)
" "$CONFIG_PY" "$VERSION"
  echo "  ✓ backend/app/core/config.py"
fi

# ── git commit + tag ───────────────────────────────────────────────────
cd "$REPO_ROOT"
git add "$ELECTRON_PKG" "$FRONTEND_PKG" "$CONFIG_PY"
git commit -m "release: bump version to $VERSION"
git tag -a "$TAG" -m "Release $VERSION"
echo ""
echo "Done.  Push with:"
echo "  git push origin main $TAG"
