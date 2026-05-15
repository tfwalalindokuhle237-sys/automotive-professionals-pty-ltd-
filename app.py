from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secure_key_change_me"

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
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- SETTINGS ----------------
ADMIN_PASSWORD = "1234"
WHATSAPP_NUMBER = "26876783891"

# ---------------- WHATSAPP ----------------
def whatsapp_link(name, phone, course):
    msg = f"New Application:%0AName: {name}%0APhone: {phone}%0ACourse: {course}"
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={msg}"

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals (Pty) Ltd</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:#0b0b0b;
    color:white;
}

/* NAV */
.nav{
    display:flex;
    justify-content:space-between;
    padding:15px 25px;
    background:#111;
    position:sticky;
    top:0;
}
.nav a{
    color:white;
    margin:0 10px;
    text-decoration:none;
}
.logo{
    color:#25D366;
    font-weight:bold;
}

/* HERO */
.hero{
    text-align:center;
    padding:70px;
    background:linear-gradient(135deg,#111,#2a0000);
}
.hero h1{
    color:#25D366;
    font-size:45px;
}
.hero p{
    opacity:0.8;
}

/* BUTTON */
.btn{
    display:inline-block;
    padding:10px 15px;
    background:#25D366;
    color:black;
    border-radius:6px;
    text-decoration:none;
    margin-top:10px;
}

/* CARDS */
.container{
    display:flex;
    justify-content:center;
    gap:20px;
    flex-wrap:wrap;
    padding:40px;
}
.card{
    background:#1a1a1a;
    padding:20px;
    width:280px;
    border-radius:10px;
    text-align:center;
}

/* FORM */
input,select{
    padding:10px;
    width:240px;
    margin:6px;
    border:none;
    border-radius:5px;
}

/* FOOTER */
footer{
    text-align:center;
    padding:20px;
    background:#111;
    margin-top:30px;
}
</style>
</head>

<body>

<div class="nav">
    <div class="logo">🚗 Automotive Professionals</div>
    <div>
        <a href="/">Home</a>
        <a href="#courses">Courses</a>
        <a href="/login">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>Excellence Through Practical Teaching</h1>
    <p>Training skilled automotive professionals in Eswatini</p>
    <a class="btn" href="#apply">Apply Now</a>
</div>

<div class="container" id="courses">

    <div class="card">
        <h2>Level 3 (12 Months)</h2>
        <p>Heavy Plant Mechanics</p>
        <p>Light Motor Mechanics</p>
    </div>

    <div class="card">
        <h2>6-Month Course</h2>
        <p>Welding Training</p>
    </div>

    <div class="card">
        <h2>Short Courses</h2>
        <p>Engine Diagnosis</p>
        <p>Vehicle Maintenance</p>
    </div>

</div>

<div class="container" id="apply">

    <!-- APPLY FORM -->
    <div class="card">
        <h2>Apply Now</h2>

        <form method="POST" action="/apply">
            <input name="name" placeholder="Full Name" required><br>
            <input name="phone" placeholder="Phone" required><br>
            <input name="email" placeholder="Email" required><br>

            <select name="course">
                <option>Heavy Plant Mechanics</option>
                <option>Light Motor Mechanics</option>
                <option>Welding Training</option>
            </select><br>

            <button class="btn" type="submit">Submit Application</button>
        </form>
    </div>

    <!-- CONTACT -->
    <div class="card">
        <h2>Contact</h2>
        <p>📞 +268 7678 3891</p>
        <p>📞 +268 7968 3891</p>
        <p>📞 +268 7678 3819</p>
        <p>📧 takernkambule@gmail.com</p>

        <a class="btn" href="https://wa.me/26876783891">WhatsApp Us</a>
    </div>

</div>

<footer>
    © 2026 Automotive Professionals (Pty) Ltd
</footer>

</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(HTML)

# ---------------- APPLY (STUDENT SYSTEM) ----------------
@app.route("/apply", methods=["POST"])
def apply():
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    course = request.form["course"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("INSERT INTO applications VALUES (NULL,?,?,?,?,?)",
              (name, phone, email, course, date))
    conn.commit()
    conn.close()

    link = whatsapp_link(name, phone, course)

    return f"""
    <h2>Application Submitted ✅</h2>
    <a href="{link}" class="btn" target="_blank">Send WhatsApp Message</a><br><br>
    <a href="/">Back Home</a>
    """

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong Password"

    return """
    <h2>Admin Login</h2>
    <form method='POST'>
        <input name='password' placeholder='Password'>
        <button type='submit'>Login</button>
    </form>
    """

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    table = "<h1>Admin Dashboard</h1><table border='1' style='width:100%;color:white;'>"
    table += "<tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Course</th><th>Date</th></tr>"

    for row in data:
        table += "<tr>" + "".join([f"<td>{i}</td>" for i in row]) + "</tr>"

    table += "</table>"
    return table

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
