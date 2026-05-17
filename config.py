import os

# =========================================================
# AUTOMOTIVE PROFESSIONALS ERP - MASTER CONFIG
# =========================================================


# =========================
# FLASK CORE
# =========================

class Config:

    SECRET_KEY = "CHANGE_THIS_TO_SUPER_RANDOM_SECRET"

    DEBUG = True


# =========================
# PROJECT STRUCTURE
# =========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
INSTANCE_FOLDER = os.path.join(BASE_DIR, "instance")
PDF_FOLDER = os.path.join(BASE_DIR, "pdf")


# create folders automatically
for folder in [UPLOAD_FOLDER, STATIC_FOLDER, INSTANCE_FOLDER, PDF_FOLDER]:
    os.makedirs(folder, exist_ok=True)


# =========================
# COMPANY BRANDING (GLOBAL)
# =========================

class Brand:

    NAME = "Automotive Professionals (Pty) Ltd"
    SLOGAN = "Excellence Through Practical Teaching"

    EMAIL = "takernkambule@gmail.com"

    PHONE_1 = "76783891"
    PHONE_2 = "76783819"

    ADDRESS = "Manzini, Trelawny Park, Before Impumelelo Savings & Co Ops"

    TIN = "104332418"

    WEBSITE = "https://yourdomain.com"


# =========================
# BRAND ASSETS (IMAGES)
# =========================

class Assets:

    LOGO = "/static/images/logo.png"

    HERO_BG = "/static/images/hero.jpg"

    INVOICE_BG = "/static/images/invoice_bg.jpg"

    WORKSHOP_BG = "/static/images/workshop_bg.jpg"


# =========================
# BANKING DETAILS
# =========================

class Bank:

    BANK_NAME = "FNB Eswatini"
    ACCOUNT_NAME = "Ntokozo Nkambule"
    ACCOUNT_TYPE = "Current Account"
    ACCOUNT_NUMBER = "63178362877"
    BRANCH_CODE = "N/A"


# =========================
# INVOICE SETTINGS
# =========================

class Invoice:

    PREFIX = "AP"
    CURRENCY = "E"
    VAT_PERCENT = 15

    TERMS = "Payment is due within 7 days."

    FOOTER_NOTE = "Thank you for trusting our workshop."


# =========================
# EMAIL SYSTEM
# =========================

class Email:

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    SENDER_EMAIL = "YOUR_EMAIL@gmail.com"
    APP_PASSWORD = "YOUR_APP_PASSWORD"


# =========================
# ADMIN SECURITY
# =========================

class Security:

    ADMIN_PASSWORD = "1234"

    SESSION_TIMEOUT_MINUTES = 60


# =========================
# ALLOWED FILES
# =========================

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


# =========================
# DATABASE
# =========================

DATABASE = os.path.join(BASE_DIR, "instance", "site.db")


# =========================
# DEFAULT COURSES
# =========================

DEFAULT_COURSES = [
    "Heavy Plant Mechanics - 12 Months",
    "Light Motor Mechanics - 12 Months",
    "Welding - 6 Months",
    "Engine Management and Diagnostics - Short Course",
    "General Maintenance - Short Course"
]