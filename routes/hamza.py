from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
hamza_bp = Blueprint(
    "hamza",
    __name__,
    template_folder="../templates"
)

# Route for Emna page
@hamza_bp.route("/hamza", methods=["GET"])
def hamza():
    return render_template("hamza/index.html")
