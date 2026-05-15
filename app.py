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
app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM_SECURE_KEY"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

ADMIN_PASSWORD = "1234"

MAIL_SENDER = "takernkambule@gmail.com"
MAIL_PASSWORD = "your_app_password"

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

    # ---------------- WORKSHOP JOBS (FULL ERP VERSION) ----------------
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

# ---------------- UI (UPGRADED PROFESSIONAL FIXED) ----------------
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

/* DARK OVERLAY */
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
backdrop-filter:blur(8px);
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
font-weight:500;
}

.nav a:hover{
color:#25D366;
}

/* HERO */
.hero{
text-align:center;
padding:70px 20px 30px;
}

.hero-box{
display:inline-block;
padding:25px 35px;
border-radius:15px;
background:rgba(0,0,0,0.65);
border:1px solid #333;
backdrop-filter:blur(8px);
}

.hero h1{
margin:0;
color:#25D366;
font-size:42px;
}

.hero p{
margin-top:10px;
opacity:0.8;
}

/* DASHBOARD STATS (NEW - ADDED ONLY) */
.dashboard{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:20px;
padding:20px 0;
}

.stat-box{
background:rgba(20,20,20,0.88);
padding:18px;
width:200px;
border-radius:12px;
border:1px solid #333;
text-align:center;
}

.stat-box h2{
margin:5px 0;
color:#25D366;
}

/* DASHBOARD MINI BADGE */
.badge{
display:inline-block;
margin-top:10px;
padding:6px 12px;
font-size:12px;
background:#25D366;
color:black;
border-radius:20px;
font-weight:bold;
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
background:rgba(20,20,20,0.88);
padding:22px;
width:340px;
border-radius:15px;
border:1px solid #333;
transition:0.3s;
}

.card:hover{
transform:translateY(-6px);
border-color:#25D366;
}

/* INPUT */
input,select{
width:100%;
padding:10px;
margin:8px 0;
background:#111;
color:white;
border:1px solid #333;
border-radius:6px;
}

input:focus,select:focus{
border-color:#25D366;
outline:none;
}

/* BUTTON */
.btn{
background:#25D366;
padding:12px;
width:100%;
border:none;
cursor:pointer;
font-weight:bold;
border-radius:6px;
color:black;
}

.btn:hover{
background:#1fae55;
}

/* COURSE BLOCK */
.course{
background:#111;
padding:10px;
margin:6px 0;
border-left:3px solid #25D366;
border-radius:5px;
font-size:14px;
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

        {% if session.admin %}
        <div class="badge">ADMIN MODE ACTIVE</div>
        {% endif %}
    </div>
</div>

<!-- ✅ DASHBOARD STATS (ADDED ONLY HERE) -->
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

<!-- CONTENT -->
<div class="container">

    <!-- APPLY -->
    <div class="card">

        <h3>Student Application</h3>

        <div class="slot" style="opacity:0.8">
            Welcome To Automotive Professionals.<br>
            Register below to join our institution.
        </div>

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

    <!-- COURSES -->
    <div class="card">

        <h3>Available Courses</h3>

        {% for c in courses %}
        <div class="course">{{c}}</div>
        {% endfor %}

    </div>

</div>

<footer>

© 2026 Automotive Professionals (Pty) Ltd | Training Excellence in Eswatini

<br><br>

<div style="display:flex;justify-content:center;gap:15px;flex-wrap:wrap;">

    <a href="https://facebook.com" style="color:white;text-decoration:none;">📘 Facebook</a>
    <a href="https://wa.me/26876783891" style="color:#25D366;text-decoration:none;">💬 WhatsApp</a>
    <span>📞 +268 7678 3891</span>

</div>

</footer>

</div>

</body>
</html>
"""
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

# ---------------- ROUTES ----------------

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

    # ADD CAR / JOB
    if request.method == "POST":

        invoice = "INV" + datetime.now().strftime("%Y%m%d%H%M%S")

        conn.execute("""
            INSERT INTO workshop_jobs(
                invoice_no, customer, phone, plate, vehicle, problem,
                labor_cost, parts_cost, amount_paid, date_in, status
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            invoice,
            request.form["customer"],
            request.form["phone"],
            request.form["plate"],
            request.form["vehicle"],
            request.form["problem"],
            float(request.form["labor_cost"]),
            float(request.form["parts_cost"]),
            float(request.form["amount_paid"]),
            datetime.now().strftime("%Y-%m-%d"),
            "IN PROGRESS"
        ))

        conn.commit()

    jobs = conn.execute("SELECT * FROM workshop_jobs ORDER BY id DESC").fetchall()
    conn.close()

    return render_template_string("""
    <style>
    body{
        margin:0;
        font-family:Arial;
        background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc') center/cover fixed;
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
    }

    input{
        width:100%;
        padding:10px;
        margin:5px 0;
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
    }

    th,td{
        border:1px solid #333;
        padding:8px;
        font-size:12px;
    }

    th{background:#111;color:#25D366;}

    .back{
        display:inline-block;
        margin-bottom:10px;
        color:#25D366;
        text-decoration:none;
    }
    </style>

    <div class="overlay">

    <a href="/admin" class="back">⬅ Back to Dashboard</a>

    <div class="card">
        <h2>🚗 Add Workshop Job</h2>

        <form method="POST">

            <input name="customer" placeholder="Customer Name" required>
            <input name="phone" placeholder="Phone" required>
            <input name="plate" placeholder="Plate Number" required>
            <input name="vehicle" placeholder="Vehicle Model" required>
            <input name="problem" placeholder="Problem Description" required>

            <input name="labor_cost" placeholder="Labor Cost" required>
            <input name="parts_cost" placeholder="Parts Cost" required>
            <input name="amount_paid" placeholder="Amount Paid" required>

            <button>Add Job</button>

        </form>
    </div>

    <div class="card">

    <h3>📋 Active Jobs</h3>

    <table>
        <tr>
            <th>Invoice</th>
            <th>Customer</th>
            <th>Vehicle</th>
            <th>Plate</th>
            <th>Cost</th>
            <th>Paid</th>
            <th>Balance</th>
            <th>Status</th>
        </tr>

        {% for j in jobs %}

        <tr>
            <td>{{j.invoice_no}}</td>
            <td>{{j.customer}}</td>
            <td>{{j.vehicle}}</td>
            <td>{{j.plate}}</td>

            <td>R {{j.labor_cost + j.parts_cost}}</td>
            <td>R {{j.amount_paid}}</td>

            <td>
                R {{(j.labor_cost + j.parts_cost) - j.amount_paid}}
            </td>

            <td>{{j.status}}</td>
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

    # CREATE JOB CARD
    if request.method == "POST":

        labor = float(request.form.get("labor_cost") or 0)
        parts = float(request.form.get("parts_cost") or 0)

        total = labor + parts

        conn.execute("""
            INSERT INTO workshop_jobs(
                customer_name,
                phone,
                address,
                vehicle_make,
                vehicle_model,
                registration,
                vin,
                mileage,
                issue,
                diagnosis,
                repair_notes,
                assigned_mechanic,
                labor_cost,
                parts_cost,
                total_cost,
                amount_paid,
                deadline,
                status,
                date_received
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form["customer_name"],
            request.form["phone"],
            request.form["address"],
            request.form["vehicle_make"],
            request.form["vehicle_model"],
            request.form["registration"],
            request.form["vin"],
            request.form["mileage"],
            request.form["issue"],
            "",
            "",
            request.form["mechanic"],
            labor,
            parts,
            total,
            0,
            request.form["deadline"],
            "IN PROGRESS",
            datetime.now().strftime("%Y-%m-%d")
        ))

        conn.commit()
        return redirect("/admin/workshop_dashboard")

    return render_template_string("""

    <style>

    body{
        font-family:Arial;
        background:#0b0b0b;
        color:white;
        margin:0;
    }

    .card{
        background:#151515;
        padding:20px;
        margin:20px;
        border-radius:10px;
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
        padding:12px;
        border:none;
        font-weight:bold;
        cursor:pointer;
    }

    </style>

    <div class="card">

    <h2>🔧 Create Workshop Job Card</h2>

    <form method="POST">

        <input name="customer_name" placeholder="Customer Name" required>
        <input name="phone" placeholder="Phone Number" required>
        <input name="address" placeholder="Address">

        <input name="vehicle_make" placeholder="Vehicle Make (Toyota, BMW...)">
        <input name="vehicle_model" placeholder="Vehicle Model">
        <input name="registration" placeholder="Plate Number" required>
        <input name="vin" placeholder="VIN Number">
        <input name="mileage" placeholder="Mileage">

        <textarea name="issue" placeholder="Problem Description"></textarea>

        <input name="mechanic" placeholder="Assign Mechanic">

        <input name="labor_cost" placeholder="Labor Cost (R)">
        <input name="parts_cost" placeholder="Parts Cost (R)">

        <input name="deadline" type="date">

        <button>Create Job Card</button>

    </form>

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

    if not job:
        return "Job not found"

    invoice_number = f"INV-{job_id:05d}"

    labor = job["labor_cost"] or 0
    parts = job["parts_cost"] or 0
    paid = job["amount_paid"] or 0

    total = labor + parts
    balance = total - paid

    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            invoice_number TEXT,
            customer_name TEXT,
            plate TEXT,
            labor REAL,
            parts REAL,
            total REAL,
            paid REAL,
            balance REAL,
            date TEXT
        )
    """)

    conn.execute("""
        INSERT INTO invoices(
            job_id, invoice_number, customer_name,
            plate, labor, parts, total,
            paid, balance, date
        )
        VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        job_id,
        invoice_number,
        job["customer_name"],
        job["registration"],
        labor,
        parts,
        total,
        paid,
        balance,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    filename = f"{invoice_number}.pdf"
    filepath = os.path.join("uploads", filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AUTOMOTIVE WORKSHOP INVOICE", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Invoice Number: {invoice_number}", styles["Normal"]))
    content.append(Paragraph(f"Customer: {job['customer_name']}", styles["Normal"]))
    content.append(Paragraph(f"Phone: {job['phone']}", styles["Normal"]))
    content.append(Paragraph(
        f"Vehicle: {job['vehicle_make']} {job['vehicle_model']}",
        styles["Normal"]
    ))
    content.append(Paragraph(f"Plate: {job['registration']}", styles["Normal"]))

    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Labor Cost: R {labor}", styles["Normal"]))
    content.append(Paragraph(f"Parts Cost: R {parts}", styles["Normal"]))
    content.append(Paragraph(f"TOTAL: R {total}", styles["Normal"]))
    content.append(Paragraph(f"Paid: R {paid}", styles["Normal"]))
    content.append(Paragraph(f"Balance: R {balance}", styles["Normal"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("Thank you for choosing our workshop!", styles["Normal"]))

    doc.build(content)

    return send_from_directory("uploads", filename, as_attachment=True)
    
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


# ---------------- FIXED ADMIN HTML (ADDED) ----------------
ADMIN_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
<title>ERP Admin Panel</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{
margin:0;
font-family:Arial;
background:url('https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0') center/cover fixed;
color:white;
}

.overlay{
display:flex;
min-height:100vh;
background:rgba(0,0,0,0.85);
}

/* SIDEBAR */
.sidebar{
width:220px;
background:rgba(0,0,0,0.9);
padding:20px;
border-right:1px solid #333;
}

.sidebar h2{
color:#25D366;
}

.sidebar a{
display:block;
color:white;
padding:10px;
text-decoration:none;
margin:5px 0;
border-radius:6px;
background:#111;
}

.sidebar a:hover{
background:#25D366;
color:black;
}

/* MAIN */
.main{
flex:1;
padding:20px;
}

/* CARDS */
.card{
background:rgba(20,20,20,0.9);
padding:15px;
margin-bottom:15px;
border-radius:10px;
border:1px solid #333;
}

.btn{
background:#25D366;
border:none;
padding:10px;
width:100%;
cursor:pointer;
font-weight:bold;
}
</style>

</head>

<body>

<div class="overlay">

    <div class="sidebar">
        <h2>ERP MENU</h2>

        <a href="/admin">📊 Dashboard</a>
        <a href="/admin/students">👨‍🎓 Students</a>
        <a href="/admin/fees">💰 Fees</a>
        <a href="/admin/workshop">🚗 Workshop</a>
        <a href="/admin/files">📁 Files</a>
        <a href="/admin/reports">📄 Reports</a>
        <a href="/logout">🚪 Logout</a>
    </div>

    <div class="main">
        {{content}}
    </div>

</div>

</body>
</html>
"""
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Workshop Admin Panel</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{
margin:0;
font-family:Arial;
color:white;
background:url('https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0') center/cover fixed;
}

.overlay{
background:rgba(0,0,0,0.85);
min-height:100vh;
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
}

.title{
font-size:22px;
color:#25D366;
font-weight:bold;
}

/* GRID */
.grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
gap:20px;
margin-top:20px;
}

/* CARD */
.card{
background:rgba(20,20,20,0.9);
padding:15px;
border-radius:10px;
border:1px solid #333;
}

.card h3{
color:#25D366;
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

/* BUTTON */
.btn{
background:#25D366;
border:none;
padding:10px;
width:100%;
font-weight:bold;
cursor:pointer;
}

input,textarea{
width:100%;
padding:8px;
margin:5px 0;
background:#111;
color:white;
border:1px solid #333;
}

</style>
</head>

<body>

<div class="overlay">

<div class="header">
    <div class="title">🔧 Automotive Workshop Admin</div>
    <a href="/logout" style="color:white;">Logout</a>
</div>

<div class="grid">

    <!-- SETTINGS -->
    <div class="card">
        <h3>Institution Settings</h3>
        <form method="POST" action="/admin">
            <input name="hero" value="{{s['hero']}}">
            <input name="whatsapp" value="{{s['whatsapp']}}">
            <textarea name="courses">{{s['courses']}}</textarea>
            <button class="btn">Save Settings</button>
        </form>
    </div>

    <!-- APPLICATIONS -->
    <div class="card">
        <h3>New Applications</h3>
        <table>
        <tr><th>Name</th><th>Course</th><th>Date</th></tr>
        {% for row in data %}
        <tr>
            <td>{{row['name']}}</td>
            <td>{{row['course']}}</td>
            <td>{{row['date']}}</td>
        </tr>
        {% endfor %}
        </table>
    </div>

    <!-- STUDENTS -->
    <div class="card">
        <h3>Registered Students</h3>
        <p style="opacity:0.7">(Feature ready for expansion)</p>
    </div>

    <!-- FILES -->
    <div class="card">
        <h3>Institution Files</h3>

        <form method="POST" action="/upload_file" enctype="multipart/form-data">
            <input type="file" name="file">
            <input name="desc" placeholder="File description">
            <button class="btn">Upload File</button>
        </form>

    </div>

</div>

</div>

</body>
</html>
"""

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if not session.get("admin"):
        return redirect("/login")

    s = get_settings()

    # UPDATE SETTINGS
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
        return redirect("/admin")

    conn = db()

    # APPLICATIONS
    applications = conn.execute("""
        SELECT * FROM applications ORDER BY id DESC
    """).fetchall()

    # STUDENTS
    students = conn.execute("""
        SELECT * FROM students ORDER BY id DESC
    """).fetchall()

    # FILES
    files = conn.execute("""
        SELECT * FROM files ORDER BY id DESC
    """).fetchall()

    conn.close()

    # 📊 SIMPLE STATS (for dashboard later)
    stats = {
        "applications": len(applications),
        "students": len(students),
        "files": len(files)
    }

    # RENDER INSIDE ERP LAYOUT
    content = render_template_string(
        ADMIN_HTML,
        s=s,
        data=applications,
        students=students,
        files=files,
        stats=stats
    )

    return render_template_string(
        ADMIN_LAYOUT,
        content=content
    )

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


