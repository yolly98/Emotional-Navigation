import speech_recognition as sr
import os
import asyncio
from threading import Thread, Lock
from pydub import AudioSegment
from pydub.playback import play
from edge_tts import VoicesManager, Communicate

if os.name == 'posix':
    from ctypes import *

    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

    asound = cdll.LoadLibrary('libasound.so')
    # Set error handler
    asound.snd_lib_error_set_handler(c_error_handler)


class VocalCommandModule:

    vocal_command_module = None

    def __init__(self):
        self.stt_model = None
        self.v_rec = None
        self.stt_service = None
        self.mic_device = None
        self.mic_timeout = 0
        self.command = None
        self.new_command = False
        self.rec_started = False
        self.tts_voice = None
        self.async_loop = None
        self.tts_started = False
        self.lock = Lock()

    @staticmethod
    def get_instance():
        if VocalCommandModule.vocal_command_module is None:
            VocalCommandModule.vocal_command_module = VocalCommandModule()
        return VocalCommandModule.vocal_command_module

    def init(self, stt_service='google', mic_device=None, mic_timeout=5):
        self.v_rec = sr.Recognizer()
        self.async_loop = asyncio.get_event_loop_policy().get_event_loop()
        voices = self.async_loop.run_until_complete((lambda: VoicesManager.create())())
        self.tts_voice = voices.find(Gender="Female", Language="it")[0]['Name']
        self.stt_service = stt_service
        self.mic_device = mic_device
        self.mic_timeout = mic_timeout

    def recognize_command(self):

        stt_service = self.stt_service
        device_index =self.mic_device

        # get audio from microphone
        with sr.Microphone(device_index=device_index) as source:
            # self.v_rec.adjust_for_ambient_noise(source)
            print("Speak now...")
            play(AudioSegment.from_wav(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'Resources',
                    'bip.wav'
                )
            ))
            try:
                audio = self.v_rec.listen(source, timeout=self.mic_timeout)
            except Exception as e:
                print(f"Microphone error [{e}]")
                self.say("Non ho capito, riprova") # IT
                self.rec_started = False
                return

        # Recognize audio by using Google or Whisper
        text = None
        try:
            if stt_service == 'whisper':
                text = self.v_rec.recognize_whisper(audio, language='italian')
            elif stt_service == 'google':
                text = self.v_rec.recognize_google(audio, language='it-IT')
        except sr.UnknownValueError:
            print("I have no understood, try again")
            text = ""
        except sr.RequestError as e:
            print(f"Vocal Command Recognizer doesn't work {e}")
            text = ""
        print(text)
        with self.lock:
            self.command = text
            self.new_command = True
            self.rec_started = False
        return text

    def say(self, text):
        if text is None or text == "":
            return
        with self.lock:
            if not self.tts_started:
                t = Thread(target=self.synthesize_text, args=(text,), daemon=True)
                t.start()
                self.tts_started = True

    def start_command_recognizer(self):
        with self.lock:
            if not self.rec_started:
                t = Thread(target=self.recognize_command, args=(), daemon=True)
                t.start()
                self.rec_started = True

    def synthesize_text(self, text):
        communicate = Communicate(text, self.tts_voice)
        self.async_loop.run_until_complete(
            (lambda: communicate.save(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'Resources',
                    'temp.mp3'
                ))
             )()
        )
        play(AudioSegment.from_mp3(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'Resources',
                'temp.mp3'
            )
        ))
        with self.lock:
            self.tts_started = False

    def get_command(self):
        if not self.new_command:
            return None
        with self.lock:
            text = self.command
            self.command = None
            self.new_command = False
            return text


if __name__ == '__main__':

    VocalCommandModule.get_instance().init(stt_service='google', mic_device=None, mic_timeout=5)
    while True:

        # command = VocalCommandModule.get_instance().recognize_command()
        t = Thread(target=VocalCommandModule.get_instance().recognize_command, args=(), daemon=True)
        t.start()
        t.join()
        command = VocalCommandModule.get_instance().get_command()
        print(command)
        VocalCommandModule.get_instance().say(command)
