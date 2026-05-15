from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change_this_key"

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
WHATSAPP_NUMBER = "26800000000"

# ---------------- WHATSAPP ----------------
def whatsapp_link(name, phone, course):
    msg = f"New Application:%0AName: {name}%0APhone: {phone}%0ACourse: {course}"
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={msg}"

# ---------------- FRONTEND ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Automotive Professionals</title>

<style>
body{margin:0;font-family:Arial;background:#0b0b0b;color:white;}

.nav{
    display:flex;justify-content:space-between;
    padding:15px;background:#111;
}
.nav a{color:white;margin:0 10px;text-decoration:none;}
.logo{color:#25D366;font-weight:bold;}

.hero{
    text-align:center;
    padding:70px;
    background:linear-gradient(135deg,#111,#2a0000);
}

.hero h1{color:#25D366;font-size:45px;}

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
    width:260px;
    border-radius:10px;
}

input,select{
    padding:10px;
    width:240px;
    margin:5px;
}

button{
    padding:10px 15px;
    background:#25D366;
    border:none;
    color:black;
    cursor:pointer;
}

a.btn{
    background:#25D366;
    padding:10px;
    display:inline-block;
    margin-top:10px;
    color:black;
    text-decoration:none;
}
</style>
</head>

<body>

<div class="nav">
    <div class="logo">🚗 Automotive Professionals</div>
    <div>
        <a href="/">Home</a>
        <a href="/login">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>Excellence Through Practical Training</h1>
    <p>Apply below to join our institution</p>
</div>

<div class="container">

    <!-- STUDENT APPLICATION (B SYSTEM) -->
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

            <button type="submit">Submit</button>
        </form>
    </div>

    <!-- COURSES -->
    <div class="card">
        <h2>Courses</h2>
        <p>✔ Heavy Plant Mechanics</p>
        <p>✔ Light Motor Mechanics</p>
        <p>✔ Welding Training</p>
    </div>

    <!-- CONTACT + WHATSAPP (C SYSTEM) -->
    <div class="card">
        <h2>Contact</h2>
        <p>📞 +268 76783891</p>
        <p>📧 takernkambule@gmail.com</p>
        <a class="btn" href="https://wa.me/26800000000">WhatsApp</a>
    </div>

</div>

</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(HTML)

# ---------------- APPLY (STUDENT SYSTEM B) ----------------
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

    # WhatsApp automation (C SYSTEM)
    link = whatsapp_link(name, phone, course)

    return f"""
    <h2>Application Submitted ✅</h2>
    <a href="{link}" target="_blank">Send WhatsApp Notification</a><br><br>
    <a href="/">Go Back</a>
    """

# ---------------- LOGIN (ADMIN SYSTEM D) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong Password"

    return """
    <form method='POST'>
        <h2>Admin Login</h2>
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
