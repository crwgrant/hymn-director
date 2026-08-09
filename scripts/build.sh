#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Ensuring bundled database exists..."
uv run init-db

echo "Building Hymn Director..."
uv run pyinstaller --noconfirm hymn-director.spec

echo "Build complete. Output is in dist/"
