from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime
import smtplib

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

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            hero TEXT,
            whatsapp TEXT
        )
    """)

    c.execute("INSERT OR IGNORE INTO settings VALUES (1,'Excellence Through Practical Teaching','26876783891')")

    conn.commit()
    conn.close()

init_db()

# ---------------- SETTINGS ----------------
ADMIN_PASSWORD = "1234"

# ---------------- GET SETTINGS ----------------
def get_settings():
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("SELECT hero, whatsapp FROM settings WHERE id=1")
    data = c.fetchone()
    conn.close()
    return data

def update_settings(hero, whatsapp):
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET hero=?, whatsapp=? WHERE id=1", (hero, whatsapp))
    conn.commit()
    conn.close()

# ---------------- WHATSAPP AUTO LINK ----------------
def whatsapp_auto(phone, name, course):
    text = f"New Application:%0AName: {name}%0APhone: {phone}%0ACourse: {course}"
    return f"https://wa.me/{phone}?text={text}"

# ---------------- EMAIL NOTIFICATION ----------------
def send_email(name, phone, course):
    try:
        sender = "yourgmail@gmail.com"
        password = "your_app_password"
        receiver = "yourgmail@gmail.com"

        msg = f"Subject: New Student Application\n\n{name} applied for {course}\nPhone: {phone}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
        server.quit()
    except:
        print("Email failed (configure Gmail app password)")

# ---------------- DESIGN ----------------
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
    background:url('https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=1500&q=80');
    background-size:cover;
    background-attachment:fixed;
}

.overlay{
    background:rgba(0,0,0,0.75);
    min-height:100vh;
}

/* NAV */
.nav{
    display:flex;
    justify-content:space-between;
    padding:15px;
    background:rgba(0,0,0,0.7);
    backdrop-filter:blur(10px);
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
    padding:80px 20px;
}

.hero h1{
    font-size:45px;
    color:#25D366;
}

/* CARDS */
.container{
    display:flex;
    justify-content:center;
    gap:20px;
    flex-wrap:wrap;
    padding:30px;
}

.card{
    background:rgba(20,20,20,0.9);
    padding:20px;
    width:280px;
    border-radius:12px;
    backdrop-filter:blur(10px);
}

/* BUTTON */
.btn{
    display:inline-block;
    padding:10px 15px;
    background:#25D366;
    color:black;
    border-radius:6px;
    text-decoration:none;
}

/* INPUT */
input,select{
    padding:10px;
    margin:5px;
    width:240px;
}
</style>
</head>

<body>

<div class="overlay">

<div class="nav">
    <div class="logo"> Automotive Professionals</div>
    <div>
        <a href="/">Home</a>
        <a href="/admin">Admin</a>
        <a href="/login">Login</a>
    </div>
</div>

<div class="hero">
    <h1>Excellence Through Practical Teaching</h1>
</div>

<div class="container">

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
            <button class="btn">Submit</button>
        </form>
    </div>

    <div class="card">
        <h2>Courses</h2>
        <p>Heavy Plant Mechanics</p>
        <p>Light Motor Mechanics</p>
        <p>Welding Training</p>
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

# ---------------- APPLY ----------------
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

    # AUTO WHATSAPP
    link = whatsapp_auto(phone, name, course)

    # EMAIL NOTIFICATION
    send_email(name, phone, course)

    return f"""
    <h2>Application Submitted ✅</h2>
    <a href="{link}" class="btn">Send WhatsApp Auto Message</a><br><br>
    <a href="/">Back</a>
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
    <form method='POST'>
        <input name='password' placeholder='Admin Password'>
        <button>Login</button>
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

    table = "<h1>Admin Dashboard</h1><table border='1' style='width:100%'>"
    table += "<tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Course</th><th>Date</th></tr>"

    for row in data:
        table += "<tr>" + "".join([f"<td>{i}</td>" for i in row]) + "</tr>"

    table += "</table>"
    return table

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
