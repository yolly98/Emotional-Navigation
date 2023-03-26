from deepface import DeepFace
import time
import cv2


class EmotionDetector:

    def __init__(self, camera=-1, iterations=1, wait_time=1):
        self.camera = camera
        self.iterations = iterations
        self.wait_time = wait_time
        pass

    def set_camera(self, camera):
        self.camera = camera

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

            for emotion in analyze[0]['emotion']:
                if emotion in emotions:
                    emotions[emotion] += analyze[0]['emotion'][emotion]
                else:
                    emotions[emotion] = analyze[0]['emotion'][emotion]

                if dominant_emotion is None or  dominant_emotion_value < emotions[emotion]:
                    dominant_emotion = emotion
                    dominant_emotion_value = emotions[emotion]

        video.release()

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


if __name__ == "__main__":
    emotion_detector = EmotionDetector(1, 20, 0.3)
    EmotionDetector.print_available_cameras()
    emotion = emotion_detector.get_emotion()
    print(f"Detected: {emotion}")