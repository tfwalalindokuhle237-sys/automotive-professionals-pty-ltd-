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
<title>Automotive Professionals</title>

<style>
body{
margin:0;
font-family:Arial;
color:white;
background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc') center/cover fixed;
}

.overlay{background:rgba(0,0,0,0.75);min-height:100vh;}

.nav{display:flex;justify-content:space-between;padding:15px;background:#111;}
.nav a{color:white;margin:0 10px;text-decoration:none}

.hero{text-align:center;padding:60px}
.hero h1{color:#25D366;font-size:40px}

.card{
background:#1c1c1c;
padding:20px;
margin:10px;
border-radius:10px;
}

.container{display:flex;justify-content:center;flex-wrap:wrap}

.btn{
background:#25D366;
padding:10px;
color:black;
text-decoration:none;
border-radius:6px;
}
</style>
</head>

<body>
<div class="overlay">

<div class="nav">
<div>🚗 Automotive</div>
<div>
<a href="/">Home</a>
<a href="/admin">Admin</a>
</div>
</div>

<div class="hero">
<h1>{{h}}</h1>
</div>

<div class="container">

<div class="card">
<h3>Apply</h3>
<form method="POST" action="/apply" enctype="multipart/form-data">
<input name="name" placeholder="Name"><br><br>
<input name="phone" placeholder="Phone"><br><br>
<input name="email" placeholder="Email"><br><br>

<select name="course">
{% for c in courses %}
<option>{{c}}</option>
{% endfor %}
</select><br><br>

<input type="file" name="file"><br><br>

<button class="btn">Submit</button>
</form>
</div>

<div class="card">
<h3>Courses</h3>
{% for c in courses %}
<p>{{c}}</p>
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
