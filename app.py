from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import sqlite3
import os
from datetime import datetime
from threading import Thread
import smtplib
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from config import COMPANY
os.makedirs("uploads", exist_ok=True)

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM_SECURE_KEY"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

ADMIN_PASSWORD = "1234"

MAIL_SENDER = "tfwalalindokuhle237@gmail.com"
MAIL_PASSWORD = "pvpo qdxj ueya bebu"

# ---------------- DATABASE ----------------
def db():
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = db()
    c = conn.cursor()

    # ---------------- APPLICATIONS ----------------
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

    # ---------------- STUDENTS ----------------
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

    # ---------------- PAYMENTS (STUDENT FINANCE) ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        date TEXT
    )
    """)

    # ---------------- INSTITUTION FILES ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        description TEXT,
        date TEXT
    )
    """)

    # ---------------- WORKSHOP JOBS (ADDED EXACTLY AS REQUESTED) ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS workshop_jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        invoice_no TEXT,

        customer_name TEXT,
        phone TEXT,
        vehicle TEXT,
        plate TEXT,
        problem TEXT,

        labor_cost REAL,
        parts_cost REAL,
        amount_paid REAL,

        date_in TEXT,
        status TEXT
    )
    """)


    # ---------------- COMPANY COMMUNICATION ----------------
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

    # ---------------- WORKSHOP EXPENSES / WALLET ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS workshop_expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        amount REAL,
        description TEXT,
        date TEXT
    )
    """)

    # ---------------- SETTINGS ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        hero TEXT,
        whatsapp TEXT,
        courses TEXT,
        logo TEXT
    )
    """)
    
    # ---------------- COMPANIES ----------------
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
    
    # ---------------- INVOICES ----------------
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

    # ---------------- DEFAULT DATA ----------------
    c.execute("""
    INSERT OR IGNORE INTO settings VALUES (
        1,
        'Automotive Training Centre',
        '26876783891',
        '12 Months - Heavy Plant Mechanics, 12 Months - Light Motor Mechanics | 6 Months - Welding | Short Courses- Engine Management And Diagnosis,General Maintenance',
        ''
    )
    """)

    conn.commit()
    conn.close()


init()





# ---------------- HELPERS ----------------
def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save(file):
    if file and allowed(file.filename):
        name = secure_filename(file.filename)
        final = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{name}"
        path = os.path.join(UPLOAD_FOLDER, final)
        file.save(path)
        return final
    return ""

def get_student_finance(student_id):
    conn = db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    payments = conn.execute(
        "SELECT SUM(amount) as total FROM payments WHERE student_id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    paid = payments["total"] if payments["total"] else 0

    return {
        "student": student,
        "paid": paid
    }
def get_settings():
    conn = db()
    data = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    conn.close()
    return data

def get_stats():
    conn = db()

    students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

    conn.close()

    return {
        "students": students,
        "apps": apps,
        "files": files
    }
def update_settings(hero, whatsapp, courses, logo):
    conn = db()
    conn.execute("""
    UPDATE settings
    SET hero=?, whatsapp=?, courses=?, logo=?
    WHERE id=1
    """, (hero, whatsapp, courses, logo))
    conn.commit()
    conn.close()

def send_email(name, email, course):
    try:
        msg = f"Subject: New Application\n\n{name} applied for {course}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, email, msg)
        server.quit()
    except:
        print("Email failed")



#______________Main UI____________#
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals Pty Ltd</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body{
margin:0;
font-family:Segoe UI, Arial;
color:white;
background:url('https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0') center/cover fixed;
}

.overlay{
background:rgba(0,0,0,0.88);
min-height:100vh;
}

/* NAV */
.nav{
display:flex;
justify-content:space-between;
align-items:center;
padding:15px 25px;
background:rgba(0,0,0,0.85);
border-bottom:1px solid #333;
position:sticky;
top:0;
z-index:100;
}

.logo{
width:45px;
height:45px;
border-radius:50%;
object-fit:cover;
border:2px solid #25D366;
background:#222;
}

.nav a{
color:white;
margin:0 10px;
text-decoration:none;
}

.nav a:hover{
color:#25D366;
}

/* HERO */
.hero{
text-align:center;
padding:60px 20px 20px;
}

.hero-box{
display:inline-block;
padding:25px 35px;
border-radius:15px;
background:rgba(0,0,0,0.65);
border:1px solid #333;
}

.hero h1{
margin:0;
color:#25D366;
font-size:40px;
}

/* DASHBOARD */
.dashboard{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:20px;
padding:20px;
}

.stat-box{
background:rgba(20,20,20,0.9);
padding:15px;
width:200px;
border-radius:10px;
text-align:center;
border:1px solid #333;
}

.stat-box h2{
color:#25D366;
}

/* MAIN */
.container{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:25px;
padding:30px;
}

/* CARD */
.card{
background:rgba(20,20,20,0.9);
padding:22px;
width:360px;
border-radius:15px;
border:1px solid #333;
}

/* BUTTON */
.btn{
background:#25D366;
padding:12px;
width:100%;
border:none;
cursor:pointer;
font-weight:bold;
color:black;
border-radius:6px;
}

/* INPUT */
input,select,textarea{
width:100%;
padding:10px;
margin:8px 0;
background:#111;
color:white;
border:1px solid #333;
border-radius:6px;
}

/* SECTION TITLE */
.section-title{
color:#25D366;
font-weight:bold;
margin-bottom:10px;
}

/* LIST */
.list-item{
background:#111;
padding:8px;
margin:5px 0;
border-left:3px solid #25D366;
border-radius:5px;
font-size:13px;
}

/* FOOTER */
footer{
text-align:center;
padding:25px;
opacity:0.7;
font-size:13px;
margin-top:20px;
border-top:1px solid #222;
}

</style>
</head>

<body>

<div class="overlay">

<!-- NAV -->
<div class="nav">

    <div style="display:flex;align-items:center;gap:10px;">
        {% if logo %}
            <img src="/uploads/{{logo}}" class="logo">
        {% else %}
            <div class="logo"></div>
        {% endif %}
        <b>Automotive Professionals Pty Ltd</b>
    </div>

    <div>
        <a href="/">Home</a>
        {% if session.admin %}
            <a href="/admin">Dashboard</a>
            <a href="/settings">Settings</a>
            <a href="/logout">Logout</a>
        {% else %}
            <a href="/login">Staff Login</a>
        {% endif %}
    </div>

</div>

<!-- HERO -->
<div class="hero">
    <div class="hero-box">
        <h1>{{h}}</h1>
        <p>Excellence Through Practical Teaching</p>
    </div>
</div>

<!-- STATS -->
<div class="dashboard">

    <div class="stat-box">
        <h3>Students</h3>
        <h2>{{stats.students}}</h2>
    </div>

    <div class="stat-box">
        <h3>Applications</h3>
        <h2>{{stats.apps}}</h2>
    </div>

    <div class="stat-box">
        <h3>Files</h3>
        <h2>{{stats.files}}</h2>
    </div>

</div>

<!-- MAIN -->
<div class="container">

    <!-- APPLICATION FORM -->
    <div class="card">

        <div class="section-title">🎓 Student Application</div>

        <form method="POST" action="/apply" enctype="multipart/form-data">

            <input name="name" placeholder="Full Name" required>
            <input name="phone" placeholder="Phone Number" required>
            <input name="email" placeholder="Email Address" required>

            <select name="course">
                {% for c in courses %}
                <option>{{c}}</option>
                {% endfor %}
            </select>

            <input type="file" name="file">

            <button class="btn">Submit Application</button>

        </form>
    </div>

    <!-- APPLICATION REQUIREMENTS -->
    <div class="card">

        <div class="section-title">📄 Application Requirements</div>

        <div class="list-item">✔ Completed Application Form</div>
        <div class="list-item">✔ Identification Documents (ID / Passport / Birth Certificate)</div>
        <div class="list-item">✔ Proof of Residence</div>

        <div class="list-item">✔ Academic Transcripts</div>
        <div class="list-item">✔ Certificates / Diplomas</div>
        <div class="list-item">✔ Entrance / Test Results (if required)</div>

        <div class="list-item">✔ Personal Statement / CV</div>
        <div class="list-item">✔ Letters of Recommendation</div>

        <div class="list-item">✔ Application Fee Proof</div>
        <div class="list-item">✔ Proof of Funding / Financial Capability</div>
        <div class="list-item">✔ Medical / Health Clearance</div>

    </div>

    <!-- COURSES (EDITABLE FROM ADMIN) -->
    <div class="card">

        <div class="section-title">📚 Courses Offered</div>

        {% for c in courses %}
        <div class="list-item">{{c}}</div>
        {% endfor %}

    </div>

    <!-- SERVICES -->
    <div class="card">

        <div class="section-title">🔧 Services (Workshop + Training)</div>

        <div class="list-item">Engine Diagnostics & Repair</div>
        <div class="list-item">Vehicle Servicing & Maintenance</div>
        <div class="list-item">Brake & Suspension Repairs</div>
        <div class="list-item">Electrical System Diagnostics</div>
        <div class="list-item">Welding & Fabrication Training</div>
        <div class="list-item">Heavy Plant Mechanics Training</div>

    </div>

</div>

<!-- FOOTER -->
<footer>
© 2026 Automotive Professionals (Pty) Ltd | Automotive Training & Workshop Excellence
</footer>

</div>

</body>
</html>
"""

# ---------------- FULL ADMIN UI (SINGLE SYSTEM - CLEAN) ----------------

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals Home</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{
margin:0;
font-family:Arial;
color:white;
background:url('https://images.unsplash.com/photo-1503376780353-7e6692767b70') center/cover fixed;
}

/* DARK OVERLAY */
.overlay{
display:flex;
min-height:100vh;
background:rgba(0,0,0,0.85);
}

/* SIDEBAR */
.sidebar{
width:230px;
background:rgba(0,0,0,0.92);
padding:20px;
border-right:1px solid #333;
}

.sidebar h2{
color:#25D366;
margin-bottom:20px;
}

.sidebar a{
display:block;
color:white;
padding:10px;
text-decoration:none;
margin:6px 0;
border-radius:6px;
background:#111;
transition:0.2s;
}

.sidebar a:hover{
background:#25D366;
color:black;
}

/* MAIN AREA */
.main{
flex:1;
padding:20px;
}

/* HEADER */
.header{
display:flex;
justify-content:space-between;
align-items:center;
padding:15px;
background:rgba(0,0,0,0.7);
border:1px solid #333;
border-radius:10px;
margin-bottom:15px;
}

.title{
font-size:22px;
color:#25D366;
font-weight:bold;
}

/* CARDS */
.card{
background:rgba(20,20,20,0.9);
padding:15px;
border-radius:10px;
border:1px solid #333;
margin-bottom:15px;
}

/* BUTTON */
.btn{
background:#25D366;
border:none;
padding:10px;
font-weight:bold;
cursor:pointer;
border-radius:5px;
}

/* INPUTS */
input,textarea{
width:100%;
padding:8px;
margin:5px 0;
background:#111;
color:white;
border:1px solid #333;
border-radius:5px;
}

/* TABLE */
table{
width:100%;
border-collapse:collapse;
margin-top:10px;
}

th,td{
border:1px solid #333;
padding:8px;
font-size:13px;
}

th{
background:#111;
color:#25D366;
}

a.action{
color:#25D366;
text-decoration:none;
margin-right:10px;
}

</style>
</head>

<body>

<div class="overlay">

    <!-- SIDEBAR -->
    <div class="sidebar">
        <h2>ERP MENU</h2>

        <a href="/admin">📊 Dashboard</a>
        <a href="/admin/students">👨‍🎓 Students</a>
        <a href="/admin/fees">💰 Fees</a>
        <a href="/admin/workshop">🚗 Workshop</a>
        <a href="/admin/files">📁 Files</a>
        <a href="/admin/reports">📄 Reports</a>
        <a href="/logout">🚪 Logout</a>
        <a href="/admin/messages">📩 Company Messages</a>
        <a href="/admin/companies">🏢 Companies</a>
        <a href="/admin/invoices">🧾 Invoices</a>
        
    </div>

    <!-- MAIN -->
    <div class="main">

        <div class="header">
            <div class="title">🔧 Automotive Workshop ERP</div>
        </div>

        <!-- DASHBOARD CONTENT WILL SHOW HERE -->
        {{content}}

    </div>

</div>

</body>
</html>
"""

#_______________Def______________
def send_company_email(to_email, subject, message):
    try:
        msg = f"Subject: {subject}\n\n{message}\n\n-- Automotive Professionals Pty Ltd"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, to_email, msg)
        server.quit()

    except Exception as e:
        print("Email failed:", e)

def workshop_wallet():

    conn = db()

    # TOTAL PAID
    income = conn.execute("""
        SELECT SUM(amount_paid) as total FROM workshop_jobs
    """).fetchone()["total"] or 0

    # TOTAL OUTSTANDING
    debt = conn.execute("""
        SELECT SUM(total_cost - amount_paid) as total
        FROM workshop_jobs
    """).fetchone()["total"] or 0

    # ACTIVE JOBS
    active = conn.execute("""
        SELECT COUNT(*) as c FROM workshop_jobs
        WHERE status='IN PROGRESS'
    """).fetchone()["c"]

    # OVERDUE JOBS
    overdue = conn.execute("""
        SELECT COUNT(*) as c FROM workshop_jobs
        WHERE date(deadline) < date('now')
        AND status != 'COMPLETED'
    """).fetchone()["c"]

    conn.close()

    return {
        "income": income,
        "debt": debt,
        "active": active,
        "overdue": overdue
    }

def get_settings():
    return db().execute("SELECT * FROM settings WHERE id=1").fetchone()


def update_settings(hero, whatsapp, courses, logo):
    conn = db()
    conn.execute("""
        UPDATE settings
        SET hero=?, whatsapp=?, courses=?, logo=?
        WHERE id=1
    """, (hero, whatsapp, courses, logo))
    conn.commit()
    conn.close()





#____________________Routes___________________
@app.route("/upload_file", methods=["POST"])
def upload_file():
    if not session.get("admin"):
        return redirect("/login")

    file = request.files.get("file")
    desc = request.form.get("desc")

    if file:
        filename = save(file)

        conn = db()
        conn.execute("""
            INSERT INTO files(filename, description, date)
            VALUES(?,?,?)
        """, (
            filename,
            desc,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        conn.close()

    return redirect("/admin")


@app.route("/admin/send_message", methods=["POST"])
def send_message():

    if not session.get("admin"):
        return redirect("/login")

    file = save(request.files.get("file"))

    sender = "Automotive Professionals Pty Ltd"
    receiver = request.form["receiver_email"]

    subject = request.form["subject"]
    message = request.form["message"]

    conn = db()
    conn.execute("""
        INSERT INTO company_messages(
            sender, receiver_email, subject, message, attachment, status, date
        ) VALUES(?,?,?,?,?,?,?)
    """, (
        sender,
        receiver,
        subject,
        message,
        file,
        "SENT",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

    Thread(
        target=send_company_email,
        args=(receiver, subject, message)
    ).start()

    return redirect("/admin/messages")
    
@app.route("/admin/messages")
def messages():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    msgs = conn.execute("""
        SELECT * FROM company_messages
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""

    <div class="card">
        <h2>📩 Company Communication Panel</h2>

        <form method="POST" action="/admin/send_message" enctype="multipart/form-data">

            <input name="receiver_email" placeholder="Receiver Email" required>
            <input name="subject" placeholder="Subject" required>
            <textarea name="message" placeholder="Message" required></textarea>

            <input type="file" name="file">

            <button class="btn">Send Message / Invoice</button>

        </form>
    </div>

    <div class="card">
        <h3>📬 Sent Messages</h3>

        {% for m in msgs %}
            <div style="background:#111;padding:10px;margin:8px 0;border-left:3px solid #25D366;">
                <b>{{m.subject}}</b><br>
                {{m.message}}<br>
                <small>{{m.receiver_email}} | {{m.date}}</small>
            </div>
        {% endfor %}

    </div>

    """, msgs=msgs)    
    
@app.route("/promote", methods=["POST"])
def promote():
    if not session.get("admin"):
        return redirect("/login")

    app_id = request.form["id"]

    conn = db()

    app_data = conn.execute(
        "SELECT * FROM applications WHERE id=?",
        (app_id,)
    ).fetchone()

    if app_data:
        conn.execute("""
            INSERT INTO students(name, phone, email, course, status, date)
            VALUES(?,?,?,?,?,?)
        """, (
            app_data["name"],
            app_data["phone"],
            app_data["email"],
            app_data["course"],
            "Active",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        conn.execute("DELETE FROM applications WHERE id=?", (app_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/")
def home():
    s = get_settings()

    courses = []
    for block in s["courses"].split("|"):
        courses += block.split(",")

    return render_template_string(
        HTML,
        h=s["hero"],
        courses=courses,
        logo=s["logo"],
        stats=get_stats()   # ✅ ADDED THIS
    )

@app.route("/apply", methods=["POST"])
def apply():
    f = save(request.files.get("file"))

    conn = db()
    conn.execute("""
        INSERT INTO applications(name,phone,email,course,file,date)
        VALUES(?,?,?,?,?,?)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["email"],
        request.form["course"],
        f,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

    Thread(
        target=send_email,
        args=(request.form["name"], request.form["email"], request.form["course"])
    ).start()

    return """
    <h2 style='font-family:Arial'>Application Submitted ✅</h2>
    <a href='/'>Back Home</a>
    """


@app.route("/admin/workshop", methods=["GET", "POST"])
def workshop():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    if request.method == "POST":

        invoice = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")

        labor = float(request.form["labor_cost"] or 0)
        parts = float(request.form["parts_cost"] or 0)
        paid = float(request.form["amount_paid"] or 0)

        conn.execute("""
            INSERT INTO workshop_jobs(
                invoice_no,
                customer_name,
                phone,
                vehicle,
                plate,
                problem,
                labor_cost,
                parts_cost,
                amount_paid,
                date_in,
                status
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            invoice,
            request.form["customer_name"],
            request.form["phone"],
            request.form["vehicle"],
            request.form["plate"],
            request.form["problem"],
            labor,
            parts,
            paid,
            datetime.now().strftime("%Y-%m-%d"),
            "IN PROGRESS"
        ))

        conn.commit()
        return redirect("/admin/workshop")

    jobs = conn.execute("""
        SELECT * FROM workshop_jobs ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""
    <style>
    body{
        margin:0;
        font-family:Arial;
        background:url('https://images.unsplash.com/photo-1503376780353-7e6692767b70') center/cover fixed;
        color:white;
    }

    .overlay{
        background:rgba(0,0,0,0.85);
        min-height:100vh;
        padding:20px;
    }

    .card{
        background:rgba(20,20,20,0.9);
        padding:15px;
        border-radius:10px;
        margin-bottom:15px;
        border:1px solid #333;
    }

    input,textarea{
        width:100%;
        padding:10px;
        margin:6px 0;
        background:#111;
        color:white;
        border:1px solid #333;
    }

    button{
        background:#25D366;
        padding:10px;
        border:none;
        font-weight:bold;
        cursor:pointer;
    }

    table{
        width:100%;
        border-collapse:collapse;
    }

    th,td{
        border:1px solid #333;
        padding:8px;
        font-size:12px;
    }

    th{background:#111;color:#25D366;}
    </style>

    <div class="overlay">

    <div class="card">
        <h2>🚗 Workshop Job Card</h2>

        <form method="POST">

            <input name="customer_name" placeholder="Customer Name" required>
            <input name="phone" placeholder="Phone" required>
            <input name="vehicle" placeholder="Vehicle" required>
            <input name="plate" placeholder="Plate Number" required>

            <textarea name="problem" placeholder="Problem"></textarea>

            <input name="labor_cost" placeholder="Labor Cost">
            <input name="parts_cost" placeholder="Parts Cost">
            <input name="amount_paid" placeholder="Amount Paid">

            <button>Create Job</button>
        </form>
    </div>

    <div class="card">
        <h3>📋 Jobs</h3>

        <table>
            <tr>
                <th>Invoice</th>
                <th>Customer</th>
                <th>Vehicle</th>
                <th>Plate</th>
                <th>Total</th>
                <th>Paid</th>
                <th>Balance</th>
                <th>Actions</th>
            </tr>

            {% for j in jobs %}
            <tr>
                <td>{{j.invoice_no}}</td>
                <td>{{j.customer_name}}</td>
                <td>{{j.vehicle}}</td>
                <td>{{j.plate}}</td>

                <td>R {{(j.labor_cost or 0) + (j.parts_cost or 0)}}</td>
                <td>R {{j.amount_paid}}</td>
                <td>R {{((j.labor_cost or 0) + (j.parts_cost or 0)) - (j.amount_paid or 0)}}</td>

                <!-- ✅ ADDED ONLY THIS -->
                <td>
                    <a href="/admin/invoice/{{j.id}}" class="btn">⬇ Download</a>
                    <a href="/admin/invoice/{{j.id}}" target="_blank">⬇ View</a>
                </td>

            </tr>
            {% endfor %}
        </table>
    </div>

    </div>
    """, jobs=jobs)


@app.route("/admin/workshop/jobcard", methods=["GET", "POST"])
def create_jobcard():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    if request.method == "POST":

        labor = float(request.form.get("labor_cost") or 0)
        parts = float(request.form.get("parts_cost") or 0)

        total = labor + parts

        conn.execute("""
            INSERT INTO workshop_jobs(
                invoice_no,
                customer_name,
                phone,
                address,
                vehicle_make,
                vehicle_model,
                registration,
                vin,
                mileage,
                problem,
                diagnosis,
                repair_notes,
                assigned_mechanic,
                labor_cost,
                parts_cost,
                total_cost,
                amount_paid,
                deadline,
                status,
                date_received,
                date_completed
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (

            f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",

            request.form["customer_name"],
            request.form["phone"],
            request.form["address"],

            request.form["vehicle_make"],
            request.form["vehicle_model"],
            request.form["registration"],
            request.form["vin"],
            request.form["mileage"],

            request.form["problem"],

            "",
            "",

            request.form["mechanic"],

            labor,
            parts,
            total,

            float(request.form.get("amount_paid") or 0),

            request.form["deadline"],

            "IN PROGRESS",

            datetime.now().strftime("%Y-%m-%d"),

            ""
        ))

        conn.commit()
        conn.close()

        return redirect("/admin/workshop")

    conn.close()

    return render_template_string("""

    <style>

    body{
        background:#0b0b0b;
        font-family:Arial;
        color:white;
    }

    .card{
        max-width:900px;
        margin:auto;
        margin-top:20px;
        background:#151515;
        padding:20px;
        border-radius:10px;
        border:1px solid #333;
    }

    input, textarea{
        width:100%;
        padding:12px;
        margin-top:8px;
        margin-bottom:10px;
        background:#111;
        color:white;
        border:1px solid #333;
    }

    button{
        width:100%;
        padding:12px;
        background:#25D366;
        border:none;
        font-weight:bold;
        cursor:pointer;
    }

    a{
        color:#25D366;
        text-decoration:none;
    }

    </style>

    <div class="card">

        <h2>🚗 Create Workshop Job Card</h2>

        <form method="POST">

            <input name="customer_name" placeholder="Customer Name" required>

            <input name="phone" placeholder="Phone Number" required>

            <input name="address" placeholder="Customer Address">

            <input name="vehicle_make" placeholder="Vehicle Make">

            <input name="vehicle_model" placeholder="Vehicle Model">

            <input name="registration" placeholder="Plate Number" required>

            <input name="vin" placeholder="VIN Number">

            <input name="mileage" placeholder="Mileage">

            <textarea name="problem" placeholder="Vehicle Problem"></textarea>

            <input name="mechanic" placeholder="Assigned Mechanic">

            <input name="labor_cost" placeholder="Labor Cost">

            <input name="parts_cost" placeholder="Parts Cost">

            <input name="amount_paid" placeholder="Amount Paid">

            <input type="date" name="deadline">

            <button>Create Job Card</button>

        </form>

        <br>

        <a href="/admin/workshop">⬅ Back to Workshop</a>

    </div>

    """)


@app.route("/admin/invoice/<int:job_id>")
def generate_invoice(job_id):

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    job = conn.execute("""
        SELECT * FROM workshop_jobs WHERE id=?
    """, (job_id,)).fetchone()

    conn.close()

    if not job:
        return "Job not found"

    labor = float(job["labor_cost"] or 0)
    parts = float(job["parts_cost"] or 0)
    paid = float(job["amount_paid"] or 0)

    total = labor + parts
    balance = total - paid

    invoice_no = job["invoice_no"]

    filename = f"{invoice_no}.pdf"
    filepath = os.path.join("uploads", filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # HEADER
    elements.append(Paragraph("AUTOMOTIVE PROFESSIONALS (PTY) LTD", styles["Title"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("INVOICE", styles["Title"]))
    elements.append(Spacer(1, 10))

    # INVOICE INFO
    elements.append(Paragraph(f"<b>Invoice No:</b> {invoice_no}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {job['date_in']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # CUSTOMER INFO
    elements.append(Paragraph(f"<b>Customer:</b> {job['customer_name']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Phone:</b> {job['phone']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Vehicle:</b> {job['vehicle']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Plate:</b> {job['plate']}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    # PROBLEM
    elements.append(Paragraph(f"<b>Problem:</b> {job['problem']}", styles["Normal"]))

    elements.append(Spacer(1, 15))

    # COST BREAKDOWN (TABLE STYLE FEEL)
    elements.append(Paragraph(f"<b>Labor Cost:</b> R {labor}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Parts Cost:</b> R {parts}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Total:</b> R {total}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Paid:</b> R {paid}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Balance Due:</b> R {balance}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Thank you for trusting our workshop 🙏", styles["Normal"]))

    doc.build(elements)

    return send_from_directory("uploads", filename, as_attachment=True)
    
@app.route("/admin")
def admin_home():

    if not session.get("admin"):
        return redirect("/login")

    content = render_template_string("""

    <div class="card">
        <h2>📊 Dashboard</h2>
        <p>Welcome to ERP Admin Panel</p>
    </div>

    """)

    return render_template_string(
        ADMIN_HTML,
        content=content
    )
    
@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if not session.get("admin"):
        return redirect("/login")

    s = get_settings()

    if request.method == "POST":
        conn = db()
        conn.execute("""
            UPDATE settings
            SET hero=?, whatsapp=?, courses=?
            WHERE id=1
        """, (
            request.form["hero"],
            request.form["whatsapp"],
            request.form["courses"]
        ))
        conn.commit()
        conn.close()

        return redirect("/settings")

    return render_template_string("""
    <h2>Settings Panel</h2>

    <form method="POST">
        <input name="hero" value="{{s['hero']}}">
        <input name="whatsapp" value="{{s['whatsapp']}}">
        <textarea name="courses">{{s['courses']}}</textarea>

        <button>Save</button>
    </form>
    """, s=s)

@app.route("/admin/workshop/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    job = conn.execute("SELECT * FROM workshop_jobs WHERE id=?", (job_id,)).fetchone()

    if request.method == "POST":

        conn.execute("""
            UPDATE workshop_jobs
            SET customer_name=?, phone=?, vehicle=?, plate=?, problem=?,
                labor_cost=?, parts_cost=?, amount_paid=?, status=?
            WHERE id=?
        """, (
            request.form["customer_name"],
            request.form["phone"],
            request.form["vehicle"],
            request.form["plate"],
            request.form["problem"],
            float(request.form["labor_cost"]),
            float(request.form["parts_cost"]),
            float(request.form["amount_paid"]),
            request.form["status"],
            job_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin/workshop")

    conn.close()

    return render_template_string("""
    <h2>Edit Job</h2>

    <form method="POST">

        <input name="customer_name" value="{{j.customer_name}}">
        <input name="phone" value="{{j.phone}}">
        <input name="vehicle" value="{{j.vehicle}}">
        <input name="plate" value="{{j.plate}}">
        <input name="problem" value="{{j.problem}}">

        <input name="labor_cost" value="{{j.labor_cost}}">
        <input name="parts_cost" value="{{j.parts_cost}}">
        <input name="amount_paid" value="{{j.amount_paid}}">

        <input name="status" value="{{j.status}}">

        <button>Save Changes</button>

    </form>
    """, j=job)


@app.route("/admin/student_statement/<int:student_id>")
def student_statement(student_id):

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    student = conn.execute("""
        SELECT * FROM students WHERE id=?
    """, (student_id,)).fetchone()

    payments = conn.execute("""
        SELECT * FROM payments WHERE student_id=?
    """, (student_id,)).fetchall()

    conn.close()

    filename = f"statement_{student_id}.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            f"<b>Automotive Professionals Pty Ltd</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(f"Student: {student['name']}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"Course: {student['course']}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"Date Registered: {student['date']}", styles["BodyText"])
    )

    elements.append(Spacer(1, 12))

    total_paid = 0

    for p in payments:
        total_paid += p["amount"]

        elements.append(
            Paragraph(
                f"Payment: {p['amount']} | Date: {p['date']}",
                styles["BodyText"]
            )
        )

    try:
        tuition = float(student["status"])
    except:
        tuition = 0

    balance = tuition - total_paid

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"<b>Total Paid:</b> {total_paid}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Balance:</b> {balance}", styles["BodyText"])
    )

    doc.build(elements)

    return send_from_directory(".", filename, as_attachment=True)
    
@app.route("/admin/students", methods=["GET", "POST"])
def admin_students():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    # ADD STUDENT
    if request.method == "POST":
        conn.execute("""
            INSERT INTO students(name, phone, email, course, status, date)
            VALUES(?,?,?,?,?,?)
        """, (
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["course"],
            request.form["tuition"],  # storing tuition temporarily
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()

    # GET STUDENTS
    students = conn.execute("""
        SELECT * FROM students ORDER BY id DESC
    """).fetchall()

    conn.close()

    # BUILD FINANCIAL DATA
    student_data = []

    for s in students:

        conn = db()

        paid = conn.execute("""
            SELECT SUM(amount) as total
            FROM payments
            WHERE student_id=?
        """, (s["id"],)).fetchone()["total"]

        payments = conn.execute("""
            SELECT * FROM payments
            WHERE student_id=?
            ORDER BY id DESC
        """, (s["id"],)).fetchall()

        conn.close()

        paid = paid if paid else 0

        try:
            tuition = float(s["status"])
        except:
            tuition = 0

        balance = tuition - paid

        student_data.append({
            "id": s["id"],
            "name": s["name"],
            "phone": s["phone"],
            "email": s["email"],
            "course": s["course"],
            "tuition": tuition,
            "paid": paid,
            "balance": balance,
            "payments": payments,
            "date": s["date"]
        })

    return render_template_string("""

    <style>
    body{
        font-family:Arial;
        color:white;
    }

    .card{
        background:rgba(20,20,20,0.9);
        padding:20px;
        border-radius:10px;
        margin-bottom:20px;
        border:1px solid #333;
    }

    input{
        width:100%;
        padding:10px;
        margin:6px 0;
        background:#111;
        color:white;
        border:1px solid #333;
    }

    button{
        padding:10px;
        background:#25D366;
        border:none;
        font-weight:bold;
        cursor:pointer;
    }

    table{
        width:100%;
        border-collapse:collapse;
        margin-top:15px;
    }

    th,td{
        border:1px solid #333;
        padding:8px;
        font-size:13px;
    }

    th{
        background:#111;
        color:#25D366;
    }

    .paid{
        color:lime;
        font-weight:bold;
    }

    .overdue{
        color:red;
        font-weight:bold;
    }

    .pdf-btn{
        display:inline-block;
        margin-top:8px;
        padding:6px 10px;
        background:#25D366;
        color:black;
        text-decoration:none;
        font-size:12px;
        border-radius:5px;
    }
    </style>

    <div class="card">

    <h2>🎓 Student Finance System</h2>

    <form method="POST">

        <input name="name" placeholder="Student Name" required>

        <input name="phone" placeholder="Phone Number" required>

        <input name="email" placeholder="Email Address" required>

        <input name="course" placeholder="Course / Department" required>

        <input name="tuition" placeholder="Total Tuition Amount" required>

        <button>Add Student</button>

    </form>

    </div>

    <div class="card">

    <h3>📊 Students Finance Overview</h3>

    <table>

        <tr>
            <th>Name</th>
            <th>Course</th>
            <th>Tuition</th>
            <th>Paid</th>
            <th>Balance</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>

        {% for s in students %}

        <tr>

            <td>{{s.name}}</td>

            <td>{{s.course}}</td>

            <td>{{s.tuition}}</td>

            <td>{{s.paid}}</td>

            <td>{{s.balance}}</td>

            <td>

                {% if s.balance > 0 %}
                    <span class="overdue">OVERDUE</span>
                {% else %}
                    <span class="paid">PAID</span>
                {% endif %}

            </td>

            <td>

                <!-- ADD PAYMENT -->

                <form method="POST" action="/admin/pay/{{s.id}}">

                    <input
                    name="amount"
                    placeholder="Payment Amount"
                    style="width:120px;">

                    <button>Add</button>

                </form>

                <br>

                <!-- PDF -->

                <a
                class="pdf-btn"
                href="/admin/student_statement/{{s.id}}">
                📄 Download Statement
                </a>

            </td>

        </tr>

        <!-- PAYMENT HISTORY -->

        <tr>
            <td colspan="7">

                <b>Payment History:</b>

                <ul>

                {% for p in s.payments %}

                    <li>
                        {{p.amount}} paid on {{p.date}}
                    </li>

                {% endfor %}

                </ul>

            </td>
        </tr>

        {% endfor %}

    </table>

    </div>

    """, students=student_data)

@app.route("/upload_logo", methods=["POST"])
def upload_logo():
    if not session.get("admin"):
        return redirect("/login")

    file = request.files.get("logo")
    if file:
        filename = save(file)
        conn = db()
        conn.execute("UPDATE settings SET logo=? WHERE id=1", (filename,))
        conn.commit()
        conn.close()

    return redirect("/admin")

@app.route("/admin/companies", methods=["GET", "POST"])
def companies():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    if request.method == "POST":
        conn.execute("""
            INSERT INTO companies(name,email,phone,address,balance,date)
            VALUES(?,?,?,?,?,?)
        """, (
            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["address"],
            0,
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()

    data = conn.execute("SELECT * FROM companies").fetchall()
    conn.close()

    return render_template_string("""

    <div class="card">
        <h2>🏢 Company Registry</h2>

        <form method="POST">
            <input name="name" placeholder="Company Name">
            <input name="email" placeholder="Email">
            <input name="phone" placeholder="Phone">
            <input name="address" placeholder="Address">
            <button class="btn">Add Company</button>
        </form>
    </div>

    <div class="card">
        <h3>Registered Companies</h3>

        {% for c in data %}
            <div style="padding:10px;background:#111;margin:6px 0;border-left:3px solid #25D366;">
                <b>{{c.name}}</b><br>
                {{c.email}} | {{c.phone}}<br>
                Balance: R{{c.balance}}
            </div>
        {% endfor %}
    </div>

    """, data=data)
@app.route("/admin/create_invoice", methods=["POST"])
def create_invoice():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    company_id = request.form["company_id"]
    amount = float(request.form["amount"])
    desc = request.form["description"]

    invoice_no = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")

    conn.execute("""
        INSERT INTO invoices(
            invoice_no, company_id, description, amount, paid, status, pdf, date
        ) VALUES(?,?,?,?,?,?,?,?)
    """, (
        invoice_no,
        company_id,
        desc,
        amount,
        0,
        "UNPAID",
        "",
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return redirect("/admin/invoices")
    
@app.route("/admin/invoices")
def invoices():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    data = conn.execute("""
        SELECT i.*, c.name as company_name
        FROM invoices i
        LEFT JOIN companies c ON i.company_id = c.id
        ORDER BY i.id DESC
    """).fetchall()

    companies = conn.execute("SELECT * FROM companies").fetchall()

    conn.close()

    return render_template_string("""

    <div class="card">
        <h2>🧾 Create Invoice</h2>

        <form method="POST" action="/admin/create_invoice">

            <select name="company_id">
                {% for c in companies %}
                    <option value="{{c.id}}">{{c.name}}</option>
                {% endfor %}
            </select>

            <input name="description" placeholder="Description">
            <input name="amount" placeholder="Amount">

            <button class="btn">Create Invoice</button>
        </form>
    </div>

    <div class="card">
        <h3>📄 Invoices</h3>

        {% for i in data %}
            <div style="background:#111;padding:10px;margin:6px 0;border-left:3px solid #25D366;">
                <b>{{i.invoice_no}}</b><br>
                Company: {{i.company_name}}<br>
                Amount: R{{i.amount}} | Paid: R{{i.paid}}<br>
                Status: {{i.status}}
            </div>
        {% endfor %}
    </div>

    """, data=data, companies=companies)
    
@app.route("/admin/pay/<int:student_id>", methods=["POST"])
def add_payment(student_id):

    if not session.get("admin"):
        return redirect("/login")

    amount = float(request.form["amount"])

    conn = db()
    conn.execute("""
        INSERT INTO payments(student_id, amount, date)
        VALUES(?,?,?)
    """, (
        student_id,
        amount,
        datetime.now().strftime("%Y-%m-%d")
    ))
    conn.commit()
    conn.close()

    return redirect("/admin/students")
    
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if not session.get("admin"):
        return redirect("/login")

    conn = db()

    s = conn.execute("""
        SELECT * FROM settings WHERE id=1
    """).fetchone()

    data = conn.execute("""
        SELECT * FROM applications
        ORDER BY id DESC
    """).fetchall()

    # SAVE SETTINGS
    if request.method == "POST":

        conn.execute("""
            UPDATE settings
            SET hero=?, whatsapp=?, courses=?
            WHERE id=1
        """, (
            request.form["hero"],
            request.form["whatsapp"],
            request.form["courses"]
        ))

        conn.commit()

        return redirect("/admin")

    conn.close()

    content = render_template_string("""

    <div class="card">

        <h2>⚙ Institution Settings</h2>

        <form method="POST">

            <input
            name="hero"
            value="{{s['hero']}}"
            placeholder="Institution Name">

            <input
            name="whatsapp"
            value="{{s['whatsapp']}}"
            placeholder="WhatsApp Number">

            <textarea
            name="courses"
            rows="6"
            placeholder="Courses">{{s['courses']}}</textarea>

            <button class="btn">Save Settings</button>

        </form>

    </div>

    <div class="card">

        <h2>📥 Applications</h2>

        <table>

            <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>Course</th>
                <th>Date</th>
            </tr>

            {% for row in data %}

            <tr>
                <td>{{row['name']}}</td>
                <td>{{row['phone']}}</td>
                <td>{{row['course']}}</td>
                <td>{{row['date']}}</td>
            </tr>

            {% endfor %}

        </table>

    </div>

    """, s=s, data=data)

    return render_template_string(
        ADMIN_HTML,
        content=content
    )
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")

    return """
    <form method='POST'>
        <input name='password' placeholder='Admin Password'>
        <button>Login</button>
    </form>
    """


@app.route("/uploads/<file>")
def files(file):
    return send_from_directory(UPLOAD_FOLDER, file)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


