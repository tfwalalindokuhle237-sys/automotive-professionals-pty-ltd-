from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automotive Professionals</title>

        <style>
            body{
                background:#111;
                color:white;
                font-family:Arial;
                text-align:center;
                padding:50px;
            }

            h1{
                color:#25D366;
                font-size:50px;
            }

            .card{
                background:#1e1e1e;
                padding:20px;
                margin:20px auto;
                width:300px;
                border-radius:10px;
            }

            a{
                color:#25D366;
                text-decoration:none;
            }
        </style>
    </head>

    <body>

        <h1>🚗 Automotive Professionals</h1>

        <p>Excellence Through Practical Teaching</p>

        <div class="card">
            <h2>Our Courses</h2>

            <p>✔ Heavy Plant Mechanics</p>
            <p>✔ Light Motor Mechanics</p>
            <p>✔ Welding Training</p>
        </div>

        <div class="card">
            <h2>Contact</h2>

            <p>📞 +268 000 0000</p>

            <a href="https://wa.me/26800000000">
                Chat on WhatsApp
            </a>
        </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
