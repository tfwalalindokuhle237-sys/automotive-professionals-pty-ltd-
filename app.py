from flask import Flask, render_template_string, request, redirect, session, send_from_directory, url_for
import sqlite3, os
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

    c.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        course TEXT,
        id_file TEXT,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        hero TEXT,
        whatsapp TEXT,
        courses TEXT
    )
    """)

    c.execute("INSERT OR IGNORE INTO settings VALUES (1,'Automotive Training Centre','26876783891','Mechanics,Welding,Diagnostics')")
    conn.commit()
    conn.close()

init()


# ---------------- HELPERS ----------------
def allowed(f):
    return "." in f and f.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


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
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, email, msg)
        server.quit()
    except:
        print("Email failed")


# ---------------- UI ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals Pty Ltd</title>

<style>
body{
margin:0;
font-family:Segoe UI, Arial;
color:white;
background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc') center/cover fixed;
}

/* DARK OVERLAY */
.overlay{
background:rgba(0,0,0,0.78);
min-height:100vh;
}

/* NAV */
.nav{
display:flex;
justify-content:space-between;
align-items:center;
padding:15px 25px;
background:rgba(0,0,0,0.85);
backdrop-filter:blur(10px);
border-bottom:1px solid #222;
}

.logo-area{
display:flex;
align-items:center;
gap:10px;
}

.logo{
width:40px;
height:40px;
border-radius:50%;
background:#222;
object-fit:cover;
border:2px solid #25D366;
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
padding:80px 20px;
}

.hero-box{
display:inline-block;
padding:20px 30px;
border-radius:15px;
background:rgba(0,0,0,0.6);
backdrop-filter:blur(8px);
border:1px solid #333;
}

.hero h1{
margin:0;
color:#25D366;
font-size:42px;
}

.hero p{
opacity:0.8;
margin-top:10px;
}

/* MAIN LAYOUT */
.container{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:20px;
padding:40px;
}

/* GLASS CARD */
.card{
background:rgba(20,20,20,0.85);
backdrop-filter:blur(10px);
padding:22px;
width:300px;
border-radius:15px;
border:1px solid #333;
transition:0.3s;
}

.card:hover{
transform:translateY(-8px);
border-color:#25D366;
}

/* INPUTS */
input,select{
width:100%;
padding:10px;
margin:8px 0;
border-radius:8px;
border:1px solid #333;
background:#111;
color:white;
outline:none;
}

input:focus,select:focus{
border-color:#25D366;
}

/* BUTTON */
.btn{
display:inline-block;
width:100%;
padding:12px;
background:#25D366;
color:black;
border:none;
border-radius:8px;
font-weight:bold;
cursor:pointer;
transition:0.3s;
}

.btn:hover{
background:#1fae55;
transform:scale(1.03);
}

/* PROFILE SLOT */
.profile-upload{
text-align:center;
padding:10px;
border:1px dashed #444;
border-radius:10px;
margin-bottom:15px;
color:#aaa;
}

/* COURSES */
.course-list p{
margin:8px 0;
padding:8px;
background:#111;
border-radius:6px;
border-left:3px solid #25D366;
}

/* FOOTER */
footer{
text-align:center;
padding:20px;
opacity:0.6;
font-size:13px;
}
</style>
</head>

<body>

<div class="overlay">

<!-- NAV -->
<div class="nav">

    <div class="logo-area">
        <div class="logo"></div>
        <div><b>Automotive Professionals</b></div>
    </div>

    <div>
        <a href="/">Home</a>
        <a href="/admin">Admin</a>
        <a href="/login">Login</a>
    </div>

</div>

<!-- HERO -->
<div class="hero">
    <div class="hero-box">
        <h1>{{h}}</h1>
        <p>Excellence Through Practical Automotive Training</p>
    </div>
</div>

<!-- CONTENT -->
<div class="container">

    <!-- APPLY -->
    <div class="card">

        <h3>Student Application</h3>

        <!-- PROFILE SLOT (future admin upload) -->
        <div class="profile-upload">
            Institution Logo Slot (Admin Upload)
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

            <input type="file" name="file" required>

            <button class="btn">Submit Application</button>

        </form>
    </div>

    <!-- COURSES -->
    <div class="card">
        <h3>Available Courses</h3>
        <div class="course-list">
            {% for c in courses %}
            <p>{{c}}</p>
            {% endfor %}
        </div>
    </div>

</div>

<footer>
© 2026 Automotive Professionals (Pty) Ltd | Built for real training systems
</footer>

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
    conn.execute("INSERT INTO applications VALUES(NULL,?,?,?,?,?,?)",
        (request.form["name"], request.form["phone"], request.form["email"],
         request.form["course"], f, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()

    Thread(target=send_email, args=(request.form["name"],request.form["email"],request.form["course"])).start()

    return "<h2>Submitted ✅</h2><a href='/'>Back</a>"


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    data = db().execute("SELECT * FROM applications ORDER BY id DESC").fetchall()

    html = "<h1>ADMIN</h1><table border='1' style='width:100%'>"
    for r in data:
        html += f"<tr><td>{r['name']}</td><td>{r['phone']}</td><td>{r['course']}</td></tr>"
    html += "</table>"
    return html


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
    return "<form method='POST'><input name='password'><button>Login</button></form>"


@app.route("/uploads/<file>")
def files(file):
    return send_from_directory(UPLOAD_FOLDER,file)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
