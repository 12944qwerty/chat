import os
import time
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET")
socket = SocketIO(app, sync_mode=None)


@app.route('/', methods=['GET'])
def chat():
    return render_template('chat.html', sync_mode=socket.async_mode)

users = {}

@socket.on("disconnect")
def disconnect():
    socket.emit("update user", {
        "username": users[request.sid],
        "type": "left",
        "time": int(time.time() * 1000)
    })
    del users[request.sid]

@socket.on("handle user")
def new_user(payload):
    users[request.sid] = payload["username"]
    socket.emit("update user", payload)

@socket.on("send message")
def new_message(payload):
    socket.emit("receive message", payload)

if __name__ == '__main__':
    socket.run(app, host="0.0.0.0", port=8080, debug=False)
