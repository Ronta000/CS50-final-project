from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import time
import datetime
import sqlite3
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
        return redirect("/dashboard")
    else:
        return render_template("register.html")
      
    return redirect('/dashboard')

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
    return render_template("dashboard.html")
@app.route("/flashcards", methods=["GET" , "POST"])
def flashcards():
    if request.method=="POST":
        question =request.form["question"]
        answer = request.form["answer"]
    return render_template("flashcards.html")
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route('/usersession')
def usersession():
    return render_template('usersession.html')

@app.route('/customizedsession')
def customizedsessiom():
    return render_template('customizedsession.html')

@app.route('/tasks')
def tasks():
     return render_template('tasks.html')


@app.route('/focusmood', methods=['GET', 'POST'])
def focusmood():
    if request.method == 'POST':
        try:
            num1 = int(request.form['num1'])
            num2 = int(request.form['num2'])

            if not (1 <= num1 <= 5 and 1 <= num2 <= 5):
                return render_template('focusmood.html', message="Both ratings must be between 1 and 5.")

            total = num1 + num2

            if 2 <= total <= 3:
                return redirect('/customizedsession1')
            elif 4 <= total <= 6:
                return redirect('/customizedsession')
            elif 7 <= total <= 8:
                return redirect('/customizedsession2')
            elif 9 <= total <= 10:
                return redirect('/customizedsession3')

        except ValueError:
            return render_template('focusmood.html', message="Please enter valid numbers.")

    return render_template('focusmood.html')


if __name__ == '__main__':
    app.run(debug=True)

        
@app.route('/customizedsession')
def customizedsession():
       if request.method == "POST":
        data = request.get_json()
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")

        user_id = session.get("user_id")

        conn = sqlite3.connect("focushive.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            INSERT INTO customized_sessions (user_id, start_time, end_time, duration_minutes, session_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, start_time, end_time, duration, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()

        return jsonify({"message": "Customized session recorded successfully!"})
    else:
        return render_template("customizedsession.html")

@app.route('/customizedsession1')
def customizedsession1():
     if request.method == "POST":
        data = request.get_json()
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")

        user_id = session.get("user_id")

        conn = sqlite3.connect("focushive.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            INSERT INTO customized_sessions (user_id, start_time, end_time, duration_minutes, session_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, start_time, end_time, duration, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()

        return jsonify({"message": "Customized session recorded successfully!"})
    else:
        return render_template("customizedsession1.html")

@app.route('/customizedsession2')
def customizedsession2():
     if request.method == "POST":
        data = request.get_json()
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")

        user_id = session.get("user_id")

        conn = sqlite3.connect("focushive.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            INSERT INTO customized_sessions (user_id, start_time, end_time, duration_minutes, session_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, start_time, end_time, duration, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()

        return jsonify({"message": "Customized session recorded successfully!"})
    else:
        return render_template("customizedsession2.html")

@app.route('/customizedsession3')
def customizedsession3():
     if request.method == "POST":
        data = request.get_json()
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")

        user_id = session.get("user_id")

        conn = sqlite3.connect("focushive.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            INSERT INTO customized_sessions (user_id, start_time, end_time, duration_minutes, session_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, start_time, end_time, duration, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()

        return jsonify({"message": "Customized session recorded successfully!"})
    else:
        return render_template("customizedsession3.html")

@app.route('/breaks')
def breaks():
    return render_template('breaks.html')
@app.route('/breaks1')
def breaks1():
    return render_template('breaks1.html')
@app.route('/breaks2')
def breaks2():
    return render_template('breaks2.html')
@app.route('/breaks3')
def breaks3():
    return render_template('breaks3.html')

conn = sqlite3.connect("studybuddy.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT,
    start_time TEXT,
    end_time TEXT,
    date TEXT,
    duration INTEGER
)
""")
conn.commit()
