import joblib
import pandas as pd
from pathlib import Path

# Locate saved ML model
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "machinelearning-workflow"
    / "models"
    / "customer_churn_model.pkl"
)

# Load trained model
model = joblib.load(MODEL_PATH)

print("Customer churn model loaded successfully!")


# Predict customer churn
def predict_customer(customer_data):

    # Convert input into DataFrame
    customer_df = pd.DataFrame([customer_data])

    # Generate prediction
    prediction = model.predict(customer_df)[0]

    # Get churn probability
    probability = model.predict_proba(customer_df)[0][1]

    # Determine risk level
    if probability < 0.30:
        risk = "Low"

    elif probability < 0.60:
        risk = "Medium"

    else:
        risk = "High"

    return {
        "prediction": "Yes" if prediction == 1 else "No",
        "probability": round(float(probability) * 100, 2),
        "risk": risk
    }