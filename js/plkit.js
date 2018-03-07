function PLKit(host) {
if (host === undefined) {
  host = "localhost";
}
var socket = new WebSocket("ws://" + host + ":7776/");
var callbacks = {};

socket.onopen = (event) => {
  console.log("opened communication channel");
};

this.send = function(key, v) {
  if (socket.readyState !== WebSocket.OPEN) {
    return;
  }

  v = v || true;
  let o = {
    key: key,
    value: v,
  };
  socket.send(JSON.stringify(o));
}

this.sendInt = function(key, v) { this.send(key, parseInt(v)); };
this.sendFloat = function(key, v) { this.send(key, parseFloat(v)); };

this.receive = function(key, func) {
  callbacks[key] = func;
}

socket.onmessage = (event) => {
  let data = JSON.parse(event.data);
  if (callbacks[data.key] !== undefined) {
    callbacks[data.key].call(null, data.value);
  }
};
}
