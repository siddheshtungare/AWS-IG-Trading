#!/bin/bash

# Function to build a layer
build_layer() {
    local layer_name=$1
    local layer_dir="layers/${layer_name}_layer"
    local python_dir="${layer_dir}/python"

    echo "Building ${layer_name} layer..."
    
    # Clean up existing files
    rm -rf ${python_dir}
    mkdir -p ${python_dir}

    # Install dependencies
    pip install -r ${layer_dir}/requirements.txt -t ${python_dir}

    # Clean up unnecessary files
    find ${python_dir} -type d -name "__pycache__" -exec rm -rf {} +
    find ${python_dir} -type f -name "*.pyc" -delete
    find ${python_dir} -type d -name "tests" -exec rm -rf {} +
    find ${python_dir} -type d -name "docs" -exec rm -rf {} +
}

# Build each layer
build_layer "numpy"
build_layer "pandas"
build_layer "sklearn"

echo "All layers built successfully!" 