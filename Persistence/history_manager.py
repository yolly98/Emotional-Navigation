import sqlite3
import os
from datetime import datetime, timedelta
import mysql.connector


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

        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="smart_navigation"
            )
        except mysql.connector.Error as e:
            print(f"Mysql Execution Error [{e}]")
            return False

        return True

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def store_sample(self, user_id, way_id, emotion, timestamp):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "INSERT INTO history (user_id, way_id, emotion, timestamp) \
                            VALUES( %s, %s, %s, %s)"
            try:
                cursor.execute(query, (user_id, way_id, emotion, timestamp))
                self.conn.commit()
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
                return False
            return True

    def get_emotions(self, user_id, way_id):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM history WHERE user_id = %s and way_id = %s"
            try:
                cursor.execute(query, (user_id, way_id))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")

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
            cursor = self.conn.cursor(prepared=True)
            query = "DELETE FROM history WHERE user_id = %s"
            try:
                cursor.execute(query, (user_id,))
                self.conn.commit()
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
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
