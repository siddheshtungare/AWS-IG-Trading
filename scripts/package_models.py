import tarfile
import os
import boto3
import io
import gzip
import shutil
import pickle
import joblib

def download_from_s3(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def create_model_tarfile():
    try:
        # S3 information
        bucket = "aws-sam-cli-managed-default-samclisourcebucket-3pncdm36uy1a"
        model_key = "IG-Trading-1/Resources/MLModels/trading_model.joblib"
        scaler_key = "IG-Trading-1/Resources/MLModels/feature_scaler.joblib"
        
        # Create temporary directory
        os.makedirs("temp_models", exist_ok=True)
        
        print("Downloading model files from S3...")
        # Download model files
        model_data = download_from_s3(bucket, model_key)
        scaler_data = download_from_s3(bucket, scaler_key)
        
        print("Loading model objects...")
        # Load the original objects using BytesIO and joblib
        model = joblib.load(io.BytesIO(model_data))
        scaler = joblib.load(io.BytesIO(scaler_data))
        
        print(f"Model type: {type(model)}")
        print(f"Scaler type: {type(scaler)}")
        
        print("Saving model files with compatible protocol...")
        # Save with protocol=2 for better compatibility with Python 3.7
        with gzip.open("temp_models/trading_model.pkl.gz", 'wb') as f:
            pickle.dump(model, f, protocol=2)
        with gzip.open("temp_models/feature_scaler.pkl.gz", 'wb') as f:
            pickle.dump(scaler, f, protocol=2)
        
        print("Copying inference code...")
        # Copy inference code and requirements
        shutil.copy("sagemaker/code/inference.py", "temp_models/inference.py")
        shutil.copy("sagemaker/code/requirements.txt", "temp_models/requirements.txt")
        
        print("Creating tar.gz archive...")
        # Create tar.gz archive
        with tarfile.open("model.tar.gz", "w:gz") as tar:
            tar.add("temp_models", arcname=".")
            
        # Verify archive contents
        print("\nVerifying archive contents:")
        with tarfile.open("model.tar.gz", "r:gz") as tar:
            for member in tar.getmembers():
                print(f"- {member.name} ({member.size} bytes)")
        
        print("Uploading to S3...")
        # Upload to S3
        s3 = boto3.client('s3')
        with open("model.tar.gz", "rb") as f:
            s3.upload_fileobj(f, bucket, "IG-Trading-1/Resources/MLModels/model.tar.gz")
        
        print("Cleaning up...")
        # Cleanup
        os.remove("model.tar.gz")
        shutil.rmtree("temp_models")
        
        print("Successfully created and uploaded model archive")
        
    except Exception as e:
        print(f"Error in create_model_tarfile: {str(e)}")
        if os.path.exists("model.tar.gz"):
            os.remove("model.tar.gz")
        if os.path.exists("temp_models"):
            shutil.rmtree("temp_models")
        raise

if __name__ == "__main__":
    create_model_tarfile() 