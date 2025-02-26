import os
import joblib
import pandas as pd

# Define model directory
MODEL_DIR = "saved_models"

# Load trained models
def load_models():
    """Load all trained models from disk."""
    models = {}
    model_files = ["RandomForest.pkl", "SVM.pkl", "KNN.pkl"]

    for model_file in model_files:
        model_path = os.path.join(MODEL_DIR, model_file)
        if os.path.exists(model_path):
            model_name = model_file.split(".")[0]  # Extract name (without .pkl)
            models[model_name] = joblib.load(model_path)
    
    if not models:
        raise FileNotFoundError("No trained models found in saved_models/")
    
    return models

def predict_stress(df: pd.DataFrame, models):
    """Make predictions using all trained models."""
    predictions = {model_name: model.predict(df).tolist() for model_name, model in models.items()}
    return predictions
