from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os

# Import custom modules with error handling
try:
    from models.model import predict_stress
    from utils.helpers import clean_csv_data, validate_csv_columns
except ImportError as e:
    raise ImportError(f"Required modules not found: {str(e)}. Ensure 'models' and 'utils' packages are properly installed.")

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

        # Read the CSV with error handling
        try:
            data = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            raise HTTPException(status_code=400, detail="The CSV file is empty.")
        except pd.errors.ParserError:
            raise HTTPException(status_code=400, detail="Invalid CSV format.")

        # Validate columns
        required_columns = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
        if not validate_csv_columns(data, required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain all required columns: {', '.join(required_columns)}"
            )

        if data.empty:
            raise HTTPException(status_code=400, detail="The CSV file contains no data.")

        # Clean the data
        try:
            cleaned_data = clean_csv_data(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error cleaning data: {str(e)}")

        # Select relevant features
        feature_columns = ["C3", "C4", "C5", "C6", "C7", "C8"]
        input_data = cleaned_data[feature_columns]

        # Predict stress levels
        try:
            predictions = predict_stress(input_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error predicting stress levels: {str(e)}")

        # Format the response
        try:
            response = [
                {
                    "person_id": str(row["C1"]),
                    "age": str(row["C2"]),
                    "stress_level": float(pred)
                }
                for row, pred in zip(cleaned_data.to_dict(orient="records"), predictions)
            ]
            
            return JSONResponse(content={"data": response})
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error formatting response: {str(e)}")

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
    """Health check endpoint to verify API is running"""
    return {"status": "healthy"}
