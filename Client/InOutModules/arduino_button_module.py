import serial


class ArduinoButton:

    arduino_button = None

    def __init__(self):
        self.serial = None

    @staticmethod
    def get_instance():
        if ArduinoButton.arduino_button is None:
            ArduinoButton.arduino_button = ArduinoButton()
        return ArduinoButton.arduino_button

    def init(self, arduino_usb):
        try:
            self.serial = serial.Serial(arduino_usb, 9600)
            self.serial.write(b"OFF")
            self.serial.timeout = 1
            print("Arduino button successfully connected")
        except:
            print("Failed serial connection with Arduino Button")
            self.serial = None

    def isAvailable(self):
        if self.serial is None:
            return False
        else:
            return True

    def ledOn(self):
        if self.serial is not None:
            self.serial.write(b"ON\n")

    def ledOff(self):
        if self.serial is not None:
            self.serial.write(b"OFF\n")

    def check_button_pressed(self):
        if self.serial is None:
            return False
        if self.serial.inWaiting() > 0:
            cmd = self.serial.readline().decode().strip()
            if cmd == "PRESSED":
                return True
        else:
            return False

if __name__ == '__main__':
    usb_port = input('insert usb port:')
    ArduinoButton.get_instance().init(usb_port)
    while True:
        if ArduinoButton.get_instance().check_button_pressed():
            print('PRESSED')
        command = input('insert command (ON/OFF):')
        if command == 'ON':
            ArduinoButton.get_instance().ledOn()
        elif command == 'OFF':
            ArduinoButton.get_instance().ledOff()
