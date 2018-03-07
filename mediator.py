from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from connection import Connection
import json

class WebSocketReceiver(WebSocketApplication):
    def on_open(self):
        print("Connection opened")
        self.name = self.ws.environ['REMOTE_PORT']
        self.conn = Connection()
        self.conn.register(self.name, self)
        print('registering')

    def on_message(self, message):
        if not self.ws.closed:
            o = json.loads(message)
            self.conn.send_to_arduino(o)
            print('received {}: {}'.format(o['key'], o['value']))

    def send(self, data):
        self.ws.send(json.dumps(data))

    def on_close(self, reason):
        print("reason is", reason)
        self.conn.unregister(self.name)

if __name__ == "__main__":
    wss = WebSocketServer(('', 7776),
        Resource(OrderedDict([('/', WebSocketReceiver)])))

    conn = Connection()

    if not conn:
        print('error no serial port found')
    else:
        conn.start_listening()

    try:
        wss.serve_forever()
    except KeyboardInterrupt:
        conn.stop_listening()
        print('bye')
