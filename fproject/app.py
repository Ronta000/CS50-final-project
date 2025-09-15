from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import time
import datetime
app = Flask(__name__)

# configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connect to database
db = SQL("sqlite:///studybuddy.db")
@app.route("/")
def index():
    return render_template("register.html")
    return "Welcome to StudyBuddy!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return ("must provide username", 400)
        if not password:
            return ("must provide password", 400)
        if not confirmation:
            return ("must provide confirmation", 400)
        if password != confirmation:
            return ("passwords don't match", 400)

        hash_pw = generate_password_hash(password)

        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hash_pw
            )
        except:
            return ("username already exists", 400)

        session["user_id"] = new_user
        return redirect("/")
    else:
        return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return ("must provide username", 400)
        if not password:
            return ("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return ("invalid username and/or password", 400)

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")  
@app.route('/sessions')
def sessions():
    return render_template('sessions.html')

if __name__ == '__main__':
    app.run(debug=True)
@app.route("/dashboard")
def dashboard():
    return
render_template("dashboard.html")
@app.route("/flashcards" methods=["GET" , "POST"])
def flashcards():
    if request.method=="POST":
        question =request.form["question"]
        answer = request.form["answer"]
    return render_template("flashcards.html")
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")
