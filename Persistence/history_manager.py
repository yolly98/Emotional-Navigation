import sqlite3
import os


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

    def store_sample(self):
        pass

    def get_sample(self, way_id):
        pass

