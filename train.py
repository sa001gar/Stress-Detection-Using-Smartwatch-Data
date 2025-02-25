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

    # Features (X) and Target (y)
    X = df[["C3", "C4", "C5", "C6", "C7", "C8"]]
    y = df["C9"]

    # Convert categorical variables if necessary
    X = pd.get_dummies(X)

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
def plot_confusion_matrix(cm, model_name, class_names):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title(f"{model_name} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

def main():
    # Step 2: Prepare train-test data
    X_train, X_test, y_train, y_test = prepare_train_test_data()

    # Step 3: Models to evaluate
    models = {
        "RandomForest": RandomForestClassifier(random_state=42),
        "SVM": SVC(kernel="linear", random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5),
    }

    # Class names for the confusion matrix
    class_names = ["Low Stress", "Medium Stress", "High Stress"]

    # Train and evaluate each model
    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model = train_and_save_model(model, model_name, X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"{model_name} Accuracy: {accuracy:.2f}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plot_confusion_matrix(cm, model_name, class_names)

if __name__ == "__main__":
    main()
