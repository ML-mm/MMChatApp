console.log('home works')

document.querySelector("#roomInput").focus();

document.querySelector("#roomInput").onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter key
        document.querySelector("#roomConnect").click();
    }
};

document.querySelector("#roomConnect").onclick = function () {
    let roomName = document.querySelector("#roomInput").value;
    window.location.pathname = "chat/rooms/" + roomName + "/";
}

/*document.querySelector("#roomSelect").onchange = function () {
    let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
    window.location.pathname = "chat/" + roomName + "/";
}*/

document.querySelector("#roomSelect").ondblclick = function () {
    let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
    window.location.pathname = "chat/rooms/" + roomName + "/";
}