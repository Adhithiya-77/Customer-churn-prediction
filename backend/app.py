from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable frontend communication
CORS(app)


# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Customer Churn Prediction API is running!"
    })


# Health check
@app.route("/health")
def health():
    return jsonify({
        "status": "Running",
        "application": "Customer Churn Prediction"
    })


if __name__ == "__main__":
    app.run(debug=True)