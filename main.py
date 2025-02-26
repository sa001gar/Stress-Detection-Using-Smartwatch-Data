from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import joblib

# Load trained models
MODEL_DIR = "saved_models"
MODEL_FILES = ["RandomForest.pkl", "SVM.pkl", "KNN.pkl"]
MODELS = {}

for model_name in MODEL_FILES:
    model_key = model_name.split(".")[0]
    try:
        MODELS[model_key] = joblib.load(os.path.join(MODEL_DIR, model_name))
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")

def predict_stress(model, data):
    return model.predict(data)

app = FastAPI(title="Stress Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = "./data/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a CSV file for stress prediction.
    
    Args:
        file (UploadFile): CSV file with required columns
        
    Returns:
        JSONResponse: Predicted stress levels including ID, Name, and Age
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    file_path = os.path.join(UPLOAD_DIR, f"temp_{os.urandom(8).hex()}.csv")
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        
        with open(file_path, "wb") as f:
            f.write(contents)

        data = pd.read_csv(file_path)
        
        # Validate and preprocess data
        required_columns = [
            "ID", "Person_Name", "Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level", 
            "Blood_Pressure", "Heart_Rate", "Daily_Steps"
        ]
        
        if not all(col in data.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain all required columns: {', '.join(required_columns)}")
        
        if data.empty:
            raise HTTPException(status_code=400, detail="The CSV file contains no data.")
        
        # Split Blood Pressure into Systolic and Diastolic
        try:
            data[["Systolic_BP", "Diastolic_BP"]] = data["Blood_Pressure"].str.split("/", expand=True).astype(int)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing blood pressure values: {str(e)}")
        
        data = data.drop(columns=["Blood_Pressure"])
        
        # Select relevant features
        X = data[["Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level", "Systolic_BP", "Diastolic_BP", "Heart_Rate", "Daily_Steps"]]
        
        # Predict using RandomForest by default
        model = MODELS.get("RandomForest")
        if model is None:
            raise HTTPException(status_code=500, detail="RandomForest model not found.")
        
        predictions = predict_stress(model, X)
        
        
        response = [
            {
                "ID": int(data.loc[idx, "ID"]),
                "Person_Name": data.loc[idx, "Person_Name"],
                "Age": int(data.loc[idx, "Age"]),
                "Stress_Level": int(pred),
            }
            for idx, pred in enumerate(predictions)
        ]
        
        return JSONResponse(content={"data": response})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {file_path}: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
