from deepface import DeepFace
import time
import cv2
from Client.state_manager import StateManager
from Client.communication_manager import CommunicationManager
import os

class FaceRecognitionModule:

    face_recognition_module = None

    def __init__(self):
        self.camera = -1
        self.iterations = 0
        self.wait_time = 0
        self.period = 0
        self.user_detection_attempts = 0

    @staticmethod
    def get_instance():
        if FaceRecognitionModule.face_recognition_module is None:
            FaceRecognitionModule.face_recognition_module = FaceRecognitionModule()
        return FaceRecognitionModule.face_recognition_module

    def configure(self, camera, iterations, wait_time, period, user_detection_attempts=20):
        self.camera = camera
        self.iterations = iterations
        self.wait_time = wait_time
        self.period = period
        self.user_detection_attempts = user_detection_attempts

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

        root_path = StateManager.get_instance().get_state('root_path')
        while True:
            _, frame = video.read()
            cv2.imshow("Your face", frame)
            key = cv2.waitKey(1)
            if key == ord("s"):
                path = os.path.join(root_path, "InputModule", "UserImages", f"{username}.png")
                cv2.imwrite(path, frame)
                break

        video.release()
        cv2.destroyAllWindows()

    def find_face(self, test=False):

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

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            model_path = None
            if test is False:
                root_path = StateManager.get_instance().get_state('root_path')
                model_path = os.path.join(root_path, "InputModule", "models", "haarcascade_frontalface_default.xml")
            else:
                model_path = os.path.join("models", "haarcascade_frontalface_default.xml")
            face_cascade = cv2.CascadeClassifier(model_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            if len(faces) > 0:
                break

        video.release()
        return True

    def verify_user(self, user_images_dir=None):

        if self.camera == -1:
            print("camera not setted")
            return

        video = cv2.VideoCapture(self.camera)
        if video.isOpened:
            pass
        else:
            print("cam not available")
            exit(1)

        if user_images_dir is None:
            root_path = StateManager.get_instance().get_state('root_path')
            user_images_dir = os.path.join(root_path, "InputModule", "UserImages")
        for file_name in os.listdir(user_images_dir):
            if file_name.endswith('.png'):
                for i in range(self.user_detection_attempts):

                    time.sleep(self.wait_time)

                    _, frame = video.read()

                    file_path = os.path.join(user_images_dir, file_name)
                    res = DeepFace.verify(frame, file_path, enforce_detection=False)
                    if res['verified']:
                        username = file_name.replace('.png', '')
                        return username

        video.release()
        return None

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

        for i in range(self.iterations):

            time.sleep(self.wait_time)

            _, frame = video.read()

            try:
                analyze = DeepFace.analyze(frame, actions=['emotion'])
            except:
                print("no face")
                continue
            result = analyze[0]

            print(result['dominant_emotion'])
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
        for i in range(4):  # change the range if there are more or less cameras
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                print(f'Cam {i}: {cam.getBackendName()} available')
            else:
                print(f'Cam {i}: {cam.getBackendName()} not available')
            cam.release()

    def run(self):
        while True:
            if StateManager.get_instance().get_state('emotion_module'):
                emotion = self.get_emotion()
                username = StateManager.get_instance().get_state('username')
                way = StateManager.get_instance().get_state('actual_way')
                timestamp = time.time()
                if not (emotion and username and way and timestamp):
                    pass
                else:
                    print("Get emotion success")
                    request = dict()
                    request['username'] = username
                    request['way_id'] = way['way'].get('id')
                    request['timestamp'] = timestamp
                    request['emotion'] = emotion
                    server_ip = StateManager.get_instance().get_state('server_ip')
                    server_port = StateManager.get_instance().get_state('server_port')
                    CommunicationManager.send(server_ip, server_port, 'POST', request, 'history')
            time.sleep(self.period)


if __name__ == "__main__":
    FaceRecognitionModule.get_instance().configure(1, 20, 0.3, 60, 5)
    # FaceRecognitionModule.print_available_cameras()
    # FaceRecognitionModule.get_instance().run()
    FaceRecognitionModule.get_instance().find_face(True)
    print("face detected")
    username = FaceRecognitionModule.get_instance().verify_user('UserImages')
    print(username)
