#!/bin/bash

# Check if `uv` is installed; if not, install it
if ! command -v uv &> /dev/null; then
    echo "'uv' is not installed. Installing it now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Make sure that `uv` is indeed installed
if ! command -v uv &> /dev/null; then
    echo "'uv' installation failed. Please install it manually."
    exit 1
fi

sudo $(uv run which python) -m streamlit run dashboard.py
