#!/bin/bash

# Set up layer directory
LAYER_DIR="layers/ml_dependencies"
PYTHON_DIR="$LAYER_DIR/python"

# Clean up existing files
rm -rf $PYTHON_DIR
mkdir -p $PYTHON_DIR

# Install dependencies
pip install -r $LAYER_DIR/requirements.txt -t $PYTHON_DIR

# Clean up unnecessary files
python scripts/clean_layer.py

# Remove cached files
find $PYTHON_DIR -type d -name "__pycache__" -exec rm -rf {} +
find $PYTHON_DIR -type f -name "*.pyc" -delete 