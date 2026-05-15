
from flask import Flask, render_template_string, request, redirect, session, send_from_directory, url_for
import sqlite3
import os
from datetime import datetime
import smtplib
from threading import Thread
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "AUTO_CODE_IQ_SECURE_KEY_2026"

# ---------------- UPLOAD CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ADMIN_PASSWORD = "1234"

MAIL_SENDER = "yourgmail@gmail.com"
MAIL_PASSWORD = "your_app_password"


# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            course TEXT,
            id_file TEXT,
            cert_file TEXT,
            message TEXT,
            status TEXT DEFAULT 'NEW',
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            hero TEXT,
            whatsapp TEXT,
            email TEXT,
            courses TEXT
        )
    """)

    c.execute("""
        INSERT OR IGNORE INTO settings
        VALUES (1,
        'Excellence Through Practical Automotive Training',
        '26876783891',
        'info@gmail.com',
        'Heavy Plant Mechanics,Light Motor Mechanics,Welding')
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HELPERS ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        final = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        path = os.path.join(UPLOAD_FOLDER, final)
        file.save(path)
        return final
    return ""


def send_email_async(name, email, course):
    try:
        msg = f"Subject: New Application\n\n{name} applied for {course}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, email, msg)
        server.quit()
    except:
        print("Email failed")


# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Auto Code IQ</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:#0b0b0b;
    color:white;
}

.nav{
    display:flex;
    justify-content:space-between;
    padding:15px;
    background:#111;
}

.nav a{color:white;margin:0 10px;text-decoration:none;}

.hero{
    text-align:center;
    padding:70px;
    background:linear-gradient(135deg,#111,#2a0000);
}

.hero h1{color:#25D366;}

.container{
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:20px;
    padding:20px;
}

.card{
    background:#1a1a1a;
    padding:20px;
    width:300px;
    border-radius:10px;
}

input,select,textarea{
    width:90%;
    padding:10px;
    margin:5px;
}

.btn{
    background:#25D366;
    padding:10px;
    color:black;
    border:none;
    cursor:pointer;
}
</style>
</head>

<body>

<div class="nav">
    <div>🚗 Auto Code IQ</div>
    <div>
        <a href="/">Home</a>
        <a href="/admin">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>Excellence Through Practical Training</h1>
</div>

<div class="container">

<div class="card">
<h2>Apply</h2>

<form method="POST" action="/apply" enctype="multipart/form-data">

<input name="name" placeholder="Name" required>
<input name="phone" placeholder="Phone" required>
<input name="email" placeholder="Email" required>

<select name="course">
<option>Heavy Plant</option>
<option>Light Motor</option>
<option>Welding</option>
</select>

<textarea name="message" placeholder="Message"></textarea>

<p>ID Upload</p>
<input type="file" name="id_file">

<p>Certificate Upload</p>
<input type="file" name="cert_file">

<button class="btn">Submit</button>
</form>

</div>

</div>

</body>
</html>
"""


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/apply", methods=["POST"])
def apply():
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    course = request.form["course"]

    id_file = save_file(request.files.get("id_file"))
    cert_file = save_file(request.files.get("cert_file"))

    conn = get_db()
    conn.execute("""
        INSERT INTO applications
        (name, phone, email, course, id_file, cert_file, message, date)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        name, phone, email, course,
        id_file, cert_file,
        request.form.get("message", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

    Thread(target=send_email_async, args=(name, email, course)).start()

    return "<h2>Application Submitted ✅</h2><a href='/'>Back</a>"


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    apps = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    conn.close()

    table = "<h1>Admin Dashboard</h1><table border='1' style='width:100%;color:white;'>"
    table += "<tr><th>Name</th><th>Phone</th><th>Email</th><th>Course</th><th>Status</th></tr>"

    for a in apps:
        table += f"<tr><td>{a['name']}</td><td>{a['phone']}</td><td>{a['email']}</td><td>{a['course']}</td><td>{a['status']}</td></tr>"

    table += "</table>"
    return table


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong Password"

    return """
    <form method='POST'>
        <input name='password' placeholder='Admin Password'>
        <button>Login</button>
    </form>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
