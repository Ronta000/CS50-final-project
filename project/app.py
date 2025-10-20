from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, jsonify
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
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    start_time TEXT,
    end_time TEXT,
    duration INTEGER,
    date TEXT
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS customizedsessiondb (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    start_time TEXT,
    end_time TEXT,
    duration INTEGER,
    date TEXT
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
db.execute("""
CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("register.html")
    
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
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
            user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        except:
            return ("username already exists", 400)

        session["user_id"] = user_id
        return redirect("/dashboard")
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
        return redirect("/dashboard")

    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/register")


@app.route('/sessions', methods=["GET", "POST"])
def sessions():
    return render_template('sessions.html')

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("studybuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    user_id = session.get("user_id")
    
    if not user_id:
        conn.close()
        return redirect("/register")
    
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    cur.execute("DELETE FROM customizedsessiondb WHERE user_id = ? AND date < ?", (user_id, seven_days_ago))
    conn.commit()
    
    cur.execute("SELECT * FROM customizedsessiondb WHERE user_id = ? AND date >= ?", (user_id, seven_days_ago))
    sessions = cur.fetchall()
    
    sessions_count = len(sessions)
    total_minutes = 0
    for s in sessions:
        start_time = datetime.datetime.fromisoformat(s["start_time"].replace("Z", "+00:00"))
        end_time = datetime.datetime.fromisoformat(s["end_time"].replace("Z", "+00:00"))
        duration_minutes = (end_time - start_time).total_seconds() / 60  
        total_minutes += duration_minutes
    
    total_hours = round(total_minutes / 60, 4)  
    
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if sessions:
        first_session_date = datetime.datetime.strptime(sessions[0]["date"], "%Y-%m-%d")
        start_date = first_session_date.strftime("%Y-%m-%d")
        end_date = (first_session_date + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        start_date = "N/A"
        end_date = "N/A"
    
    conn.close()
    
    return render_template(
        "dashboard.html",
        start_date=start_date,
        end_date=end_date,
        sessions_count=sessions_count,
        total_hours=total_hours,
        sessions=sessions
    )


@app.route("/flashcards", methods=["GET", "POST"])
def flashcards():
    user_id = session["user_id"]
    conn = sqlite3.connect("studybuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":
        sessions=sessionsquestion = request.form.get("question")
        answer = request.form.get("answer")

        if question and answer:
            cur.execute(
                "INSERT INTO flashcards (user_id, question, answer) VALUES (?, ?, ?)",
                (user_id, question, answer)
            )
            conn.commit()

    cur.execute("SELECT * FROM flashcards WHERE user_id = ?", (user_id,))
    cards = cur.fetchall()
    conn.close()

    return render_template("flashcards.html", cards=cards)

@app.route("/flashcards_data")
def flashcards_data():
    user_id = session["user_id"]
    conn = sqlite3.connect("studybuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM flashcards WHERE user_id = ?", (user_id,))
    cards = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(cards)

@app.route("/add_flashcard", methods=["POST"])
def add_flashcard():
    user_id = session["user_id"]
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")

    conn = sqlite3.connect("studybuddy.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO flashcards (user_id, question, answer) VALUES (?, ?, ?)",
        (user_id, question, answer)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/delete_flashcard/<int:id>", methods=["DELETE"])
def delete_flashcard(id):
    user_id = session["user_id"]
    conn = sqlite3.connect("studybuddy.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM flashcards WHERE id = ? AND user_id = ?", (id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/get_flashcards")
def get_flashcards():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = session["user_id"]
    flashcards = db.execute("SELECT question, answer FROM flashcards WHERE user_id = ?", user_id,)

    return jsonify(flashcards)

@app.route('/usersession' , methods=["GET" , "POST"])
def usersession():
    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400
        
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        session_type = data.get("session_type")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")
        date = data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d")

        if session_type == "study":
            db.execute(
                "INSERT INTO customizedsessiondb (user_id, start_time, end_time, duration, date) VALUES (?, ?, ?, ?, ?)",
                user_id, start_time, end_time, duration, date
            )
            return jsonify({"message": "Study session saved successfully!"}), 200
        
        return jsonify({"message": "Break session not recorded."}), 200

    return render_template('usersession.html')

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    conn = sqlite3.connect("studybuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    cur.execute("DELETE FROM tasks WHERE user_id = ? AND date(date_created) < ?", (user_id, seven_days_ago))
    conn.commit()

    if request.method == "POST":
        task = request.form.get("tasks")
        if task:
            cur.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, task))
            conn.commit()
        conn.close()
        return redirect("/tasks")

    cur.execute("SELECT id, task, completed FROM tasks WHERE user_id = ? ORDER BY date_created DESC", (user_id,))
    tasks = cur.fetchall()
    conn.close()

    return render_template("tasks.html", tasks=tasks)

@app.route("/update_task/<int:task_id>", methods=["POST"])
def update_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    conn = sqlite3.connect("studybuddy.db")
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed = NOT completed WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
    return redirect("/tasks")


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    conn = sqlite3.connect("studybuddy.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
    return redirect("/tasks")

@app.route('/focusmood', methods=['GET', 'POST'])
def focusmood():
    if request.method == "POST":
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

@app.route('/customizedsession' ,methods=["GET", "POST"] )
def customizedsession():
    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400
        
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        start_time = data.get("start_time")
        end_time = data.get("end_time")
        duration = data.get("duration")
        date = data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d")

        db.execute(
            "INSERT INTO customizedsessiondb (user_id, start_time, end_time, duration, date) VALUES (?, ?, ?, ?, ?)",
            user_id, start_time, end_time, duration, date
        )
        return jsonify({"message": "Session saved successfully!"}), 200
    
    return render_template("customizedsession.html")

@app.route('/customizedsession1' , methods=["GET", "POST"])
def customizedsession1():
        if request.method == "POST":
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data received"}), 400

            user_id = session.get("user_id")

            if not user_id:
                return jsonify({"error": "User not logged in"}), 401

            start_time = data.get("start_time")
            end_time = data.get("end_time")
            duration = data.get("duration")
            date = data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d")

            db.execute(
                "INSERT INTO customizedsessiondb (user_id, start_time, end_time, duration, date) VALUES (?, ?, ?, ?, ?)",
                user_id, start_time, end_time, duration, date
            )

            return jsonify({"message": "Session saved successfully!"}), 200
       
        return render_template("customizedsession1.html")

@app.route('/customizedsession2' ,methods=["GET", "POST"] )
def customizedsession2():
        if request.method == "POST":
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data received"}), 400

            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not logged in"}), 401

            start_time = data.get("start_time")
            end_time = data.get("end_time")
            duration = data.get("duration")
            date = data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d")

            db.execute(
                "INSERT INTO customizedsessiondb (user_id, start_time, end_time, duration, date) VALUES (?, ?, ?, ?, ?)",
                user_id, start_time, end_time, duration, date
            )

            return jsonify({"message": "Session saved successfully!"}), 200
        
        return render_template("customizedsession2.html")

@app.route('/customizedsession3' , methods=["GET", "POST"])
def customizedsession3():
        if request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400

            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "User not logged in"}), 401

            start_time = data.get("start_time")
            end_time = data.get("end_time")
            duration = data.get("duration")
            date = data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d")

            db.execute(
                "INSERT INTO customizedsessiondb (user_id, start_time, end_time, duration, date) VALUES (?, ?, ?, ?, ?)",
                user_id, start_time, end_time, duration, date
            )
            return jsonify({"message": "Session saved successfully!"}), 200
       
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

if __name__ == '__main__':
    app.run(debug=True)