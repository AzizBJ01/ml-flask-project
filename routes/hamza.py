from flask import Blueprint, render_template, request, session
import pandas as pd
import joblib
import os
from datetime import datetime

# Create Blueprint
hamza_bp = Blueprint(
    "hamza",
    __name__,
    template_folder="../templates"
)

# Model path
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "web_xgboost_classifier.pkl")
model = None

def load_model():
    """Lazy load the model only when needed"""
    global model
    if model is None:
        model = joblib.load(model_path)
    return model

def generate_recommendations(purchase_amount, frequency, satisfaction, rating, age, high_value_prob):
    """Generate marketing recommendations based on customer features and prediction"""
    recommendations = []
    
    # Overall value assessment
    if high_value_prob >= 70:
        recommendations.append({
            'priority': 'high',
            'title': 'High-Value Customer',
            'message': 'This customer is a high-value target. Focus on retention and upselling premium products.'
        })
    elif high_value_prob >= 40:
        recommendations.append({
            'priority': 'medium',
            'title': 'Medium-Value Customer',
            'message': 'This customer has potential. Engage with targeted campaigns to increase their lifetime value.'
        })
    else:
        recommendations.append({
            'priority': 'low',
            'title': 'Low-Value Customer',
            'message': 'Focus on cost-effective engagement strategies. Consider reactivation campaigns if they show interest.'
        })
    
    # Specific feature-based recommendations
    if purchase_amount < 100:
        recommendations.append({
            'priority': 'medium',
            'title': 'Increase Purchase Amount',
            'message': f'Current average purchase (${purchase_amount:.2f}) is low. Recommend bundle deals or premium products to increase order value.'
        })
    elif purchase_amount > 200:
        recommendations.append({
            'priority': 'high',
            'title': 'Upsell Opportunity',
            'message': f'High purchase amount (${purchase_amount:.2f}) indicates willingness to spend. Target with exclusive offers and loyalty rewards.'
        })
    
    if frequency < 3:
        recommendations.append({
            'priority': 'high',
            'title': 'Improve Purchase Frequency',
            'message': f'Low frequency ({frequency:.1f} purchases). Send personalized recommendations and remind about your products/services regularly.'
        })
    elif frequency > 8:
        recommendations.append({
            'priority': 'high',
            'title': 'Loyalty Program',
            'message': f'High frequency ({frequency:.1f} purchases) shows loyalty. Introduce VIP program or exclusive benefits to maintain engagement.'
        })
    
    if satisfaction < 3.5:
        recommendations.append({
            'priority': 'high',
            'title': 'Address Satisfaction Issues',
            'message': f'Low satisfaction score ({satisfaction:.1f}/5.0). Reach out to understand concerns and improve experience. Critical for retention.'
        })
    elif satisfaction >= 4.5:
        recommendations.append({
            'priority': 'medium',
            'title': 'Leverage Positive Experience',
            'message': f'High satisfaction ({satisfaction:.1f}/5.0). Perfect time to ask for referrals, testimonials, or upsell related products.'
        })
    
    if rating < 3.5:
        recommendations.append({
            'priority': 'medium',
            'title': 'Product Quality Focus',
            'message': f'Lower product rating ({rating:.1f}/5.0). Review product offerings and highlight best-rated alternatives.'
        })
    
    if age < 25:
        recommendations.append({
            'priority': 'medium',
            'title': 'Young Customer Segment',
            'message': f'Young customer (age {age:.0f}). Focus on social media marketing, trends, and value-for-money messaging.'
        })
    elif age > 50:
        recommendations.append({
            'priority': 'medium',
            'title': 'Mature Customer Segment',
            'message': f'Mature customer (age {age:.0f}). Emphasize quality, reliability, and customer service in communications.'
        })
    
    return recommendations

def calculate_acquisition_metrics(predictions_history):
    """Calculate ML-powered acquisition cost optimization metrics"""
    if not predictions_history:
        return {
            'high_value_rate': 0,
            'cac_efficiency': 0,
            'target_quality_score': 0,
            'cost_savings_potential': 0,
            'conversion_potential': 0,
            'total_evaluated': 0,
            'high_value_count': 0,
            'medium_value_count': 0,
            'low_value_count': 0
        }
    
    total = len(predictions_history)
    high_value = sum(1 for p in predictions_history if p.get('is_high_value', False))
    medium_value = sum(1 for p in predictions_history if 40 <= p.get('proba_class_1', 0) < 70)
    low_value = total - high_value - medium_value
    
    high_value_rate = (high_value / total * 100) if total > 0 else 0
    
    # CAC Efficiency: Higher high-value rate = lower effective CAC
    # Formula: 100 - (low_value_rate * 1.5) + (high_value_rate * 0.8)
    low_value_rate = (low_value / total * 100) if total > 0 else 0
    cac_efficiency = max(0, min(100, 100 - (low_value_rate * 1.5) + (high_value_rate * 0.8)))
    
    # Target Quality Score: Weighted average of value probabilities
    avg_high_value_prob = sum(p.get('proba_class_1', 0) for p in predictions_history) / total if total > 0 else 0
    target_quality_score = avg_high_value_prob
    
    # Cost Savings Potential: If you only target high-value, how much you save
    # Assuming low-value targets waste 70% of ad spend, medium waste 30%
    waste_from_low = low_value_rate * 0.70
    waste_from_medium = medium_value * 0.30 / total * 100 if total > 0 else 0
    cost_savings_potential = waste_from_low + waste_from_medium
    
    # Conversion Potential: Based on average probabilities
    conversion_potential = avg_high_value_prob
    
    return {
        'high_value_rate': round(high_value_rate, 1),
        'cac_efficiency': round(cac_efficiency, 1),
        'target_quality_score': round(target_quality_score, 1),
        'cost_savings_potential': round(cost_savings_potential, 1),
        'conversion_potential': round(conversion_potential, 1),
        'total_evaluated': total,
        'high_value_count': high_value,
        'medium_value_count': medium_value,
        'low_value_count': low_value
    }

@hamza_bp.route("/hamza", methods=["GET", "POST"])
def hamza():
    prediction = None
    
    # Initialize session predictions history if not exists
    if 'predictions_history' not in session:
        session['predictions_history'] = []
    
    if request.method == "POST":
        try:
            # Load model if not already loaded
            ml_model = load_model()
            
            # Extract form data
            purchase_amount = request.form.get("purchase_amount")
            frequency = request.form.get("frequency")
            satisfaction = request.form.get("satisfaction")
            rating = request.form.get("rating")
            age = request.form.get("age")
            
            # Create input DataFrame
            input_data = pd.DataFrame({
                'Purchase_Amount': [float(purchase_amount)],
                'Frequency_of_Purchase': [float(frequency)],
                'Customer_Satisfaction': [float(satisfaction)],
                'Product_Rating': [float(rating)],
                'Age': [float(age)]
            })
            
            # Make prediction
            prediction_result = ml_model.predict(input_data)[0]
            prediction_proba = ml_model.predict_proba(input_data)[0]
            
            # Interpret prediction in marketing terms
            proba_class_1 = float(prediction_proba[1]) * 100 if len(prediction_proba) > 1 else 0
            proba_class_0 = float(prediction_proba[0]) * 100
            
            # Determine customer value segment
            if proba_class_1 >= 70:
                value_segment = "HIGH VALUE"
                value_color = "#00ff88"
                value_icon = "⭐"
            elif proba_class_1 >= 40:
                value_segment = "MEDIUM VALUE"
                value_color = "#ffaa00"
                value_icon = "📊"
            else:
                value_segment = "LOW VALUE"
                value_color = "#ff6b6b"
                value_icon = "⚠️"
            
            # Generate marketing recommendations based on features and prediction
            recommendations = generate_recommendations(
                float(purchase_amount), 
                float(frequency), 
                float(satisfaction), 
                float(rating), 
                float(age),
                proba_class_1
            )
            
            # Format prediction result
            prediction = {
                'class': int(prediction_result),
                'probability': float(max(prediction_proba)) * 100,
                'proba_class_0': proba_class_0,
                'proba_class_1': proba_class_1,
                'value_segment': value_segment,
                'value_color': value_color,
                'value_segment': value_segment,
                'value_color': value_color,
                'value_icon': value_icon,
                'recommendations': recommendations,
                'is_high_value': proba_class_1 >= 70,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store prediction in session history (keep last 100)
            session['predictions_history'].append({
                'proba_class_1': proba_class_1,
                'is_high_value': proba_class_1 >= 70,
                'value_segment': value_segment,
                'timestamp': datetime.now().isoformat()
            })
            if len(session['predictions_history']) > 100:
                session['predictions_history'] = session['predictions_history'][-100:]
            session.modified = True
            
        except Exception as e:
            prediction = {'error': str(e)}
    
    # Calculate acquisition metrics from prediction history
    acquisition_metrics = calculate_acquisition_metrics(session.get('predictions_history', []))
    
    return render_template("hamza/index.html", prediction=prediction, metrics=acquisition_metrics)
