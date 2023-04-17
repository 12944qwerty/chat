const chatBox = document.getElementById("chatbox");
function addMessage(time, user, message) {
    const messageBox = document.createElement("div");
    chatBox.appendChild(messageBox);

    if (user) {
        messageBox.innerHTML = `${user}: ${message}`;
    } else {
        messageBox.innerHTML = message;
        messageBox.dataset.info = true;
    }

}

function serverMessage({ time, _, message }) {
    addMessage(time, "", message);
}

function handleMessage({ time, username, message }) {
    addMessage(time, username, message);
}

const chatform = document.getElementById("chat");

socket.on("receive message", handleMessage);
socket.on("server message", serverMessage);

chatform.addEventListener("submit", (e) => {
    if (e.submitter.value === 'logout') {
        fetch("/logout", {
            method: "POST"
        });
        window.location.href = "/login";
    }
    
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
