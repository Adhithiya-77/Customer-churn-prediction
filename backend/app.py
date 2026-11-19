from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

from database import get_connection
from model import predict_customer


app = Flask(__name__)
CORS(app)


# ==========================================
# REQUIRED CUSTOMER FEATURES
# ==========================================

REQUIRED_FIELDS = [
    "customer_name",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges"
]


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Customer Churn Prediction API is running!"
    })


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy"
    })


# ==========================================
# ADD CUSTOMER AND PREDICT CHURN
# ==========================================

@app.route("/add-customer", methods=["POST"])
def add_customer():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No customer data received"
            }), 400

        # Validate required fields
        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in data or data[field] is None
            or data[field] == ""
        ]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "fields": missing_fields
            }), 400

        customer_name = str(data["customer_name"]).strip()

        if not customer_name:
            return jsonify({
                "error": "Customer name cannot be empty"
            }), 400

        # Convert numeric values
        try:
            senior_citizen = int(data["SeniorCitizen"])
            tenure = int(data["tenure"])
            monthly_charges = float(data["MonthlyCharges"])
            total_charges = float(data["TotalCharges"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid numeric customer details"
            }), 400

        if senior_citizen not in (0, 1):
            return jsonify({
                "error": "SeniorCitizen must be 0 or 1"
            }), 400

        if not 0 <= tenure <= 72:
            return jsonify({
                "error": "Tenure must be between 0 and 72"
            }), 400

        if monthly_charges < 0 or total_charges < 0:
            return jsonify({
                "error": "Charges cannot be negative"
            }), 400

        # Prepare model input
        customer_data = {
            "gender": data["gender"],
            "SeniorCitizen": senior_citizen,
            "Partner": data["Partner"],
            "Dependents": data["Dependents"],
            "tenure": tenure,
            "PhoneService": data["PhoneService"],
            "MultipleLines": data["MultipleLines"],
            "InternetService": data["InternetService"],
            "OnlineSecurity": data["OnlineSecurity"],
            "OnlineBackup": data["OnlineBackup"],
            "DeviceProtection": data["DeviceProtection"],
            "TechSupport": data["TechSupport"],
            "StreamingTV": data["StreamingTV"],
            "StreamingMovies": data["StreamingMovies"],
            "Contract": data["Contract"],
            "PaperlessBilling": data["PaperlessBilling"],
            "PaymentMethod": data["PaymentMethod"],
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges
        }

        # Generate ML prediction
        result = predict_customer(customer_data)

        # Save customer and prediction
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers (
                customer_name,
                gender,
                SeniorCitizen,
                Partner,
                Dependents,
                tenure,
                PhoneService,
                MultipleLines,
                InternetService,
                OnlineSecurity,
                OnlineBackup,
                DeviceProtection,
                TechSupport,
                StreamingTV,
                StreamingMovies,
                Contract,
                PaperlessBilling,
                PaymentMethod,
                MonthlyCharges,
                TotalCharges,
                ChurnPrediction,
                ChurnProbability,
                RiskLevel
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            customer_name,
            customer_data["gender"],
            customer_data["SeniorCitizen"],
            customer_data["Partner"],
            customer_data["Dependents"],
            customer_data["tenure"],
            customer_data["PhoneService"],
            customer_data["MultipleLines"],
            customer_data["InternetService"],
            customer_data["OnlineSecurity"],
            customer_data["OnlineBackup"],
            customer_data["DeviceProtection"],
            customer_data["TechSupport"],
            customer_data["StreamingTV"],
            customer_data["StreamingMovies"],
            customer_data["Contract"],
            customer_data["PaperlessBilling"],
            customer_data["PaymentMethod"],
            customer_data["MonthlyCharges"],
            customer_data["TotalCharges"],
            result["prediction"],
            result["probability"],
            result["risk"]
        ))

        customer_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Customer added successfully",
            "customer_id": customer_id,
            "prediction": result["prediction"],
            "probability": result["probability"],
            "risk": result["risk"]
        }), 201

    except Exception as e:

        print("Add customer error:", e)

        return jsonify({
            "error": "Unable to add customer"
        }), 500


# ==========================================
# GET ALL CUSTOMERS
# ==========================================

@app.route("/customers", methods=["GET"])
def get_customers():

    try:

        conn = get_connection()

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM customers
            ORDER BY id DESC
        """)

        customers = [
            dict(row) for row in cursor.fetchall()
        ]

        conn.close()

        return jsonify(customers)

    except Exception as e:

        print("Get customers error:", e)

        return jsonify({
            "error": "Unable to retrieve customers"
        }), 500


# ==========================================
# DELETE CUSTOMER
# ==========================================

@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM customers
            WHERE id = ?
        """, (customer_id,))

        deleted_rows = cursor.rowcount

        conn.commit()
        conn.close()

        if deleted_rows == 0:

            return jsonify({
                "error": "Customer not found"
            }), 404

        return jsonify({
            "message": "Customer deleted successfully",
            "customer_id": customer_id
        }), 200

    except Exception as e:

        print("Delete customer error:", e)

        return jsonify({
            "error": "Unable to delete customer"
        }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )