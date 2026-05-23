from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# ==============================
# LOAD MODEL
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "expense_model_v2.pkl"
)

expense_model = joblib.load(MODEL_PATH)

print("ML Model Loaded Successfully")


# ==============================
# HOME ROUTE
# ==============================

@app.route('/')
def home():
    return "Finance AI Backend Running"


# ==============================
# PREDICTION API
# ==============================

@app.route('/predict', methods=['POST'])
def predict():

    data = request.json

    total_expense = float(data["total_expense"])
    income = float(data["income"])
    budget = float(data["budget"])

    input_features = {

        "Food": total_expense * 0.25,
        "Healthcare": total_expense * 0.05,
        "Others": total_expense * 0.20,
        "Recharge": total_expense * 0.10,
        "Shopping": total_expense * 0.30,
        "Transport": total_expense * 0.10,

        "Month_num": 1,

        "income": income,
        "budget": budget,

        "savings": income - total_expense,
        "prev_expense": total_expense
    }

    df = pd.DataFrame([input_features])

    prediction = expense_model.predict(df)[0]

    return jsonify({
        "predicted_expense": float(prediction)
    })


# ==============================

if __name__ == '__main__':
    app.run(debug=True)