from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "internalign_secret"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db()
        conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                     (name, email, password, role))
        conn.commit()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (email, password)).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "admin":
                return redirect("/admin_dashboard")
            else:
                return redirect("/user_dashboard")

    return render_template("login.html")

@app.route("/user_dashboard")
def user_dashboard():
    if session.get("role") != "user":
        return redirect("/login")
    return render_template("user_dashboard.html", name=session.get("name"))

@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")
    return render_template("admin_dashboard.html", name=session.get("name"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)