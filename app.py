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
background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc') center/cover fixed;
}

/* DARK OVERLAY */
.overlay{
background:rgba(0,0,0,0.82);
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

.nav-left{
display:flex;
align-items:center;
gap:10px;
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
padding:80px 20px 40px;
}

.hero-box{
display:inline-block;
padding:25px 35px;
border-radius:15px;
background:rgba(0,0,0,0.6);
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
background:rgba(20,20,20,0.85);
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

/* PROFILE SLOT */
.slot{
text-align:center;
padding:15px;
border:1px dashed #444;
margin-bottom:10px;
color:#aaa;
border-radius:10px;
}

/* FOOTER */
footer{
text-align:center;
padding:20px;
opacity:0.6;
font-size:13px;
margin-top:20px;
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

<!-- CONTENT -->
<div class="container">

    <!-- APPLY -->
    <div class="card">

        <h3>Student Application</h3>

        <div class="slot">
            Welcome To Automotive Professionals,continue below to proceed  with your registrations, all the best :)
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

    <div style="display:flex;justify-content:center;align-items:center;gap:18px;flex-wrap:wrap;">

        <!-- FACEBOOK -->
        <a href="https://facebook.com" target="_blank"
        style="color:white;text-decoration:none;font-size:15px;">
            📘 Automotive Professionals Pty Ltd
        </a>

        <!-- WHATSAPP -->
        <a href="https://wa.me/26876783891" target="_blank"
        style="color:#25D366;text-decoration:none;font-size:15px;">
            💬 WhatsApp
        </a>

        <!-- PHONE -->
        <span style="font-size:15px;">
            📞 +268 7678 3891
        </span>

    </div>
</footer>

</div>

</body>
</html>
"""

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
        logo=s["logo"]
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


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if not session.get("admin"):
        return redirect("/login")

    s = get_settings()

    if request.method == "POST":
        hero = request.form["hero"]
        whatsapp = request.form["whatsapp"]
        courses = request.form["courses"]

        conn = db()
        conn.execute("""
            UPDATE settings
            SET hero=?, whatsapp=?, courses=?
            WHERE id=1
        """, (hero, whatsapp, courses))
        conn.commit()
        conn.close()

        return redirect("/settings")

    return render_template_string("""
    <h2>Settings Panel</h2>

    <form method="POST">
        <input name="hero" value="{{s.hero}}" placeholder="Hero Text">
        <input name="whatsapp" value="{{s.whatsapp}}" placeholder="WhatsApp">
        <textarea name="courses">{{s.courses}}</textarea>

        <button>Save</button>
    </form>
    """, s=s)

return render_template_string("""

<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals Admin</title>

<style>

body{
margin:0;
font-family:Segoe UI, Arial;
background:
linear-gradient(rgba(0,0,0,0.88),rgba(0,0,0,0.88)),
url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1600') center/cover fixed;
color:white;
}

/* TOPBAR */
.topbar{
display:flex;
justify-content:space-between;
align-items:center;
padding:18px 30px;
background:rgba(0,0,0,0.85);
border-bottom:2px solid #25D366;
position:sticky;
top:0;
z-index:100;
backdrop-filter:blur(10px);
}

.topbar h1{
margin:0;
font-size:24px;
color:#25D366;
}

.topbar a{
color:white;
text-decoration:none;
margin-left:15px;
font-weight:600;
}

.topbar a:hover{
color:#25D366;
}

/* MAIN */
.wrapper{
padding:30px;
}

/* STATS */
.stats{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:20px;
margin-bottom:30px;
}

.stat-card{
background:rgba(20,20,20,0.92);
padding:25px;
border-radius:15px;
border:1px solid #333;
box-shadow:0 0 20px rgba(0,0,0,0.4);
}

.stat-card h2{
margin:0;
font-size:34px;
color:#25D366;
}

.stat-card p{
margin-top:8px;
opacity:0.7;
}

/* BOX */
.box{
background:rgba(18,18,18,0.95);
padding:25px;
border-radius:16px;
border:1px solid #333;
margin-bottom:25px;
box-shadow:0 0 20px rgba(0,0,0,0.3);
}

.box h3{
margin-top:0;
color:#25D366;
font-size:22px;
}

/* INPUTS */
input,textarea,select{
width:100%;
padding:12px;
margin-top:10px;
margin-bottom:15px;
background:#111;
border:1px solid #333;
border-radius:8px;
color:white;
box-sizing:border-box;
}

input:focus,textarea:focus,select:focus{
outline:none;
border-color:#25D366;
}

/* BUTTON */
button{
background:#25D366;
color:black;
border:none;
padding:12px 20px;
font-weight:bold;
border-radius:8px;
cursor:pointer;
transition:0.3s;
}

button:hover{
background:#1db954;
transform:translateY(-2px);
}

/* TABLE */
.table-wrap{
overflow-x:auto;
}

table{
width:100%;
border-collapse:collapse;
margin-top:15px;
}

th{
background:#25D366;
color:black;
padding:14px;
font-size:14px;
text-align:left;
}

td{
padding:12px;
border-bottom:1px solid #333;
background:rgba(255,255,255,0.02);
font-size:14px;
}

/* BADGES */
.badge{
padding:6px 10px;
border-radius:30px;
font-size:12px;
font-weight:bold;
display:inline-block;
}

.active{
background:#25D366;
color:black;
}

.pending{
background:orange;
color:black;
}

/* FILE BUTTON */
.file-btn{
background:#111;
padding:8px 12px;
border-radius:6px;
text-decoration:none;
color:#25D366;
border:1px solid #25D366;
font-size:13px;
}

/* DEPARTMENTS */
.departments{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:20px;
}

.dept{
background:#151515;
padding:18px;
border-radius:12px;
border-left:4px solid #25D366;
}

.dept h4{
margin-top:0;
color:#25D366;
}

/* FOOTER */
.footer{
text-align:center;
opacity:0.5;
margin-top:30px;
font-size:13px;
}

</style>
</head>

<body>

<!-- TOP -->
<div class="topbar">
    <h1>⚙ Automotive Professionals Admin</h1>

    <div>
        <a href="/">Home</a>
        <a href="/settings">Settings</a>
        <a href="/logout">Logout</a>
    </div>
</div>

<div class="wrapper">

<!-- STATS -->
<div class="stats">

    <div class="stat-card">
        <h2>{{data|length}}</h2>
        <p>Total Applications</p>
    </div>

    <div class="stat-card">
        <h2>4</h2>
        <p>Departments</p>
    </div>

    <div class="stat-card">
        <h2>2026</h2>
        <p>Current Intake</p>
    </div>

    <div class="stat-card">
        <h2>ACTIVE</h2>
        <p>Institution Status</p>
    </div>

</div>

<!-- SETTINGS -->
<div class="box">

    <h3>🌍 Institution Settings</h3>

    <form method="POST">

        <label>Hero Text</label>
        <input name="hero" value="{{s.hero}}">

        <label>WhatsApp Number</label>
        <input name="whatsapp" value="{{s.whatsapp}}">

        <label>Courses</label>
        <textarea name="courses" rows="5">{{s.courses}}</textarea>

        <button type="submit">Save Live Changes</button>

    </form>

</div>

<!-- LOGO -->
<div class="box">

    <h3>🖼 Upload Institution Logo</h3>

    <form method="POST" action="/upload_logo" enctype="multipart/form-data">

        <input type="file" name="logo">

        <button type="submit">Upload Logo</button>

    </form>

</div>

<!-- DEPARTMENTS -->
<div class="box">

<h3>🏭 Departments</h3>

<div class="departments">

<div class="dept">
<h4>Heavy Plant Mechanics</h4>
<p>18 Month Full Professional Course</p>
</div>

<div class="dept">
<h4>Light Motor Mechanics</h4>
<p>Engine Systems • Suspension • Diagnostics</p>
</div>

<div class="dept">
<h4>Welding Department</h4>
<p>6 Month Practical Industrial Training</p>
</div>

<div class="dept">
<h4>Diagnostics & Maintenance</h4>
<p>Short Skills Courses & Engine Management</p>
</div>

</div>

</div>

<!-- STUDENTS -->
<div class="box">

<h3>🧑‍🎓 Registered Students</h3>

<div class="table-wrap">

<table>

<tr>
<th>ID</th>
<th>Student</th>
<th>Phone</th>
<th>Course</th>
<th>Status</th>
<th>Documents</th>
<th>Date</th>
</tr>

{% for r in data %}

<tr>

<td>#{{r.id}}</td>

<td>
<b>{{r.name}}</b><br>
<small>{{r.email}}</small>
</td>

<td>{{r.phone}}</td>

<td>{{r.course}}</td>

<td>
<span class="badge active">
Registered
</span>
</td>

<td>
{% if r.file %}
<a class="file-btn" href="/uploads/{{r.file}}" target="_blank">
View File
</a>
{% else %}
No File
{% endif %}
</td>

<td>{{r.date}}</td>

</tr>

{% endfor %}

</table>

</div>

</div>

<div class="footer">
© 2026 Automotive Professionals (Pty) Ltd — Institution Management System
</div>

</div>

</body>
</html>

""", s=s, data=data)

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
