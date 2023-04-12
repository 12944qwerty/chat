import os
import time
import json
from flask import Flask, request, render_template, redirect, session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import dotenv

DEBUG = True

app = Flask(__name__)
db = SQLAlchemy()
app.config['SECRET_KEY'] = os.environ.get("SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
db.init_app(app)

socket = SocketIO(app, sync_mode=None)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

active = {}

@app.route('/', methods=['GET'])
def chat():
    if not session.get('username'):
        return redirect('/login')
    
    return render_template('chat.html', username=session['username'], sync_mode=socket.async_mode)

@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.execute(db.select(User.password).where(User.username == username)).first()

        if password == user.tuple()[0]:
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Username or password is incorrect")
    
    return render_template('login.html')
    
@app.route('/signup', methods=['GET', 'POST'])
def signUpPage():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        db.session.add(User(username=username, password=password))
        db.session.commit()

        return redirect('/login')
    else:
        return render_template('signup.html')
    
@app.route('/logout', methods=['GET', 'POST'])
def logoutPage():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect('/login')
    else:
        return """<form method="POST"><label>Are you sure you want to logout?</label><input type="submit" value="Logout"></form>"""
    
@app.route('/admin', methods=['GET'])
def adminPage():
    if session.get('username') in ['qwerty']:
        return render_template('admin.html')
    return redirect('/')

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

if __name__ == '__main__':
    socket.run(app, host="0.0.0.0", port=8080, debug=DEBUG)
