import sqlite3
from pathlib import Path

# Database location
DB_PATH = Path(__file__).resolve().parent / "customers.db"


# Connect to database
def get_connection():
    return sqlite3.connect(DB_PATH)


# Create customer table
def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,

            gender TEXT,
            SeniorCitizen INTEGER,
            Partner TEXT,
            Dependents TEXT,
            tenure INTEGER,
            PhoneService TEXT,
            MultipleLines TEXT,
            InternetService TEXT,
            OnlineSecurity TEXT,
            OnlineBackup TEXT,
            DeviceProtection TEXT,
            TechSupport TEXT,
            StreamingTV TEXT,
            StreamingMovies TEXT,
            Contract TEXT,
            PaperlessBilling TEXT,
            PaymentMethod TEXT,
            MonthlyCharges REAL,
            TotalCharges REAL,

            ChurnPrediction TEXT,
            ChurnProbability REAL,
            RiskLevel TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("Customer database created successfully!")


if __name__ == "__main__":
    create_table()