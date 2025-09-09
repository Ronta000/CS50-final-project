@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if not confirmation:
            return apology("must provide confirmation", 400)
        if password != confirmation:
            return apology("passwords don't match", 400)

        hash_pw = generate_password_hash(password)

        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hash_pw
            )
        except:
            return apology("username already exists", 400)

        session["user_id"] = new_user
        return redirect("/")
    else:
        return render_template("register.html")