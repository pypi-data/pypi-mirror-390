#!/bin/bash
set -e

echo "Installing dependencies with binary wheels preference..."

# Upgrade pip first
python -m pip install --upgrade pip

# Install asyncpg with binary preference (don't compile from source)
pip install --only-binary=:all: asyncpg==0.29.0 || pip install asyncpg==0.29.0

# Install rest of requirements
pip install -r cli/requirements.txt

echo "Build complete!"
