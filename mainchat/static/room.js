console.log('room works')

const roomName = JSON.parse(document.getElementById('roomName').textContent);

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

function onlineUsersSelectorAdd(value) {
    if (document.querySelector("option[value='" + value + "']")) return;
    let newOption = document.createElement("option");
    newOption.value = value;
    newOption.innerHTML = value;
    onlineUsersSelector.appendChild(newOption);
}

function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

chatMessageInput.focus();

chatMessageInput.onkeyup = function (e) {
    if (e.keyCode === 13) {
        chatMessageSend.click();
    }
}

chatMessageSend.onclick = function () {
    if (chatMessageInput.value.length === 0) return;
    chatSocket.send(JSON.stringify({
        "message": chatMessageInput.value,
    }));
    chatMessageInput.value = "";
}


chatLog.onclick = function () {
    let userChoice = prompt("Choose a number: 1 - Edit Message, 2 - Delete Message");
    switch (userChoice) {
        case '1':
            let edited_msg = prompt("Enter edited message:");
            break;
        case '2':
            chatSocket.send(JSON.stringify({
                "message": "/deleting",
            }));
            break;
    }
}


let chatSocket = null;

function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

    chatSocket.onopen = function (e) {
        console.log("Connected to the WebSocket: " + String(chatSocket.url));
    }

    chatSocket.onclose = function (e) {
        console.log("WebSocket connection closed. Trying to reconnect in 2s...");
        setTimeout(function () {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data);

        /*
        $('#chatMessageInput').one('input', function () {
            if (data.user) {
                chatLog.value += `${data.user} is typing....` + "\n";
            }
        })
        */

        switch (data.type) {
            case "chat_message":
                chatLog.value += data.user + ": " + data.message + "\n";
                break;
            case "user_list":
                for (let i = 0; i < data.users.length; i++) {
                    onlineUsersSelectorAdd(data.users[i]);
                }
                break;
            case "user_join":
                chatLog.value += data.user + " joined the room.\n";
                onlineUsersSelectorAdd(data.user);
                break;
            case "user_leave":
                chatLog.value += data.user + " left the room.\n";
                onlineUsersSelectorRemove(data.user);
                break;
            case "private_message":
                chatLog.value += "PM from " + data.user + ": " + data.message + "\n";
                break;
            case "pm_delivered":
                chatLog.value += "PM to " + data.target + ": " + data.message + "\n";
                break;
            case "leave_room":
                chatMessageInput.value += data.user + ", " + data.message + "\n";
                break;
            case "command_list":
                chatLog.value += data.message + "\n" + "\n";
                break;
            case "admin_list":
                if (data.users.length > 0) {
                    chatLog.value += data.message
                    for (let i = 0; i < data.users.length; i++) {
                        onlineUsersSelectorAdd(data.users[i]);
                    }
                    break;
                } else {
                    chatLog.value += "This is an admins only room." + "\n";
                    break;
                }
            case "message_list":
                for (let m = data.messages.length; m > 0; m--) {
                    chatLog.value += String(data.users[m]) + ": " + String(data.messages[m]) + "\n";
                }
                chatLog.value += "\n";
                break;
            case "list_msg":
                chatMessageInput.value += "Which message do you want to delete?"
                for (let p = 0; p < data.message_lists; ++p) {
                    chatMessageInput.value += " - " + "\n" +
                        String(data.message_lists_id[p]) + ": " + String(data.message_lists_content[p]);
                }
                break;
            default:
                console.error("Unknown message type!");
                break;
        }

        $('#chatMessageInput').one('input', function () {
            if (data.user) {
                chatLog.value += `${data.user} is typing....` + "\n";
            }
        })
        // scroll 'chatLog' to the bottom
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    chatSocket.onerror = function (err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}

connect();

onlineUsersSelector.onchange = function () {
    chatMessageInput.value = "/pm " + onlineUsersSelector.value + " ";
    onlineUsersSelector.value = null;
    chatMessageInput.focus();
}