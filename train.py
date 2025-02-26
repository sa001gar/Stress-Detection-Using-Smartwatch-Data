import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Define the directory to save models
MODEL_DIR = "saved_models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Step 2: Read CSV and prepare train-test data
def prepare_train_test_data():
    # Read the CSV file
    df = pd.read_csv("final_dataset.csv")
    
    # Rename columns based on the dataset description
    df.columns = [
        "Person_Id", "Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level",
        "Blood_Pressure", "Heart_Rate", "Daily_Steps", "Stress_Level"
    ]
    
    # Split Blood Pressure into Systolic and Diastolic
    df[["Systolic_BP", "Diastolic_BP"]] = df["Blood_Pressure"].str.split("/", expand=True).astype(int)

    # Select relevant features (excluding original Blood_Pressure)
    X = df[["Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level", "Systolic_BP", "Diastolic_BP", "Heart_Rate", "Daily_Steps"]]
    y = df["Stress_Level"]
    
    # Split into train and test datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

# Step 3: Train models and save them
def train_and_save_model(model, model_name, X_train, y_train):
    model.fit(X_train, y_train)
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    joblib.dump(model, model_path)
    print(f"{model_name} model saved as {model_path}")
    return model

# Step 4: Plot confusion matrix
def plot_confusion_matrix(cm, model_name):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"{model_name} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

# Step 5: Test the model
def test_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{model_name} Test Accuracy: {accuracy:.2f}")
    
    # Validate predictions
    unique_preds = set(y_pred)
    expected_labels = set(y_test.unique())
    
    if unique_preds.issubset(expected_labels):
        print(f"{model_name} predictions are valid.")
    else:
        print(f"⚠️ {model_name} produced unexpected values: {unique_preds}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(cm, model_name)

def main():
    # Step 2: Prepare train-test data
    X_train, X_test, y_train, y_test = prepare_train_test_data()

    # Step 3: Models to evaluate
    models = {
        "RandomForest": RandomForestClassifier(random_state=42),
        "SVM": SVC(kernel="linear", random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5),
    }

    for model_name, model in models.items():
        print(f"\n🔹 Training {model_name}...")
        model = train_and_save_model(model, model_name, X_train, y_train)
        
        # Test the trained model
        test_model(model, X_test, y_test, model_name)

if __name__ == "__main__":
    main()
