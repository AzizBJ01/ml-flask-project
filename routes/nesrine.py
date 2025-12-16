from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
nesrine_bp = Blueprint(
    "nesrine",
    __name__,
    template_folder="../templates"
)

# Load trained model
# Route for Emna page
@nesrine_bp.route("/nesrine", methods=["GET"])
def nesrine():
    return render_template("nesrine/index.html")
