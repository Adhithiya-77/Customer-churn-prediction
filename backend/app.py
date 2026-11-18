from flask import Flask, jsonify, request
from flask_cors import CORS

from database import get_connection
from model import predict_customer

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Customer Churn Prediction API is running!"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "Running"
    })


# Add new customer
@app.route("/add-customer", methods=["POST"])
def add_customer():

    try:
        data = request.get_json()

        required_fields = [
            "customer_name", "gender", "SeniorCitizen",
            "Partner", "Dependents", "tenure",
            "PhoneService", "MultipleLines", "InternetService",
            "OnlineSecurity", "OnlineBackup", "DeviceProtection",
            "TechSupport", "StreamingTV", "StreamingMovies",
            "Contract", "PaperlessBilling", "PaymentMethod",
            "MonthlyCharges", "TotalCharges"
        ]

        missing = [
            field for field in required_fields
            if field not in data
        ]

        if missing:
            return jsonify({
                "error": "Missing customer fields",
                "fields": missing
            }), 400

        customer_data = {
            field: data[field]
            for field in required_fields
            if field != "customer_name"
        }

        # Predict churn
        result = predict_customer(customer_data)

        # Save customer and prediction
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers (
                customer_name, gender, SeniorCitizen,
                Partner, Dependents, tenure,
                PhoneService, MultipleLines, InternetService,
                OnlineSecurity, OnlineBackup, DeviceProtection,
                TechSupport, StreamingTV, StreamingMovies,
                Contract, PaperlessBilling, PaymentMethod,
                MonthlyCharges, TotalCharges,
                ChurnPrediction, ChurnProbability, RiskLevel
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            data["customer_name"],
            data["gender"],
            data["SeniorCitizen"],
            data["Partner"],
            data["Dependents"],
            data["tenure"],
            data["PhoneService"],
            data["MultipleLines"],
            data["InternetService"],
            data["OnlineSecurity"],
            data["OnlineBackup"],
            data["DeviceProtection"],
            data["TechSupport"],
            data["StreamingTV"],
            data["StreamingMovies"],
            data["Contract"],
            data["PaperlessBilling"],
            data["PaymentMethod"],
            data["MonthlyCharges"],
            data["TotalCharges"],
            result["prediction"],
            result["probability"],
            result["risk"]
        ))

        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Customer added successfully!",
            "customer_id": customer_id,
            "prediction": result["prediction"],
            "probability": result["probability"],
            "risk": result["risk"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)