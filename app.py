from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secure_key_change_me"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            image_file TEXT,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            hero TEXT,
            whatsapp TEXT,
            logo TEXT
        )
    """)

    c.execute("INSERT OR IGNORE INTO settings VALUES (1,'Excellence Through Practical Teaching','26876783891','')")

    conn.commit()
    conn.close()

init_db()

ADMIN_PASSWORD = "1234"

# ---------------- SETTINGS ----------------
def get_settings():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT hero, whatsapp, logo FROM settings WHERE id=1")
    data = c.fetchone()
    conn.close()
    return data

def update_settings(hero, whatsapp, logo):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET hero=?, whatsapp=?, logo=? WHERE id=1",
              (hero, whatsapp, logo))
    conn.commit()
    conn.close()

# ---------------- FILE SAVE ----------------
def save_file(file):
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        return file.filename
    return ""

# ---------------- WHATSAPP (READY FOR API UPGRADE) ----------------
def whatsapp_message(phone, name, course):
    return f"New Application: {name} - {course} - {phone}"

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:#0b0b0b;
    color:white;
}

/* HEADER */
.nav{
    display:flex;
    justify-content:space-between;
    padding:15px;
    background:#111;
}
.nav a{
    color:white;
    margin:0 10px;
    text-decoration:none;
}
.logo{color:#25D366;font-weight:bold;}

/* HERO */
.hero{
    text-align:center;
    padding:60px;
    background:linear-gradient(135deg,#111,#2a0000);
}

/* CARDS */
.container{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:20px;
    padding:20px;
}
.card{
    background:#1a1a1a;
    padding:20px;
    width:300px;
    border-radius:10px;
}

/* INPUT */
input,select{
    padding:10px;
    margin:5px;
    width:250px;
}

/* BUTTON */
.btn{
    background:#25D366;
    color:black;
    padding:10px;
    display:inline-block;
    text-decoration:none;
    border-radius:5px;
}
</style>
</head>

<body>

<div class="nav">
    <div class="logo">🚗 Automotive Professionals</div>
    <div>
        <a href="/">Home</a>
        <a href="/admin">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>Excellence Through Practical Teaching</h1>
</div>

<div class="container">

<!-- STUDENT FORM -->
<div class="card">
<h2>Apply Now</h2>

<form method="POST" action="/apply" enctype="multipart/form-data">

<input name="name" placeholder="Full Name" required><br>
<input name="phone" placeholder="Phone" required><br>
<input name="email" placeholder="Email" required><br>

<select name="course">
<option>Heavy Plant Mechanics</option>
<option>Light Motor Mechanics</option>
<option>Welding</option>
</select><br>

<p>ID Upload</p>
<input type="file" name="id_file"><br>

<p>CV Upload</p>
<input type="file" name="cv_file"><br>

<p>Profile Image</p>
<input type="file" name="image_file"><br>

<button class="btn">Submit Application</button>

</form>
</div>

<!-- COURSES -->
<div class="card">
<h2>Courses</h2>
<p>Heavy Plant Mechanics</p>
<p>Light Motor Mechanics</p>
<p>Welding</p>
</div>

</div>

</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML)

# ---------------- APPLY ----------------
@app.route("/apply", methods=["POST"])
def apply():
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    course = request.form["course"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    id_file = save_file(request.files.get("id_file"))
    cv_file = save_file(request.files.get("cv_file"))
    image_file = save_file(request.files.get("image_file"))

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO applications 
        VALUES (NULL,?,?,?,?,?,?,?,?)
    """, (name, phone, email, course, id_file, cv_file, image_file, date))

    conn.commit()
    conn.close()

    msg = whatsapp_message(phone, name, course)

    return f"""
    <h2>Application Submitted ✅</h2>
    <p>{msg}</p>
    <a class="btn" href="/">Back</a>
    """

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        if request.method == "POST":
            if request.form["password"] == ADMIN_PASSWORD:
                session["admin"] = True
                return redirect("/admin")
        return """
        <form method='POST'>
            <input name='password' placeholder='Password'>
            <button>Login</button>
        </form>
        """

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    html = "<h1>Admin Dashboard</h1>"

    html += "<table border='1' style='width:100%;color:white;'>"
    html += "<tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Course</th><th>ID</th><th>CV</th><th>Image</th><th>Date</th></tr>"

    for row in data:
        html += "<tr>" + "".join([f"<td>{i}</td>" for i in row]) + "</tr>"

    html += "</table>"

    return html

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
