from datetime import datetime, timedelta
from pymongo import MongoClient


class UserDataManager:

    user_data_manager = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if UserDataManager.user_data_manager is None:
            UserDataManager.user_data_manager = UserDataManager()
        return UserDataManager.user_data_manager

    def open_connection(self):
        self.conn = MongoClient('mongodb://admin:password@localhost:27017/')

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def store_sample(self, username, way, emotion, timestamp):

        if way == "":
            return True

        username = username.lower()
        if self.conn is None:
            return False

        sample = {
            'username': username,
            'way': way,
            'emotion': emotion,
            'timestamp': timestamp
        }
        db = self.conn['emotional_navigation'].history
        try:
            db.insert_one(sample)
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def get_emotions(self, username, way):
        username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return []
        db = self.conn['emotional_navigation'].history
        samples = db.find(
            {
                '$and': [
                    {'username': username},
                    {'way': way}
                ]
            }
        )
        if samples is None:
            return []
        emotions = []
        for sample in samples:
            emotions.append(sample['emotion'])
        return emotions

    def delete_history_of_a_user(self, username):

        username = username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return False
        db = self.conn['emotional_navigation'].history
        try:
            db.delete_many({'username': username})
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def delete_history_by_user_way(self, username, way):

        username = username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return False
        db = self.conn['emotional_navigation'].history
        try:
            db.delete_many(
                {
                    '$and': [
                        {'username': username},
                        {'way': way}
                    ]
                }
            )
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def create_user(self, username, image):

        username = username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return False
        db = self.conn['emotional_navigation'].user
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

    def delete_user(self, username):

        username = username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return False
        db = self.conn['emotional_navigation'].user
        try:
            db.delete_one({'username': username})
        except Exception as e:
            print(f"Mongo execution error [{e}]")
            return False
        return True

    def get_user_image(self, username):
        username = username.lower()
        if self.conn is None:
            print("Closed mongo connection")
            return None
        db = self.conn['emotional_navigation'].user
        user = db.find_one({'username': username})
        if user is None:
            return None
        return user['image']


if __name__ == '__main__':
    history = UserDataManager().get_instance()
    history.open_connection()
    history.create_user("user0", '')
    history.store_sample("user0", "Via Alfonso", 'happy', datetime.now())
    history.store_sample("user0", "Via Alfonso", 'sad', datetime.now() + timedelta(minutes=1))
    history.store_sample("user0", "Via Giacomo", 'disgust', datetime.now() + timedelta(minutes=2))
    history.store_sample("user0", "Via Giacomo", 'angry', datetime.now() + timedelta(minutes=3))
    history.store_sample("user0", "Via Giacomo", 'fear', datetime.now() + timedelta(minutes=4))
    emotions = history.get_emotions("user0", "Via Alfonso")
    print(f"way: Via Alfonso emotions: {emotions}")
    emotions = history.get_emotions("user0", "Via Giacomo")
    print(f"way: Via Giacomo emotions: {emotions}")
    history.delete_history_of_a_user("user0")
    history.delete_user("user0")
    history.close_connection()