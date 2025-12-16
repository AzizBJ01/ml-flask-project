from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
emna_bp = Blueprint(
    "emna",
    __name__,
    template_folder="../templates"
)

# Route for Emna page
@emna_bp.route("/emna", methods=["GET"])
def emna():
    return render_template("emna/index.html")
