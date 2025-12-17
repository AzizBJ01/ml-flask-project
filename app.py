class CampaignFinale:
    pass

from flask import Flask, render_template
from routes.aziz import aziz_bp
from routes.emna import emna_bp
from routes.nesrine import nesrine_bp
from routes.syrine import syrine_bp
from routes.hamza import hamza_bp
from routes.islem import islem_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(aziz_bp)
app.register_blueprint(emna_bp)
app.register_blueprint(nesrine_bp)
app.register_blueprint(syrine_bp)
app.register_blueprint(islem_bp)
app.register_blueprint(hamza_bp)


# Landing page
@app.route("/")
def home():
    return render_template("index.html")  # your main page with buttons

if __name__ == "__main__":
    app.run(debug=True)
