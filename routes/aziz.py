from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
aziz_bp = Blueprint(
    "aziz",
    __name__,
    template_folder="../templates"
)

# Load trained model
model = joblib.load("models/best_return_risk_model_correction.pkl")

@aziz_bp.route("/aziz", methods=["GET", "POST"])
def aziz():
    prediction = None

    if request.method == "POST":
        try:
            data = {
                'Return_Rate_History': float(request.form["param1"]),
                'Product_Rating_Avg': float(request.form["param2"]),
                'Customer_Satisfaction': float(request.form["param3"]),
                'Purchase_Frequency': float(request.form["param4"]),
                'Average_Spend': float(request.form["param5"]),
            }

            input_df = pd.DataFrame([data])

            probability = model.predict_proba(input_df)[0][1] * 100

            if probability < 35:
                risk = "LOW RISK"
            elif probability < 60:
                risk = "MEDIUM RISK"
            elif probability < 85:
                risk = "HIGH RISK"
            else:
                risk = "EXTREME RISK"

            prediction = f"{risk} — {probability:.2f}%"

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("aziz/index.html", prediction=prediction)
