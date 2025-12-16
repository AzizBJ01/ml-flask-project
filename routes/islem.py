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
# Route for Emna page
@islem_bp.route("/islem", methods=["GET"])
def islem():
    return render_template("islem/index.html")
