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
        courses TEXT,
        logo TEXT
    )
    """)

    # DEFAULT DATA (YOUR UPDATED STRUCTURE)
    c.execute("""
    INSERT OR IGNORE INTO settings VALUES (
        1,
        'Automotive Training Centre',
        '26876783891',
        'Level 3 18 Months - Heavy Plant Mechanics,Light Motor Mechanics | 6 Month - Welding | Short Courses- Engine Management And Diagnosis,General Maintenance',
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


def get_settings():
    conn = db()
    data = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    conn.close()
    return data


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
        {% if logo %}
            <img src="/uploads/{{logo}}" class="logo">
        {% else %}
            <div class="logo"></div>
        {% endif %}
        <b>Automotive Professionals</b>
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
    s = get_settings()

    courses = []
    for block in s["courses"].split("|"):
        courses += block.split(",")

    return render_template_string(HTML,
        h=s["hero"],
        courses=courses,
        logo=s["logo"]
    )
    
def get_settings():
    return db().execute("SELECT * FROM settings WHERE id=1").fetchone()


def update_settings(hero, whatsapp, courses, logo):
    db().execute("""
    UPDATE settings
    SET hero=?, whatsapp=?, courses=?, logo=?
    WHERE id=1
    """, (hero, whatsapp, courses, logo))
    db().commit()
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


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/")

    s = get_settings()

    if request.method == "POST":
        hero = request.form["hero"]
        whatsapp = request.form["whatsapp"]
        courses = request.form["courses"]

        update_settings(hero, whatsapp, courses, s["logo"])
        return redirect("/admin")

    data = db().execute("SELECT * FROM applications ORDER BY id DESC").fetchall()

    return render_template_string("""
    <style>
    body{font-family:Arial;background:#111;color:white;padding:20px}
    input,textarea{width:100%;padding:10px;margin:5px 0}
    .box{background:#1c1c1c;padding:15px;border-radius:10px;margin-bottom:20px}
    table{width:100%;border-collapse:collapse}
    th,td{border:1px solid #333;padding:8px}
    th{background:#25D366;color:black}
    </style>

    <h1>ADMIN CONTROL PANEL</h1>

    <div class="box">
        <h3>Edit Website Live</h3>
        <form method="POST">
            <input name="hero" value="{{s.hero}}">
            <input name="whatsapp" value="{{s.whatsapp}}">
            <textarea name="courses">{{s.courses}}</textarea>
            <button>Save</button>
        </form>
    </div>

    <div class="box">
        <h3>Applications</h3>
        <table>
            <tr><th>Name</th><th>Phone</th><th>Course</th><th>Date</th></tr>
            {% for r in data %}
            <tr>
                <td>{{r.name}}</td>
                <td>{{r.phone}}</td>
                <td>{{r.course}}</td>
                <td>{{r.date}}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    """, s=s, data=data)

@app.route("/upload_logo", methods=["POST"])
def upload_logo():
    if not session.get("admin"):
        return redirect("/login")

    file = request.files.get("logo")
    if file:
        filename = save(file)
        db().execute("UPDATE settings SET logo=? WHERE id=1", (filename,))
        db().commit()

    return redirect("/admin")

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
