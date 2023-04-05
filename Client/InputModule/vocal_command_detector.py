import speech_recognition as sr
import pyttsx3
from Client.state_manager import StateManager

class VocalCommandModule:

    vocal_command_module = None

    def __init__(self):
        self.v_rec = None
        self.v_synt = None
        pass

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

    def run(self):

        command = self.recognize_command()
        print(command)
        state = StateManager.get_instance().get_state('state')