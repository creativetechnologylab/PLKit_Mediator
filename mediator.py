from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from connection import Connection
import json

class Mediator(WebSocketApplication):
    def on_open(self):
        print("Connection opened", self.ws.environ)
        self.conn = Connection.auto()

    def on_message(self, message):
        if not self.ws.closed:
            o = json.loads(message)
            print(o)
           

    def on_close(self, reason):
        print("reason is", reason)

if __name__ == "__main__":
    wss = WebSocketServer(('', 5000),
        Resource(OrderedDict([('/', Mediator)])))

    if not Connection.auto():
        print('error no serial port found')

    try:
        wss.serve_forever()
    except KeyboardInterrupt:
        print('bye')
