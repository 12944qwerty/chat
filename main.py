import os
import time
from flask import Flask, request, render_template, redirect, session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
import argon2
import dotenv

DEBUG = True

app = Flask(__name__)
db = SQLAlchemy()
app.config["SECRET_KEY"] = os.environ.get("SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
db.init_app(app)

socket = SocketIO(app, sync_mode=None)

hasher = PasswordHasher()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

active = {}

@app.route("/", methods=["GET"])
def chat():
    if not session.get("username"):
        return redirect("/login")
    
    return render_template("chat.html", username=session["username"], sync_mode=socket.async_mode)

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    if session.get("username"):
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.execute(db.select(User.password).where(User.username == username)).first()

        if user:
            try:
                if hasher.verify(user.tuple()[0], password):
                    session["username"] = username
                    if hasher.check_needs_rehash(user.tuple()[0]):
                        db.session.execute(db.update(User).where(User.username == username).values(password=hasher.hash(password)))
                        db.session.commit()

                    return redirect("/")
            except argon2.exceptions.InvalidHash:
                return render_template("login.html", error="Username or password is incorrect")
        
        return render_template("login.html", error="Username or password is incorrect")
    
    return render_template("login.html")
    
@app.route("/signup", methods=["GET", "POST"])
def signUpPage():
    if session.get("username"):
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        pwdrepeat = request.form.get("pwdrepeat")

        if not username:
            return render_template("signup.html", error="Username is required")
        elif not password:
            return render_template("signup.html", error="Password is required")
        elif not pwdrepeat:
            return render_template("signup.html", error="Repeat password is required")
        elif password != pwdrepeat:
            return render_template("signup.html", error="Passwords do not match")

        try:
            print(password, hasher.hash(password))
            db.session.add(User(username=username, password=hasher.hash(password)))
            db.session.commit()

            return redirect("/login")
        except:
            return render_template("signup.html", error="Username already in use")
    else:
        return render_template("signup.html")
    
@app.route("/logout", methods=["GET", "POST"])
def logoutPage():
    if request.method == "POST":
        session.pop("username", None)
        return redirect("/login")
    else:
        return """<form method="POST"><label>Are you sure you want to logout?</label><input type="submit" value="Logout"></form>"""

@socket.on("disconnect")
def disconnect():
    socket.emit("update user", {
        "username": active[request.sid],
        "type": "left",
        "time": int(time.time() * 1000)
    })
    del active[request.sid]

@socket.on("handle user")
def new_user(payload):
    active[request.sid] = payload["username"]
    socket.emit("update user", payload)

@socket.on("send message")
def new_message(payload):
    socket.emit("receive message", payload)

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=8080, debug=DEBUG)
