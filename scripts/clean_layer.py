import os
import shutil

def clean_layer(layer_path):
    """Remove unnecessary files from the layer to reduce size"""
    # Remove tests
    for root, dirs, files in os.walk(layer_path):
        for d in dirs:
            if d in ['tests', 'test', '__pycache__', 'docs']:
                shutil.rmtree(os.path.join(root, d))
        
        for f in files:
            if f.endswith(('.pyc', '.pyo', '.pyd', '.so', '.html', '.md')):
                os.remove(os.path.join(root, f))

if __name__ == "__main__":
    layer_path = "layers/ml_dependencies/python"
    clean_layer(layer_path) 