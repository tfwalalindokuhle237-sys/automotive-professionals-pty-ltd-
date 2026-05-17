import sqlite3
from config import DATABASE


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# INITIALISE ALL TABLES (FROM YOUR ORIGINAL SCRIPT)
# =========================================================

def init_db():
    conn = get_db()
    c = conn.cursor()


    # ================= APPLICATIONS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        course TEXT,
        file TEXT,
        date TEXT
    )
    """)


    # ================= STUDENTS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        course TEXT,
        status TEXT,
        date TEXT
    )
    """)


    # ================= PAYMENTS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        date TEXT
    )
    """)


    # ================= FILES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        description TEXT,
        date TEXT
    )
    """)


    # ================= WORKSHOP JOBS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS workshop_jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,

        customer_name TEXT,
        phone TEXT,
        address TEXT,

        vehicle_make TEXT,
        vehicle_model TEXT,
        registration TEXT,
        vin TEXT,
        mileage TEXT,

        problem TEXT,
        diagnosis TEXT,
        repair_notes TEXT,

        assigned_mechanic TEXT,

        labor_cost REAL,
        parts_cost REAL,
        total_cost REAL,
        amount_paid REAL,

        deadline TEXT,

        status TEXT,
        date_received TEXT,
        date_completed TEXT
    )
    """)


    # ================= COMPANY MESSAGES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS company_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver_email TEXT,
        subject TEXT,
        message TEXT,
        attachment TEXT,
        status TEXT,
        date TEXT
    )
    """)


    # ================= EXPENSES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS workshop_expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        amount REAL,
        description TEXT,
        date TEXT
    )
    """)


    # ================= SETTINGS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        hero TEXT,
        whatsapp TEXT,
        courses TEXT,
        logo TEXT
    )
    """)


    # ================= COMPANIES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        balance REAL DEFAULT 0,
        date TEXT
    )
    """)


    # ================= INVOICES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS invoices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        company_id INTEGER,
        description TEXT,
        amount REAL,
        paid REAL,
        status TEXT,
        pdf TEXT,
        date TEXT
    )
    """)


    conn.commit()
    conn.close()