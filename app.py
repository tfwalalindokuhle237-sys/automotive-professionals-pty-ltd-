from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import sqlite3
import os
from datetime import datetime
import smtplib

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_SECURE_KEY"

# ---------------- FILE UPLOAD CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            course TEXT,
            id_file TEXT,
            cv_file TEXT,
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
        'youremail@gmail.com',
        'Heavy Plant,Light Motor,Welding')
    """)

    conn.commit()
    conn.close()

init_db()

ADMIN_PASSWORD = "1234"

# ---------------- SETTINGS ----------------
def get_settings():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT hero, whatsapp, email, courses FROM settings WHERE id=1")
    data = c.fetchone()
    conn.close()
    return data

def update_settings(hero, whatsapp, email, courses):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET hero=?, whatsapp=?, email=?, courses=? WHERE id=1",
              (hero, whatsapp, email, courses))
    conn.commit()
    conn.close()

# ---------------- EMAIL ----------------
def send_email(name, phone, course):
    try:
        sender = "yourgmail@gmail.com"
        password = "your_app_password"
        receiver = "yourgmail@gmail.com"

        msg = f"Subject: New Application\n\n{name} applied for {course}\nPhone: {phone}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
        server.quit()
    except:
        print("Email failed")

# ---------------- WHATSAPP (META API READY) ----------------
def send_whatsapp_api(phone, name, course):
    """
    REAL WhatsApp Cloud API READY STRUCTURE
    You must add:
    - TOKEN
    - PHONE_ID
    """
    print(f"[WHATSAPP] Would send: {name} - {course}")
    # Replace with real Meta API later

# ---------------- SAVE FILE ----------------
def save_file(file):
    if file:
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)
        return file.filename
    return ""

# ---------------- FRONTEND (WORKSHOP STYLE UI) ----------------
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
    background:url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1500&q=80');
    background-size:cover;
    background-attachment:fixed;
}

.overlay{background:rgba(0,0,0,0.8);min-height:100vh;}

.nav{
    display:flex;
    justify-content:space-between;
    padding:15px;
    background:rgba(0,0,0,0.7);
}

.nav a{color:white;margin:0 10px;text-decoration:none;}

.logo{color:#25D366;font-weight:bold;}

.hero{text-align:center;padding:70px;}
.hero h1{color:#25D366;font-size:45px;}

.container{display:flex;justify-content:center;flex-wrap:wrap;gap:20px;padding:20px;}

.card{
    background:rgba(20,20,20,0.9);
    padding:20px;
    width:300px;
    border-radius:12px;
}

input,select,textarea{
    width:90%;
    padding:10px;
    margin:5px;
}

.btn{
    background:#25D366;
    color:black;
    padding:10px;
    border:none;
    border-radius:6px;
    cursor:pointer;
    text-decoration:none;
    display:inline-block;
}
</style>
</head>

<body>
<div class="overlay">

<div class="nav">
<div class="logo">🚗 Automotive Professionals</div>
<div>
<a href="/">Home</a>
<a href="/login">Admin</a>
</div>
</div>

<div class="hero">
<h1>Excellence Through Practical Training</h1>
</div>

<div class="container">

<!-- APPLY -->
<div class="card">
<h2>Apply</h2>

<form method="POST" action="/apply" enctype="multipart/form-data">

<input name="name" placeholder="Full Name" required>
<input name="phone" placeholder="Phone" required>
<input name="email" placeholder="Email">

<select name="course">
<option>Heavy Plant Mechanics</option>
<option>Light Motor Mechanics</option>
<option>Welding</option>
</select>

<textarea name="message" placeholder="Message"></textarea>

<p>ID Upload</p>
<input type="file" name="id_file">

<p>CV Upload</p>
<input type="file" name="cv_file">

<p>Certificate Upload</p>
<input type="file" name="cert_file">

<br><br>
<button class="btn">Submit</button>
</form>

</div>

</div>

</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory("uploads", filename)

# ---------------- APPLY ----------------
@app.route("/apply", methods=["POST"])
def apply():
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    course = request.form["course"]
    message = request.form.get("message", "")
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    id_file = save_file(request.files.get("id_file"))
    cv_file = save_file(request.files.get("cv_file"))
    cert_file = save_file(request.files.get("cert_file"))

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO applications
        (name, phone, email, course, id_file, cv_file, cert_file, message, date)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (name, phone, email, course, id_file, cv_file, cert_file, message, date))
    conn.commit()
    conn.close()

    send_email(name, phone, course)
    send_whatsapp_api(phone, name, course)

    return "<h2>Application Submitted Successfully ✅</h2><a href='/'>Back</a>"

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong password"

    return """
    <form method='POST'>
        <input name='password' placeholder='Admin Password'>
        <button>Login</button>
    </form>
    """

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    table = "<h1>Admin Dashboard</h1><table border='1' style='width:100%'>"
    table += "<tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Course</th><th>Date</th></tr>"

    for row in data:
        table += "<tr>" + "".join([f"<td>{i}</td>" for i in row[:6]]) + "</tr>"

    table += "</table>"
    return table

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
