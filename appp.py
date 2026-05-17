from flask import Flask
from config import Config, DATABASE, UPLOAD_FOLDER

import os
import sqlite3


# =========================
# FLASK APP INIT
# =========================

app = Flask(__name__)
app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# REGISTER BLUEPRINTS (MODULES WILL GO HERE)
# =========================

# We will add these later:
# from routes.auth import auth_bp
# from routes.admin import admin_bp
# from routes.workshop import workshop_bp
# from routes.finance import finance_bp
# from routes.files import files_bp

# app.register_blueprint(auth_bp)
# app.register_blueprint(admin_bp)
# app.register_blueprint(workshop_bp)
# app.register_blueprint(finance_bp)
# app.register_blueprint(files_bp)


# =========================
# HEALTH CHECK ROUTE
# =========================

@app.route("/")
def home():
    return {
        "status": "running",
        "app": "Automotive ERP System",
        "message": "System is active"
    }


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)