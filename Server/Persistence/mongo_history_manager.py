from datetime import datetime, timedelta
from pymongo import MongoClient


class MongoHistoryManager:

    history_manager = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if MongoHistoryManager.history_manager is None:
            MongoHistoryManager.history_manager = MongoHistoryManager()
        return MongoHistoryManager.history_manager

    def open_connection(self):
        self.conn = MongoClient('mongodb://admin:password@localhost:27017/')

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def store_sample(self, username, way_id, emotion, timestamp):
        if self.conn is None:
            return False

        sample = {
            'username': username,
            'way_id': int(way_id),
            'emotion': emotion,
            'timestamp': timestamp
        }
        db = self.conn['smart_navigation'].history
        try:
            db.insert_one(sample)
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def get_emotions(self, username, way_id):
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].history
        samples = db.find(
            {
                '$and': [
                    {'username': username},
                    {'way_id': way_id}
                ]
            }
        )
        if samples is None:
            return None
        emotions = []
        for sample in samples:
            emotions.append(sample['emotion'])
        return emotions

    def delete_history_of_a_user(self, username):

        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].history
        try:
            db.delete_many({'username': username})
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def create_user(self, username, image):
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].user
        user = {
            "username": username,
            "image": image
        }
        try:
            db.insert_one(user)
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def get_user_image(self, username):
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].history
        user = db.find_one({'username': username})
        if user is None:
            return None
        return user['image']


if __name__ == '__main__':
    history = MongoHistoryManager().get_instance()
    history.open_connection()
    history.store_sample("user0", 0, 'happy', datetime.now())
    history.store_sample("user0", 0, 'sad', datetime.now() + timedelta(minutes=1))
    history.store_sample("user0", 1, 'disgust', datetime.now() + timedelta(minutes=2))
    history.store_sample("user0", 1, 'angry', datetime.now() + timedelta(minutes=3))
    history.store_sample("user0", 1, 'fear', datetime.now() + timedelta(minutes=4))
    emotions = history.get_emotions("user0", 0)
    print(f"way_id: {0} emotions: {emotions}")
    emotions = history.get_emotions("user0", 1)
    print(f"way_id: {1} emotions: {emotions}")
    history.delete_history_of_a_user("user0")

    history.close_connection()