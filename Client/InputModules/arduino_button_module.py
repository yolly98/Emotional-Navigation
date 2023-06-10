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

    def init(self, arduino_com):
        try:
            self.serial = serial.Serial(arduino_com, 9600)
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
            self.serial.write(b"ON")

    def ledOff(self):
        if self.serial is not None:
            self.serial.write(b"OFF")

    def check_button_pressed(self):
        if self.serial is None:
            return False
        if self.serial.inWaiting() > 0:
            cmd = self.serial.readline().decode().strip()
            if cmd == "PENDING":
                return True
        else:
            return False