from flask import Blueprint, render_template, request
import pandas as pd
import joblib

# Create Blueprint
syrine_bp = Blueprint(
    "syrine",
    __name__,
    template_folder="../templates"
)


@syrine_bp.route("/syrine", methods=["GET"])
def syrine():
    return render_template("syrine/index.html")
