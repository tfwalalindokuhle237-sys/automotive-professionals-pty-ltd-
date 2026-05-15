from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import sqlite3
import os
from datetime import datetime
from threading import Thread
import smtplib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_RANDOM_SECURE_KEY"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

ADMIN_PASSWORD = "1234"

MAIL_SENDER = "your_email@gmail.com"
MAIL_PASSWORD = "your_app_password"


# ---------------- DATABASE ----------------
def db():
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = db()
    c = conn.cursor()

    # applications
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

    # settings (LIVE editable later in admin)
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        hero TEXT,
        whatsapp TEXT,
        courses TEXT
    )
    """)

    # DEFAULT DATA (YOUR COURSES)
    c.execute("""
    INSERT OR IGNORE INTO settings VALUES (
        1,
        'Automotive Training Centre',
        '26876783891',
        'Level 3 - Full Course (18 Months): Heavy Plant Mechanics, Light Motor Mechanics | 6 Month Course: Welding | Short Courses: Engine Management & Diagnosis, General Maintenance'
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


def settings():
    return db().execute("SELECT * FROM settings WHERE id=1").fetchone()


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


# ---------------- UI (UPGRADED PROFESSIONAL) ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals Pty Ltd</title>

<style>
body{
margin:0;
font-family:Segoe UI;
color:white;
background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc') center/cover fixed;
}

.overlay{
background:rgba(0,0,0,0.8);
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
}

.nav a{
color:white;
margin:0 10px;
text-decoration:none;
}

.logo{
width:45px;
height:45px;
border-radius:50%;
background:#222;
border:2px solid #25D366;
}

/* HERO */
.hero{
text-align:center;
padding:70px 20px;
}

.hero h1{
color:#25D366;
font-size:42px;
margin:0;
}

/* LAYOUT */
.container{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:20px;
padding:30px;
}

/* CARD */
.card{
background:rgba(20,20,20,0.85);
padding:20px;
width:320px;
border-radius:12px;
border:1px solid #333;
}

/* INPUT */
input,select{
width:100%;
padding:10px;
margin:6px 0;
background:#111;
color:white;
border:1px solid #333;
}

/* BUTTON */
.btn{
background:#25D366;
padding:10px;
width:100%;
border:none;
cursor:pointer;
font-weight:bold;
}

/* COURSES */
.course{
background:#111;
padding:8px;
margin:5px 0;
border-left:3px solid #25D366;
}

/* PROFILE SLOT */
.slot{
text-align:center;
padding:15px;
border:1px dashed #444;
margin-bottom:10px;
color:#aaa;
}
</style>
</head>

<body>

<div class="overlay">

<div class="nav">
    <div style="display:flex;align-items:center;gap:10px;">
        <div class="logo"></div>
        <b>Automotive Professionals</b>
    </div>
    <div>
        <a href="/">Home</a>
        <a href="/admin">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>{{h}}</h1>
</div>

<div class="container">

<!-- APPLY -->
<div class="card">

<h3>Student Application</h3>

<div class="slot">Institution Logo (Admin Upload Later)</div>

<form method="POST" action="/apply" enctype="multipart/form-data">

<input name="name" placeholder="Full Name" required>
<input name="phone" placeholder="Phone Number" required>
<input name="email" placeholder="Email" required>

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
<h3>Courses</h3>

{% for c in courses %}
<div class="course">{{c}}</div>
{% endfor %}

</div>

</div>
</div>

</body>
</html>
"""


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    s = settings()
    return render_template_string(HTML, h=s["hero"], courses=s["courses"].split(","))


@app.route("/apply", methods=["POST"])
def apply():
    f = save(request.files.get("file"))

    conn = db()
    conn.execute("""
        INSERT INTO applications VALUES(NULL,?,?,?,?,?,?)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["email"],
        request.form["course"],
        f,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()

    Thread(target=send_email,
           args=(request.form["name"], request.form["email"], request.form["course"])).start()

    return """
    <h2 style='font-family:Arial'>Application Submitted ✅</h2>
    <a href='/'>Back Home</a>
    """


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/")

    data = db().execute("SELECT * FROM applications ORDER BY id DESC").fetchall()

    html = "<h1>ADMIN DASHBOARD</h1><table border='1' style='width:100%;font-family:Arial'>"
    html += "<tr><th>Name</th><th>Phone</th><th>Course</th><th>Date</th></tr>"

    for r in data:
        html += f"<tr><td>{r['name']}</td><td>{r['phone']}</td><td>{r['course']}</td><td>{r['date']}</td></tr>"

    html += "</table>"
    return html


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
