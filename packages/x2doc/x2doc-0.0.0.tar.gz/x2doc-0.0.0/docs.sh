#!/usr/bin/env bash

# Set up venv
if [ ! -d .docs ]; then
  uv venv .docs
fi
source .docs/bin/activate
uv pip install -r docs.txt

# Build
sphinx-build -b html docs docs/out

# Clean up
deactivate
