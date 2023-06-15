from deepface import DeepFace
import time
import cv2
from Client.state_manager import StateManager
from Client.communication_manager import CommunicationManager
from Client.InOutModules.arduino_button_module import ArduinoButton
from Client.Monitor.monitor import Monitor
import os
import pandas


class FaceProcessingModule:

    face_recognition_module = None

    def __init__(self):
        self.camera = -1
        self.max_attempts = 0
        self.emotion_samples = 0
        self.wait_time = 0
        self.period = 0
        self.detector = None
        self.model = None
        self.distance = None

    @staticmethod
    def get_instance():
        if FaceProcessingModule.face_recognition_module is None:
            FaceProcessingModule.face_recognition_module = FaceProcessingModule()
        return FaceProcessingModule.face_recognition_module

    def configure(self, camera, max_attempts, emotion_samples, wait_time, period, detector, model, distance):
        self.camera = camera
        self.max_attempts = max_attempts
        self.emotion_samples = emotion_samples
        self.wait_time = wait_time
        self.period = period
        self.detector = detector
        self.model = model
        self.distance = distance

    def get_picture(self, username):
        if self.camera == -1:
            print("camera not setted")
            return

        video = cv2.VideoCapture(self.camera)
        if video.isOpened:
            pass
        else:
            print("cam not available")
            exit(1)

        actual_path = os.path.abspath(os.path.dirname(__file__))
        ArduinoButton.get_instance().ledOff()
        while True:
            _, frame = video.read()
            cv2.imshow("Your face", frame)
            key = cv2.waitKey(1)
            if key == ord("s") or ArduinoButton.get_instance().check_button_pressed():
                path = os.path.join(actual_path, '..', 'Resources', 'UserImages', f'{username}.png')
                cv2.imwrite(path, frame)
                break

        ArduinoButton.get_instance().ledOff()
        video.release()
        cv2.destroyAllWindows()

    def find_face(self):

        if self.camera == -1:
            print("camera not setted")
            return False

        video = cv2.VideoCapture(self.camera)
        if video.isOpened:
            pass
        else:
            print("cam not available")
            exit(1)

        while True:

            time.sleep(self.wait_time)

            _, frame = video.read()

            try:
                DeepFace.extract_faces(frame, detector_backend=self.detector)
            except Exception:
                continue
            break

        video.release()
        return True

    def verify_user(self):

        if self.camera == -1:
            print("camera not setted")
            return

        video = cv2.VideoCapture(self.camera)
        if video.isOpened:
            pass
        else:
            print("cam not available")
            exit(1)

        actual_path = os.path.dirname(__file__)
        user_images_dir = os.path.join(actual_path, '..', 'Resources', 'UserImages')

        _, frame = video.read()
        img_path = os.path.join(user_images_dir, "temp.png")
        cv2.imwrite(img_path, frame)
        dfs = DeepFace.find(
            img_path=img_path,
            db_path=user_images_dir,
            enforce_detection=False,
            distance_metric=self.distance,
            detector_backend=self.detector,
            model_name=self.model
        )
        res = []
        username = None
        for df in dfs:
            res.append(df.to_dict())

        print(res)
        res = res[0]['identity']
        if 1 in res:
            username = res[1]
            username = username.replace(user_images_dir, '')
            username = username.replace('/', '')
            username = username.replace('.png', '')

        # remove the temporary files used to execute the model
        os.remove(img_path)
        all_tmp_files = os.listdir(user_images_dir)
        for tmp_file_name in all_tmp_files:
            name, extension = os.path.splitext(tmp_file_name)
            if extension == '.pkl':
                os.remove(os.path.join(user_images_dir, tmp_file_name))

        video.release()
        return username

    def get_emotion(self):

        if self.camera == -1:
            print("camera not setted")
            return

        video = cv2.VideoCapture(self.camera)
        if video.isOpened:
            print("cam available")
        else:
            print("cam not available")
            exit(1)

        emotions = {}
        dominant_emotion = None
        dominant_emotion_value = 0

        emotion_samples = 0
        for i in range(0, self.max_attempts):
            # check if enough emotions are collected
            if emotion_samples >= self.emotion_samples:
                break

            time.sleep(self.wait_time)

            _, frame = video.read()

            try:
                analyze = DeepFace.analyze(frame, actions=['emotion'], detector_backend=self.detector)
            except:
                print("no face") # [Test]
                continue

            emotion_samples += 1
            result = analyze[0]

            # print(result['dominant_emotion']) [Test]
            for emotion in result['emotion']:
                if emotion in emotions:
                    emotions[emotion] += result['emotion'][emotion]
                else:
                    emotions[emotion] = result['emotion'][emotion]

                if dominant_emotion is None or dominant_emotion_value < emotions[emotion]:
                    dominant_emotion = emotion
                    dominant_emotion_value = emotions[emotion]

        video.release()

        StateManager.get_instance().set_state('actual_emotion', dominant_emotion)
        return dominant_emotion

    @staticmethod
    def print_available_cameras():
        i = 0
        while True:  # change the range if there are more or less cameras
            try:
                cam = cv2.VideoCapture(i)
                if cam.isOpened():
                    print(f'Cam {i}: {cam.getBackendName()} available')
                else:
                    print(f'Cam {i}: {cam.getBackendName()} not available')
                cam.release()
                i += 1
            except Exception:
                break

    def run(self):
        while True:
            time.sleep(self.period)
            start_time = time.time()
            state = StateManager.get_instance().get_state('state')
            username = StateManager.get_instance().get_state('username')
            if username is not None and state == 'navigator':

                emotion = self.get_emotion()
                way = StateManager.get_instance().get_state('actual_way')
                pos = StateManager.get_instance().get_state('last_pos')
                timestamp = time.time()
                if not (emotion and username and way and timestamp and not way['street_name'] == ''):
                    pass
                else:
                    print(f"Get emotion success [{emotion}]")
                    request = dict()
                    request['username'] = username
                    request['way'] = way['street_name']
                    request['timestamp'] = timestamp
                    request['emotion'] = emotion
                    server_ip = StateManager.get_instance().get_state('server_ip')
                    server_port = StateManager.get_instance().get_state('server_port')
                    CommunicationManager.send(server_ip, server_port, 'POST', request, 'history')
                    Monitor.get_instance().collect_measure('emotions', f"{emotion}, {pos[0]}, {pos[1]}")
                    
            Monitor.get_instance().collect_measure('history_collector', time.time() - start_time)


if __name__ == "__main__":

    FaceProcessingModule.get_instance().configure(
        camera=1,
        max_attempts=10,
        emotion_samples=1,
        wait_time=1,
        period=60,
        detector="opencv",
        model="VGG-Face",
        distance="cosine"
    )

    ArduinoButton.get_instance().init('COM8')

    FaceProcessingModule.print_available_cameras()
    FaceProcessingModule.get_instance().find_face()
    print("face detected")
    emotion = FaceProcessingModule.get_instance().get_emotion()
    print(f'dominant emotion: {emotion}')
    FaceProcessingModule.get_instance().get_picture('default')
    username = FaceProcessingModule.get_instance().verify_user()
    print(f'{username} recognized')


