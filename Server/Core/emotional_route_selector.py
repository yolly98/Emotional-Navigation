from Server.Persistence.mongo_history_manager import MongoHistoryManager
from Server.Core.map_engine import MapEngine

# emotion values for balance
ANGRY = -5
DISGUST = -1
FEAR = -3
HAPPY = 2
SAD = -2
SURPRISE = 5
NEUTRAL = 1

MAX_LENGTH_PENALTY = 0.1  # 10%


class EmotionalRouteSelector:

    @staticmethod
    def get_path(username, source, destination):

        path = MapEngine.calculate_path(source, destination)
        if path is None:
            return None
        if username is None:
            return path
        evaluated_path = EmotionalRouteSelector.evaluate_path(path, username)
        original_length = evaluated_path['length']
        while True:
            if evaluated_path['emotional_path'][0]['balance'] >= 0:
                break
            else:
                new_path = MapEngine.calculate_path(source, destination, excluded_way=evaluated_path['emotional_path'][0]['way_id'])
                if new_path is None:
                    break
                new_evaluated_path = EmotionalRouteSelector.evaluate_path(new_path, username)
                if new_evaluated_path['overall_balance'] > evaluated_path['overall_balance'] \
                        and evaluated_path['length'] + original_length * MAX_LENGTH_PENALTY > new_evaluated_path['length']:
                    path = new_path
                    evaluated_path = new_evaluated_path
                else:
                    print("second path is not better")
                    break
        return path

    @staticmethod
    def evaluate_path(path, username):

        # get all emotions related to the path from user's history
        MongoHistoryManager.get_instance().open_connection()
        emotional_path = []
        length = 0
        overall_balance = 0
        for way in path:
            way_id = way['way'].get('id')
            length += way['way'].get('length')
            emotions = MongoHistoryManager.get_instance().get_emotions(username, way_id)

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

            emotion_balance = emotion_balance * way['way'].get('length')
            overall_balance += emotion_balance
            emotional_path.append({'way_id': way_id, 'balance': emotion_balance})

        MongoHistoryManager.get_instance().close_connection()
        res = dict()
        res['length'] = length
        res['overall_balance'] = overall_balance
        res['emotional_path'] = sorted(emotional_path, key=lambda k: k['balance'])
        print(res)

        return res
