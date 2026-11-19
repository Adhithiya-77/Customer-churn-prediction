import random

from database import get_connection
from model import predict_customer


# ==========================================
# CONFIGURATION
# ==========================================

TOTAL_CUSTOMERS = 500

random.seed(42)


# ==========================================
# GENERATE CUSTOMER DATA
# ==========================================

def generate_customer(customer_number):

    gender = random.choice(["Male", "Female"])

    senior_citizen = random.choices(
        [0, 1],
        weights=[85, 15]
    )[0]

    partner = random.choice(["Yes", "No"])

    dependents = random.choice(["Yes", "No"])

    tenure = random.randint(0, 72)

    phone_service = random.choice(["Yes", "No"])

    if phone_service == "No":
        multiple_lines = "No phone service"
    else:
        multiple_lines = random.choice(["Yes", "No"])

    internet_service = random.choices(
        ["DSL", "Fiber optic", "No"],
        weights=[35, 45, 20]
    )[0]

    if internet_service == "No":

        online_security = "No internet service"
        online_backup = "No internet service"
        device_protection = "No internet service"
        tech_support = "No internet service"
        streaming_tv = "No internet service"
        streaming_movies = "No internet service"

    else:

        online_security = random.choice(["Yes", "No"])
        online_backup = random.choice(["Yes", "No"])
        device_protection = random.choice(["Yes", "No"])
        tech_support = random.choice(["Yes", "No"])
        streaming_tv = random.choice(["Yes", "No"])
        streaming_movies = random.choice(["Yes", "No"])

    contract = random.choices(
        ["Month-to-month", "One year", "Two year"],
        weights=[55, 25, 20]
    )[0]

    paperless_billing = random.choice(["Yes", "No"])

    payment_method = random.choice([
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])

    monthly_charges = round(
        random.uniform(20, 120), 2
    )

    total_charges = round(
        monthly_charges * tenure, 2
    )

    customer = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges
    }

    return customer


# ==========================================
# INSERT CUSTOMERS INTO DATABASE
# ==========================================

def bulk_insert_customers():

    print("\nGenerating customer records...")

    conn = get_connection()
    cursor = conn.cursor()

    records = []

    successful_predictions = 0

    for i in range(1, TOTAL_CUSTOMERS + 1):

        customer_data = generate_customer(i)

        customer_name = f"Synthetic Customer {i:04d}"

        # Generate ML prediction
        prediction_result = predict_customer(customer_data)

        successful_predictions += 1

        record = (
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
            prediction_result["prediction"],
            prediction_result["probability"],
            prediction_result["risk"]
        )

        records.append(record)

    # Insert all records together
    cursor.executemany(
        """
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
        """,
        records
    )

    conn.commit()

    # Get updated database count
    cursor.execute("SELECT COUNT(*) FROM customers")

    total_records = cursor.fetchone()[0]

    conn.close()

    print("\n===================================")
    print("CUSTOMER INSERTION COMPLETED")
    print("===================================")

    print(f"New customers inserted: {len(records)}")
    print(f"Predictions generated: {successful_predictions}")
    print(f"Total database records: {total_records}")

    print("===================================")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    bulk_insert_customers()