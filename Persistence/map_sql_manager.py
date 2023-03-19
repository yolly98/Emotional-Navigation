import sqlite3
from Utility.utility import Way, GNode
import os


class MapSqlManager:

    map_sql_manager = None

    def __init__(self):
        self.conn = None

    def open_connection(self):
        db_path = os.path.join(os.path.abspath('..'), 'Persistence', 'sql_smart_navigation.db')
        print(db_path)
        if not os.path.exists(db_path):
            print("Sqlite db doesn't exist")
            return False
        try:
            self.conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            print(f"Sqlite Connection Error [{e}]")

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def get_way(self, way_id):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM way WHERE id = ? LIMIT 1"
            try:
                cursor.execute(query, (way_id,))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
            res = cursor.fetchone()
            if res is None:
                return False
            res = Way(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7])
            return res

    def get_way_from_start_node(self, start_node):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM way WHERE start_node = ?"
            try:
                cursor.execute(query, (start_node,))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_way_from_name(self, way_name):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM way WHERE name = ?"
            try:
                cursor.execute(query, (way_name,))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_way_from_end_node(self, end_node):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM way WHERE end_node = ?"
            try:
                cursor.execute(query, (end_node,))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_node(self, node_id):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor()
            query = "SELECT * FROM node WHERE id = ? LIMIT 1"
            try:
                cursor.execute(query, (node_id,))
            except sqlite3.Error as e:
                print(f"Sqlite Execution Error [{e}]")
            res = cursor.fetchone()
            if res is None:
                return False
            res = GNode(res[0], res[1], res[2], res[3], res[4])
            return res

    def get_nodes_from_coord(self, max_lat, min_lat, max_lon, min_lon):
        if self.conn is None:
            return False
        cursor = self.conn.cursor()
        query = "SELECT * FROM node \
        WHERE lat < ? and lat > ? and \
        lon < ? and lon > ? "
        try:
            cursor.execute(query, (max_lat, min_lat, max_lon, min_lon))
        except sqlite3.Error as e:
            print(f"Sqlite Execution Error [{e}]")
        res = cursor.fetchall()
        if res is None:
            return False
        nodes = []
        for row in res:
            node = GNode(row[0], row[1], row[2], row[3], row[4])
            nodes.append(node)
        return nodes

    @staticmethod
    def get_instance():
        if MapSqlManager.map_sql_manager is None:
            MapSqlManager.map_sql_manager = MapSqlManager()
        return MapSqlManager.map_sql_manager


if __name__ == '__main__':
    map_sql_manager = MapSqlManager().get_instance()
    map_sql_manager.open_connection()
    way = map_sql_manager.get_way(115)
    node = map_sql_manager.get_node(248140361)
    print(way)
    print(node)
    map_sql_manager.close_connection()
