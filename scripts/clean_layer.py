import os
import shutil

def clean_layer():
    layer_path = 'layers/python'
    
    # Remove tests
    for root, dirs, files in os.walk(layer_path):
        for d in dirs:
            if d in ['tests', 'test', '__pycache__']:
                shutil.rmtree(os.path.join(root, d))
        
        # Remove .pyc files
        for f in files:
            if f.endswith('.pyc'):
                os.remove(os.path.join(root, f))

if __name__ == '__main__':
    clean_layer() 