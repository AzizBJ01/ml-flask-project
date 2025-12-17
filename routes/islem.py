from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
#islem_bp = Blueprint(
 #   "islem",
  #  __name__,
   # template_folder="../templates"
#)

# Load trained model
# Route for Emna page
#@islem_bp.route("/islem", methods=["GET"])
#def islem():
  #  return render_template("islem/index.html")
# /routes/islem.py - COMPLETE WORKING VERSION
# /routes/islem.py - SIMPLE WORKING VERSION
from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
islem_bp = Blueprint(
    "islem",
    __name__,
    template_folder="../templates"
)

# Load trained model
model = joblib.load("models/impressions_model.pkl")
encoders = joblib.load("models/encoders.pkl")

# Define expected values based on your training data
EXPECTED_CATEGORIES = {
    "Target_Audience": ["Women 18–24", "Women 25–34", "Women 35–44", "Women 45+", 
                       "Men 18–24", "Men 25–34", "Men 35–44", "Men 45+"],
    "Campaign_Goal": ["Increase Sales", "Increase Brand Awareness", "Increase Website Traffic"],
    "Channel_Used": ["Facebook", "Instagram", "Twitter", "Pinterest"],
    "Location": ["Paris", "London", "Berlin", "New York", "Online / Global"],
    "Language": ["English", "French", "German", "Spanish"],
    "Customer_Segment": ["Retail", "Luxury", "B2B", "B2C"],
    "Company": ["Nike", "Adidas", "Zara", "H&M", "Amazon", "Other"]
}

@islem_bp.route("/islem", methods=["GET", "POST"])
def islem():
    prediction = None
    platform_results = None
    budget_allocation = None
    form_data = {}

    if request.method == "POST":
        try:
            # Collect form data
            form_data = {
                "duration": request.form.get("duration", ""),
                "budget": request.form.get("budget", ""),
                "conversion_rate": request.form.get("conversion_rate", ""),
                "engagement": request.form.get("engagement", ""),
                "target_audience": request.form.get("target_audience", ""),
                "campaign_goal": request.form.get("campaign_goal", ""),
                "location": request.form.get("location", ""),
                "language": request.form.get("language", ""),
                "customer_segment": request.form.get("customer_segment", ""),
                "company": request.form.get("company", "")
            }

            # Convert numeric values
            base_data = {
                "Duration_Days": int(form_data["duration"]) if form_data["duration"] else 30,
                "Acquisition_Cost": float(form_data["budget"]) if form_data["budget"] else 5000,
                "Conversion_Rate": float(form_data["conversion_rate"]) if form_data["conversion_rate"] else 5.0,
                "Engagement_Score": float(form_data["engagement"]) if form_data["engagement"] else 5.0,
                "Target_Audience": form_data["target_audience"],
                "Campaign_Goal": form_data["campaign_goal"],
                "Location": form_data["location"],
                "Language": form_data["language"],
                "Customer_Segment": form_data["customer_segment"],
                "Company": form_data["company"] if form_data["company"] else "Other"
            }

            # Get total budget for allocation calculation
            total_budget = float(form_data["budget"]) if form_data["budget"] else 5000

            # Validate and adjust categories to match training data
            for field, expected_values in EXPECTED_CATEGORIES.items():
                if field in base_data and base_data[field] not in expected_values:
                    # Find closest match or use default
                    if field == "Target_Audience":
                        # Map similar categories
                        if "Men" in base_data[field]:
                            base_data[field] = "Men 25–34"  # Default male category
                        elif "Women" in base_data[field]:
                            base_data[field] = "Women 25–34"  # Default female category
                        else:
                            base_data[field] = "Women 25–34"  # Default
                    else:
                        # Use first expected value as default
                        base_data[field] = expected_values[0]

            platforms = EXPECTED_CATEGORIES["Channel_Used"]
            results = {}

            for platform in platforms:
                row = base_data.copy()
                row["Channel_Used"] = platform

                df = pd.DataFrame([row])

                # Encode categorical columns with error handling
                try:
                    for col, le in encoders.items():
                        if col in df.columns:
                            # Transform with unseen label handling
                            try:
                                df[col + "_Encoded"] = le.transform(df[col])
                            except ValueError:
                                # Handle unseen label by using a default value
                                default_value = le.classes_[0] if len(le.classes_) > 0 else 0
                                df[col + "_Encoded"] = [le.transform([default_value])[0]]
                    
                    # Prepare features
                    X = df[
                        [
                            "Duration_Days",
                            "Acquisition_Cost",
                            "Conversion_Rate",
                            "Engagement_Score",
                            "Target_Audience_Encoded",
                            "Campaign_Goal_Encoded",
                            "Channel_Used_Encoded",
                            "Location_Encoded",
                            "Language_Encoded",
                            "Customer_Segment_Encoded",
                            "Company_Encoded",
                        ]
                    ]

                    results[platform] = int(model.predict(X)[0])
                    
                except Exception as e:
                    results[platform] = 0  # Default value if prediction fails
                    print(f"Error predicting for {platform}: {e}")

            platform_results = results
            prediction = max(results, key=results.get)
            
            # BUDGET ALLOCATION CALCULATION - FIXED
            if platform_results and total_budget > 0:
                total_impressions = sum(results.values())
                
                # Calculate proportional budget allocation based on impressions
                if total_impressions > 0:
                    budget_allocation = {}
                    for platform, impressions in results.items():
                        proportion = impressions / total_impressions
                        budget_allocation[platform] = round(proportion * total_budget, 2)
                else:
                    # If all impressions are 0, distribute budget evenly
                    budget_allocation = {
                        platform: round(total_budget / len(results), 2)
                        for platform in results.keys()
                    }

        except Exception as e:
            prediction = f"Error: {str(e)}"
            print(f"Form submission error: {e}")

    return render_template(
        "islem/index.html",
        prediction=prediction,
        platform_results=platform_results,
        budget_allocation=budget_allocation,
        form_data=form_data  # Pass form data back to repopulate form
    )