import speech_recognition as sr
import pyttsx3
from threading import Lock
import time


class VocalCommandModule:

    vocal_command_module = None

    def __init__(self):
        self.v_rec = None
        self.v_synt = None
        self.rec_lock = Lock()
        self.synt_lock = Lock()
        self.command = None
        self.msg = None

    @staticmethod
    def get_instance():
        if VocalCommandModule.vocal_command_module is None:
            VocalCommandModule.vocal_command_module = VocalCommandModule()
        return VocalCommandModule.vocal_command_module

    def init(self):
        self.v_rec = sr.Recognizer()
        self.v_synt = pyttsx3.init()

    def recognize_command(self):

        # get audio from michrophone
        with self.v_rec.Microphone() as source:
            print("Parla ora...")
            audio = self.v_rec.listen(source)

        # Recongnize audio by using CMU Sphinx
        text = None
        try:
            text = self.v_rec.recognize_sphinx(audio)
        except sr.UnknownValueError:
            print("I have no understood, try again")
        except sr.RequestError as e:
            print("Vocal Command Recognized doesn't work {0}".format(e))
        return text

    def sysntetize_text(self, text):
        self.v_synt.say(text)
        self.v_synt.runAndWait()

    # public
    def get_command(self):
        with self.rec_lock:
            command = self.command
            self.command = None
            return command

    # public
    def synt_msg(self, msg):
        with self.synt_lock:
            self.msg = msg

    def run_v_rec(self):
        while True:
            command = self.recognize_command()
            print(command)
            with self.rec_lock:
                self.command = command

    def run_v_synt(self):
        while True:
            with self.synt_lock:
                if self.msg is None:
                    continue
                else:
                    msg = self.msg
                    self.msg = None
                    self.sysntetize_text(msg)
            time.sleep(1000)

