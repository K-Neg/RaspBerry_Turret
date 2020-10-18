ws = new WebSocket("ws://192.168.1.119:8000/ws");

var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value;

slider.oninput = function () {
    output.innerHTML = this.value;
    ws.send(this.value);
    event.preventDefault
}


