import speech_recognition as sr
import pyttsx3
from threading import Thread

class VocalCommandModule:

    vocal_command_module = None

    def __init__(self):
        self.v_rec = None
        self.v_synt = None

    @staticmethod
    def get_instance():
        if VocalCommandModule.vocal_command_module is None:
            VocalCommandModule.vocal_command_module = VocalCommandModule()
        return VocalCommandModule.vocal_command_module

    def init(self):
        self.v_rec = sr.Recognizer()
        self.v_synt = pyttsx3.init()

    def recognize_command(self):

        # get audio from microphone
        with sr.Microphone() as source:
            print("Parla ora...")
            self.v_rec.adjust_for_ambient_noise(source)
            audio = self.v_rec.listen(source, timeout=5)

        # Recognize audio by using Google
        text = None
        try:
            text = self.v_rec.recognize_google(audio, language='it-IT')
        except sr.UnknownValueError:
            print("I have no understood, try again")
            return None
        except sr.RequestError as e:
            print(f"Vocal Command Recognized doesn't work {e}")
            return None
        print(text)
        return text

    def say(self, text):
        t = Thread(target=self.synthesize_text, args=(text,), daemon=True)
        t.start()

    def synthesize_text(self, text):
        self.v_synt.say(text)
        try:
            self.v_synt.runAndWait()
        except Exception:
            pass



if __name__ == '__main__':

    VocalCommandModule.get_instance().init()
    while True:
        command = VocalCommandModule.get_instance().recognize_command()
        print(command)
        VocalCommandModule.get_instance().synthesize_text(command)
