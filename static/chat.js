const chatBox = document.getElementById("chatbox").children[0];
function addMessage(time, user, message) {
    const messageBox = document.createElement("li");
    chatBox.appendChild(messageBox);

    if (user) {
        messageBox.innerHTML = `${user}: ${message}`;
    } else {
        messageBox.innerHTML = message;
    }

}

function userUpdate({ time, username, type }) {
    addMessage(time, "", `${username} ${type} the party!`);
}

function handleMessage({ time, username, message }) {
    addMessage(time, username, message);
}

const login = document.getElementById("login");
const chatform = document.getElementById("chat");
login.addEventListener("submit", (e) => {
    e.preventDefault();

    if (!username) {
        socket = io();
        
        username = document.getElementById("username").value;
        document.getElementById("user").innerText = username;
        login.style.display = 'none';
        chatform.style.display = 'block';

        socket.on("receive message", handleMessage);
        socket.on("update user", userUpdate);

        socket.emit("handle user", {
            username,
            type: "joined",
            time: Date.now(),
        });
    } else {
        socket.emit("handle user", {
            username,
            time: Date.now(),
        });
        
        if (socket) {
            socket.off();
        }
        socket = null;
        login.style.display = 'block';
        chatform.style.display = 'none';
    }
});

chatform.addEventListener("submit", (e) => {
    e.preventDefault();

    if (username) {
        const message = document.getElementById("prompt");

        if (message) {
            socket.emit("send message", {
                username,
                message: message.value,
                time: Date.now()
            });
            message.value = "";
        }
    }
});
