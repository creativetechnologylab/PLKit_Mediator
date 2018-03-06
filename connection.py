from serial import Serial
from serial.tools import list_ports
import struct

class Connection:
    _serial = None
    STX = b'\x02'
    ETX = b'\x03'
    FLOAT = b'\xf0'
    INT = b'\xf1'
    BANG = b'\xf2'
    STRING = b'\xf3'

    def __init__(self, serial):
        self.serial = serial

    @staticmethod
    def auto(baud=115200):
        serial = Connection._serial
        print('serial is', serial)
        if not serial:
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
            return Connection(serial)

    @staticmethod
    def close():
        if Connection._serial:
            Connection._serial.close()

    def _construct_packet(self, key, data):
        o = Connection.STX
        o += bytes([len(key)])
        o += key.encode('utf8')

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
