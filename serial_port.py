# Before use, include the user into the correct group to avoid permission errors
# Ubuntu
# sudo usermod -a -G dialout 'user'
# Arch
# sudo usermod -a -G uucp 'user'

import serial
from serial.tools import list_ports


def com_ports():
    return list_ports.comports()


class SerialPort:
    def __init__(self, rate: int = 115200):
        self.ser = serial.Serial(timeout=0)

    def write_byte(self, data: str) -> None:
        self.ser.write(data.encode(encoding='ascii'))

    def send_ready(self) -> None:
        self.write_byte('1')

    def read_byte(self) -> str:
        if not self.ser.is_open:
            self.ser.open()
        inp = self.ser.read()
        return inp.decode(encoding='ascii')

    def set_baudrate(self, rate: int):
        if self.ser.port is not None:
            self.ser.baudrate = rate

    def get_baudrate(self):
        return self.ser.baudrate

    def set_serial_name(self, name: str):
        self.ser.port = name

    def get_serial_name(self):
        return self.ser.port

    def in_waiting(self):
        return self.ser.in_waiting

    def flush(self):
        self.ser.flush()

    def close(self):
        self.ser.close()


if __name__ == '__main__':
    ser = SerialPort()
    print(ser)
    # read_thread = threading.Thread(name="read", target=read_byte, args=[ser])
    # read_thread.start()
    for i in range(10):
        ser.send_ready()
        print(ser.read_byte())
