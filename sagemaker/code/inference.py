import os
import json
import gzip
import pickle
import numpy as np
from io import BytesIO

def model_fn(model_dir):
    """Load the model and scaler from the compressed files in S3"""
    try:
        print(f"Starting model loading from directory: {model_dir}")
        print(f"Contents of model_dir: {os.listdir(model_dir)}")
        
        # Load the trading model
        model_path = os.path.join(model_dir, 'trading_model.pkl.gz')
        print(f"Loading model from: {model_path}")
        with gzip.open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("Successfully loaded model")
            
        # Load the feature scaler
        scaler_path = os.path.join(model_dir, 'feature_scaler.pkl.gz')
        print(f"Loading scaler from: {scaler_path}")
        with gzip.open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        print("Successfully loaded scaler")
        
        # Verify both components are loaded
        if model is None or scaler is None:
            raise ValueError("Failed to load either model or scaler")
            
        print(f"Model type: {type(model)}")
        print(f"Scaler type: {type(scaler)}")
            
        return {
            'model': model, 
            'scaler': scaler
        }
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Contents of model_dir: {os.listdir(model_dir)}")
        print(f"Full model_dir path: {os.path.abspath(model_dir)}")
        raise

def input_fn(request_body, request_content_type):
    """Parse input data"""
    print(f"Received request with content type: {request_content_type}")
    if request_content_type == 'application/json':
        print(f"Request body: {request_body}")
        data = json.loads(request_body)
        features = np.array(data['features'], dtype=np.float32)
        print(f"Parsed features shape: {features.shape}")
        return features
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model_dict):
    """Make prediction using the loaded model"""
    try:
        print(f"Input data shape: {input_data.shape}")
        
        # Scale the features
        scaled_features = model_dict['scaler'].transform(input_data.reshape(1, -1))
        print(f"Scaled features shape: {scaled_features.shape}")
        
        # Get prediction and probabilities
        prediction = model_dict['model'].predict(scaled_features)
        probabilities = model_dict['model'].predict_proba(scaled_features)
        
        print(f"Prediction: {prediction}")
        print(f"Probabilities shape: {probabilities.shape}")
        
        return {
            'prediction': prediction.tolist(),
            'probabilities': probabilities.tolist()
        }
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        print(f"Error type: {type(e)}")
        raise

def output_fn(prediction, response_content_type):
    """Format the prediction output"""
    print(f"Formatting output with content type: {response_content_type}")
    if response_content_type == 'application/json':
        response = json.dumps(prediction)
        print(f"Response: {response}")
        return response
    else:
        raise ValueError(f"Unsupported content type: {response_content_type}") 