#!/usr/bin/env bash

# Verify deps
if ! command -v uv &> /dev/null; then
    echo "[ERR] uv not found" >&2
    exit 1
fi

# Set up venv
if [ ! -d .publish ]; then
  uv venv .publish
fi
source .publish/bin/activate
uv pip install -r publish.txt

# Publish
python3 -m build
python3 -m twine upload dist/*

# Clean up
deactivate
