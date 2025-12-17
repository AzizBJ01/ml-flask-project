from flask import Blueprint, render_template, request
import pandas as pd
import joblib
import os

nesrine_bp = Blueprint(
    "nesrine",
    __name__,
    template_folder="templates"
)
def predict_clicks_with_model(model, input_dict):
    row = {}

    # 1. Encode categorical features (NO scaling)
    for col in model.categorical_cols:
        value = input_dict.get(col)
        encoder = model.label_encoders[col]

        if value in encoder.classes_:
            row[col] = encoder.transform([value])[0]
        else:
            row[col] = model.unknown_defaults[col]

    # 2. Scale ONLY Acquisition_Cost
    cost_value = [[input_dict["Acquisition_Cost"]]]
    cost_scaled = model.scaler.transform(cost_value)[0][0]

    row["Acquisition_Cost"] = cost_scaled

    # 3. Build final feature matrix (same order as training)
    X = pd.DataFrame([row])[model.safe_features]

    # 4. Predict using the internal DecisionTreeRegressor
    prediction = model.model.predict(X.to_numpy())[0]

    return int(prediction)

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "campaign_model_finale.joblib")

model = joblib.load(MODEL_PATH)
print("MODEL CONTENT:", model.__dict__)


CATEGORIES = {
    'Target_Audience': ['Men 35-44'],
    'Channel_Used': ['LinkedIn', 'Facebook', 'Instagram'],
    'Campaign_Goal': ['Brand Awareness'],
    'Customer_Segment': ['Food'],
    'Language': ['English']
}

AVG_CLICKS = 1250

@nesrine_bp.route("/nesrine/", methods=["GET", "POST"])
def nesrine():

    analysis = None
    recommendations = []

    form_data = {
        'Target_Audience': 'Men 35-44',
        'Channel_Used': 'LinkedIn',
        'Campaign_Goal': 'Brand Awareness',
        'Customer_Segment': 'Food',
        'Language': 'English',
        'Acquisition_Cost': 3000
    }

    if request.method == "POST":

        form_data = {
            'Target_Audience': request.form.get("Target_Audience"),
            'Channel_Used': request.form.get("Channel_Used"),
            'Campaign_Goal': request.form.get("Campaign_Goal"),
            'Customer_Segment': request.form.get("Customer_Segment"),
            'Language': request.form.get("Language"),
            'Acquisition_Cost': float(request.form.get("Acquisition_Cost"))
        }

        df = pd.DataFrame([form_data])
        predicted_clicks = predict_clicks_with_model(model, form_data)

        diff_pct = ((predicted_clicks - AVG_CLICKS) / AVG_CLICKS) * 100
        cost_per_click = form_data['Acquisition_Cost'] / predicted_clicks

        current_channel = form_data['Channel_Used']

        for channel in CATEGORIES['Channel_Used']:
            if channel != current_channel:
                test_cfg = form_data.copy()
                test_cfg['Channel_Used'] = channel
                test_df = pd.DataFrame([test_cfg])

                new_pred = predict_clicks_with_model(model, test_cfg)

                recommendations.append({
                    'from': current_channel,
                    'to': channel,
                    'gain_clics': new_pred - predicted_clicks,
                    'new_total': new_pred,
                    'gain_cout': round((new_pred - predicted_clicks) * cost_per_click, 2)
                })

        recommendations.sort(key=lambda x: x['gain_clics'], reverse=True)

        analysis = {
            'predicted_clicks': predicted_clicks,
            'avg_clicks': AVG_CLICKS,
            'performance_pct': round(diff_pct, 1),
            'cost_per_click': round(cost_per_click, 2),
            'best_recommendation': recommendations[0] if recommendations else None
        }

    return render_template(
        "nesrine/index.html",
        analysis=analysis,
        recommendations=recommendations,
        categories=CATEGORIES,
        form_data=form_data
    )
