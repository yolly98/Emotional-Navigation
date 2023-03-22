import sqlite3
import os
from datetime import datetime, timedelta


class HistoryManager:

    history_manager = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if HistoryManager.history_manager is None:
            HistoryManager.history_manager = HistoryManager()
        return HistoryManager.history_manager

    def open_connection(self):
        db_path = os.path.join(os.path.abspath('..'), 'Persistence', 'sql_smart_navigation.db')
        if not os.path.exists(db_path):
            print("Sqlite db doesn't exist")
            return False
        try:
            self.conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            print(f"Sqlite Connection Error [{e}]")
        return True

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def store_sample(self, user_id, way_id, emotion, timestamp):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "INSERT INTO history (user_id, way_id, emotion, timestamp) \
                            VALUES( ?, ?, ?, ?)"
            try:
                cursor.execute(query, (user_id, way_id, emotion, timestamp))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
                return False
            return True

    def get_emotions(self, user_id, way_id):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM history WHERE user_id = ? and way_id = ?"
            try:
                cursor.execute(query, (user_id, way_id))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")

            res = cursor.fetchall()
            if res is None:
                return False

            emotions = []
            for sample in res:
                emotions.append(sample[2])
            return emotions
        pass

    def delete_history_of_a_user(self, user_id):

        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "DELETE FROM history WHERE user_id = ?"
            try:
                cursor.execute(query, (user_id,))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
                return False
            return True


if __name__ == '__main__':
    history = HistoryManager().get_instance()
    history.open_connection()
    history.store_sample(0, 0, 'happy', datetime.now())
    history.store_sample(0, 0, 'sad', datetime.now() + timedelta(minutes=1))
    history.store_sample(0, 1, 'disgust', datetime.now() + timedelta(minutes=2))
    history.store_sample(0, 1, 'angry', datetime.now() + timedelta(minutes=3))
    history.store_sample(0, 1, 'fear', datetime.now() + timedelta(minutes=4))
    emotions = history.get_emotions(0, 0)
    print(f"way_id: {0} emotions: {emotions}")
    emotions = history.get_emotions(0, 1)
    print(f"way_id: {1} emotions: {emotions}")
    history.delete_history_of_a_user(0)
    history.close_connection()
