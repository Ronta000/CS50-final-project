from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
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
        subject_names = request.form.getlist("subjects")  
        subject_names = [name.strip() for name in subject_names if name.strip()]
        if len(subject_names) == 0:
            return ("must provide at least one subject", 400)
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

        conn = sqlite3.connect('studybuddy.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,name TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id))''')
        for name in subject_names:
            c.execute("INSERT INTO subjects (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        conn.close()
       
    
        session["user_id"] = new_user
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
        return redirect("/")

    else:
        return render_template("login.html")  

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

@app.route('/sessions')
def sessions():
    return render_template('sessions.html')

if __name__ == '__main__':
    app.run(debug=True)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/flashcards" , methods=["GET" , "POST"])
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
    subjects = get_user_subjects()
    if request.method == 'POST':
        selected_subject = request.form['subject']
        start_custom_pomodoro(selected_subject)
        return redirect(url_for('session_page', subject=selected_subject))
    return render_template('customizedsession.html' , subjects = subjects)

    

@app.route('/tasks')
def tasks():
     return render_template('tasks.html')
    
@app.route('/finish_session', methods=['POST'])
def finish_session():
    focus = int(request.form['focus'])
    mood = int(request.form['mood'])
    total_score = focus + mood

    if total_score <= 3:
        study_time = 25
        break_time = 5
    elif total_score <= 5:
        study_time = 30
        break_time = 5
    elif total_score <= 7:
        study_time = 40
        break_time = 5
    else:
        study_time = 50
        break_time = 10

    save_session(focus, mood, study_time, break_time)
    return render_template('next_session.html', study_time=study_time, break_time=break_time)



