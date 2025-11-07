#!/bin/bash
# Build JAX-MD documentation locally
# Mimics ReadTheDocs build process

set -e

echo "Building JAX-MD documentation..."
echo "=================================="

# Set environment variables for JAX
export READTHEDOCS=1
export JAX_PLATFORMS=cpu
export JAX_ENABLE_X64=1

# Copy examples (like ReadTheDocs pre_build)
echo "Copying examples..."
cp -r examples docs/

# Convert to notebooks (without execution)
echo "Converting examples to notebooks..."
uv run jupytext --to notebook docs/examples/*.py
uv run jupytext --to notebook docs/examples/units/*.py

# Remove Python files
rm docs/examples/*.py
rm docs/examples/units/*.py

# Build docs with Sphinx (nbsphinx will execute notebooks here)
echo "Building Sphinx documentation (nbsphinx will execute notebooks)..."
uv run sphinx-build docs docs/_build

# Post-build: Copy notebooks for download
echo "Copying notebooks to output..."
mkdir -p docs/_build/html/notebooks
mkdir -p docs/_build/html/notebooks/units
cp docs/examples/*.ipynb docs/_build/html/notebooks/
cp docs/examples/units/*.ipynb docs/_build/html/notebooks/units/

# Clean up
rm -rf docs/examples

echo ""
echo "=================================="
echo "✓ Documentation built successfully!"
echo "=================================="
echo ""
echo "To view: xdg-open docs/_build/index.html"
echo "Or run: python3 -m http.server 8000 -d docs/_build"
echo ""
echo "Notebooks available at: docs/_build/html/notebooks/"
