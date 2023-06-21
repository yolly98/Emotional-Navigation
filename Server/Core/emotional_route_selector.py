from Server.Persistence.user_data_manager import UserDataManager
from Server.Core.map_engine import MapEngine
import json
import math

# emotion values for balance
ANGRY = -5
DISGUST = -1
FEAR = -3
HAPPY = 2
SAD = -2
SURPRISE = 5
NEUTRAL = 1


class EmotionalRouteSelector:

    @staticmethod
    def get_path(username, source, destination):

        paths = MapEngine.calculate_path(source, destination, [])
        if paths is None:
            return None
        if username is None:
            return paths[0]

        evaluated_paths = []
        for path in paths:
            evaluated_path = EmotionalRouteSelector.evaluate_path(path, username)
            evaluated_paths.append(evaluated_path)

        # search the best emotional path
        best_path = None
        for evaluated_path in evaluated_paths:
            # print(json.dumps(paths[i], indent=4))
            print(f"length: {evaluated_path['distance'] / 1000} km | duration: {math.floor(evaluated_path['time'] / 60000)} minutes")
            if best_path is None or \
                    best_path['overall_balance'] < evaluated_path['overall_balance'] or \
                    (best_path['overall_balance'] == evaluated_path['overall_balance'] and best_path['time'] > evaluated_path['time']):
                best_path = evaluated_path

        return best_path

    @staticmethod
    def evaluate_path(path, username):

        # get all emotions related to the path from user's history
        UserDataManager.get_instance().open_connection()
        overall_balance = 0
        for way in path['ways']:

            way_name = way['street_name']
            if way_name == "":
                continue
            emotions = UserDataManager.get_instance().get_emotions(username, way_name)

            emotion_balance = 0
            for emotion in emotions:
                if emotion == 'angry':
                    emotion_balance += ANGRY
                elif emotion == 'disgust':
                    emotion_balance += DISGUST
                elif emotion == 'fear':
                    emotion_balance += FEAR
                elif emotion == 'happy':
                    emotion_balance += HAPPY
                elif emotion == 'sad':
                    emotion_balance += SAD
                elif emotion == 'surprise':
                    emotion_balance += SURPRISE
                elif emotion == 'neutral':
                    emotion_balance += NEUTRAL

            emotion_balance = emotion_balance * way['distance']
            overall_balance += emotion_balance

        UserDataManager.get_instance().close_connection()
        evaluated_path = path.copy()
        evaluated_path['overall_balance'] = overall_balance

        return evaluated_path


if __name__ == "__main__":

    start_point = [42.332047177395246, 12.264483264442843]
    destination = 'Via Magenta, Ronciglione'

    UserDataManager.get_instance().open_connection()
    UserDataManager.get_instance().create_user('test', '')
    UserDataManager.get_instance().close_connection()

    path = EmotionalRouteSelector.get_path('test', start_point, destination)
    print(json.dumps(path, indent=4))
    MapEngine.plot_path(path)

    UserDataManager.get_instance().open_connection()
    UserDataManager.get_instance().store_sample('test', 'Strada Provinciale Ronciglionese', 'sad', 0)
    UserDataManager.get_instance().store_sample('test', 'Strada Provinciale Ronciglionese', 'sad', 0)
    UserDataManager.get_instance().store_sample('test', 'Strada Provinciale Ronciglionese', 'angry', 0)
    UserDataManager.get_instance().close_connection()

    path = EmotionalRouteSelector.get_path('test', start_point, destination)
    print(json.dumps(path, indent=4))
    MapEngine.plot_path(path)

    UserDataManager.get_instance().open_connection()
    UserDataManager.get_instance().delete_history_of_a_user('test')
    UserDataManager.get_instance().delete_user('test')
    UserDataManager.get_instance().close_connection()

