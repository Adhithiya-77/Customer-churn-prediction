from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

from database import get_connection
from model import predict_customer

app = Flask(__name__)
CORS(app)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return jsonify({
        "message": "Customer Churn Prediction API is running!"
    })


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "message": "API is working"
    })


# =====================================================
# ADD CUSTOMER
# =====================================================

@app.route("/add-customer", methods=["POST"])
def add_customer():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No customer data received"}), 400

    required_fields = [
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

    missing_fields = [
        field for field in required_fields
        if field not in data or data[field] is None or data[field] == ""
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    try:

        customer_data = {
            field: data[field]
            for field in required_fields
            if field != "customer_name"
        }

        result = predict_customer(customer_data)

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

        customer_id = cursor.lastrowid

        conn.commit()
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


# =====================================================
# GET ALL CUSTOMERS
# =====================================================

@app.route("/customers", methods=["GET"])
def get_customers():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY id DESC
    """)

    customers = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(customers)


# =====================================================
# DASHBOARD STATISTICS
# =====================================================

@app.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
        WHERE ChurnPrediction = 'Yes'
    """)
    churned = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
        WHERE ChurnPrediction = 'No'
    """)
    retained = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
        WHERE RiskLevel = 'High'
    """)
    high_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT RiskLevel, COUNT(*)
        FROM customers
        GROUP BY RiskLevel
    """)

    risk_rows = cursor.fetchall()

    risk_distribution = {
        "Low": 0,
        "Medium": 0,
        "High": 0
    }

    for risk, count in risk_rows:
        if risk in risk_distribution:
            risk_distribution[risk] = count

    conn.close()

    return jsonify({
        "total_customers": total,
        "churned_customers": churned,
        "retained_customers": retained,
        "high_risk_customers": high_risk,
        "risk_distribution": risk_distribution
    })


# =====================================================
# TOP 20 CHURN CUSTOMERS
# =====================================================

@app.route("/top-customers", methods=["GET"])
def top_customers():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE ChurnPrediction = 'Yes'
        ORDER BY ChurnProbability DESC
        LIMIT 20
    """)

    customers = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(customers)


# =====================================================
# SEARCH CUSTOMERS WITH PAGINATION
# =====================================================

@app.route("/customers/search", methods=["GET"])
def search_customers():

    search = request.args.get("search", "").strip()
    search_by = request.args.get("search_by", "name").lower()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1 or per_page not in [10, 20, 50]:
        return jsonify({"error": "Invalid pagination values"}), 400

    offset = (page - 1) * per_page
    search_term = f"%{search}%"

    if search_by == "name":
        conditions = "customer_name LIKE ?"
        params = [search_term]

    elif search_by == "id":
        conditions = "CAST(id AS TEXT) LIKE ?"
        params = [search_term]

    elif search_by == "contract":
        conditions = "Contract LIKE ?"
        params = [search_term]

    elif search_by == "risk":
        conditions = "RiskLevel LIKE ?"
        params = [search_term]

    elif search_by == "all":
        conditions = """
            customer_name LIKE ?
            OR CAST(id AS TEXT) LIKE ?
            OR Contract LIKE ?
            OR CAST(tenure AS TEXT) LIKE ?
            OR ChurnPrediction LIKE ?
            OR RiskLevel LIKE ?
        """
        params = [search_term] * 6

    else:
        return jsonify({"error": "Invalid search category"}), 400

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM customers WHERE {conditions}",
            params
        )

        total = cursor.fetchone()[0]

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT *
            FROM customers
            WHERE {conditions}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            params + [per_page, offset]
        )

        customers = [dict(row) for row in cursor.fetchall()]

        total_pages = (total + per_page - 1) // per_page

        return jsonify({
            "customers": customers,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# =====================================================
# DELETE CUSTOMER
# =====================================================

@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM customers WHERE id = ?",
        (customer_id,)
    )

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({
            "error": "Customer not found"
        }), 404

    return jsonify({
        "message": "Customer deleted successfully!"
    })


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)