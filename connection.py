from serial import Serial
from serial.serialutil import SerialException
from serial.tools import list_ports
import struct
import threading
import time
import re

class Connection:
    _serial = None
    STX = b'\x02'
    ETX = b'\x03'
    FLOAT = b'\xf0'
    INT = b'\xf1'
    BANG = b'\xf2'
    STRING = b'\xf3'

    # Singleton pattern
    _instance = None
    def __new__(cls):
        if Connection._instance is None:
            Connection._instance = object.__new__(cls)
        return Connection._instance

    def __init__(self):
        self.wss = {}
        self._connect()

    def _connect(self, baud=115200):
        serial = None
        for port in list_ports.comports():
            if 'Arduino' in port.description:
                serial = Serial(port.device, baud)
                print('found port {} {}'.format(port.device, port.description))
                break

        if not serial:
            print('no serial found')
            pass
        else:
            Connection._serial = serial
            serial.timeout = 0.5
            self.serial = serial

    @staticmethod
    def close():
        if Connection._serial:
            Connection._serial.close()

    def register(self, name, ws):
        self.wss[name] = ws
        print('registered', name, 'to', ws)

    def unregister(self, name):
        del self.wss[name]

    def start_listening(self):
        self.thread = threading.Thread(name='serial-listener',
                                       target=self._listen_thread)
        self.listen = threading.Event()
        self.listen.set()
        self.thread.start()

    def stop_listening(self):
        self.serial.cancel_read()
        self.listen.clear()

    def send_to_arduino(self, o):
        packet = self._construct_packet(o['key'], o['value'])
        try:
            self.serial.write(packet)
        except (OSError, SerialException):
            self._connect()
            time.sleep(1)

    def _listen_thread(self):
        time.sleep(0.2)
        print('starting listening')
        buffer = ''
        while self.listen.is_set():
            try:
                b = self.serial.read()
                buffer += b.decode('utf8')
                buffer = self._process_incoming(buffer)
            except (OSError, SerialException):
                self._connect()
                time.sleep(1)

        print('end listening')

    def _process_incoming(self, data):
        data = re.sub(r'\r|\n', '', data)
        match = re.match(r'\|(\w+),(b|i|f),([\w\.]*)\|', data)
        # print(data)
        if match:
            key, t, d = match.groups()

            if t == 'f':
                d = float(d)
            elif t == 'i':
                d = int(d)

            o = { 'key': key, 'type': t }

            if t != 'b':
                o['value'] = d
            else:
                o['value'] = True

            for _, ws in self.wss.items():
                ws.send(o)
                print('sending:', o['key'], o['value'])

            _, end = match.span()
            return self._process_incoming(data[end:])

        match = re.match(r'{([^{}]+)}', data)
        if match:
            message = match.groups()[0]
            print('message:', message)
            _, end = match.span()
            return self._process_incoming(data[end:])

        return data

    def _construct_packet(self, key, data):
        o = Connection.STX
        o += bytes([len(key)])
        o += key.encode('utf8')

        # try parsing an int and float
        if type(data) == str:
            try:
                data = int(data)
            except ValueError:
                try:
                    data = float(data)
                except ValueError:
                    pass

        if type(data) == int:
            o += Connection.INT
            o += struct.pack('i', data)
        elif type(data) == float:
            o += Connection.FLOAT
            o += struct.pack('f', data)
        elif type(data) == bool:
            o += Connection.BANG
        elif type(data) == str:
            o += Connection.STRING
            o += data.encode()
        else:
            raise "data type not supported"

        o += Connection.ETX

        return o
