from Utility.way import Way
from Utility.gnode import GNode
import mysql.connector


class MapSqlManager:

    map_sql_manager = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if MapSqlManager.map_sql_manager is None:
            MapSqlManager.map_sql_manager = MapSqlManager()
        return MapSqlManager.map_sql_manager

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

    def get_way(self, way_id):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM way WHERE id = %s LIMIT 1"
            try:
                cursor.execute(query, (way_id,))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
            res = cursor.fetchone()
            if res is None:
                return False
            res = Way(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7])
            return res

    def get_way_by_start_node(self, start_node):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM way WHERE start_node = %s"
            try:
                cursor.execute(query, (start_node,))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_way_by_name(self, way_name):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM way WHERE name = %s"
            try:
                cursor.execute(query, (way_name,))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
                return False
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_way_by_end_node(self, end_node):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM way WHERE end_node = %s"
            try:
                cursor.execute(query, (end_node,))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
                return False
            res = cursor.fetchall()
            if res is None:
                return False
            ways = []
            for row in res:
                way = Way(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                ways.append(way)
            return ways

    def get_way_by_node(self, node):
        if self.conn is None:
            return False
        else:
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM way WHERE end_node = %s or start_node = %s"
            try:
                cursor.execute(query, (node, node))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
                return False
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
            cursor = self.conn.cursor(prepared=True)
            query = "SELECT * FROM node WHERE id = %s LIMIT 1"
            try:
                cursor.execute(query, (node_id,))
            except mysql.connector.Error as e:
                print(f"Mysql Execution Error [{e}]")
            res = cursor.fetchone()
            if res is None:
                return False
            res = GNode(res[0], res[1], res[2], res[3], res[4])
            return res

    def get_nodes_by_coord(self, max_lat, min_lat, max_lon, min_lon):
        if self.conn is None:
            return False
        cursor = self.conn.cursor(prepared=True)
        query = "SELECT * FROM node \
        WHERE lat < %s and lat > %s and \
        lon < %s and lon > %s "
        try:
            cursor.execute(query, (max_lat, min_lat, max_lon, min_lon))
        except mysql.connector.Error as e:
            print(f"Mysql Execution Error [{e}]")
        res = cursor.fetchall()
        if res is None:
            return False
        nodes = []
        for row in res:
            node = GNode(row[0], row[1], row[2], row[3], row[4])
            nodes.append(node)
        return nodes

    def get_node_by_coord(self, lat, lon):
        if self.conn is None:
            return False
        cursor = self.conn.cursor(prepared=True)
        query = "SELECT * FROM node \
        WHERE lat = %s and lon = %s"
        try:
            cursor.execute(query, (lat, lon))
        except mysql.connector.Error as e:
            print(f"Mysql Execution Error [{e}]")
        res = cursor.fetchone()
        if res is None:
            return False
        res = GNode(res[0], res[1], res[2], res[3], res[4])
        return res

    def get_nearest_node(self, lat, lon):

        if self.conn is None:
            return False
        cursor = self.conn.cursor(prepared=True)

        query = "SELECT id, type, name, lat, lon, \
                SQRT(POW(69.1 * (lat - %s), 2) + POW(69.1 * (%s - lon) * COS(lat / 57.3), 2)) AS distance \
                FROM ordered_points_table \
                WHERE lat < %s + '0.001' and lat > %s - '0.001' \
                and lon < %s + '0.001' and lon > %s - '0.001' \
                ORDER BY distance \
                LIMIT 1"
        try:
            cursor.execute(query, (lat, lon, lat, lat, lon, lon))
        except mysql.connector.Error as e:
            print(f"Mysql Execution Error [{e}]")
        res = cursor.fetchone()
        if res is None:
            return False
        res = GNode(res[0], res[1], res[2], res[3], res[4])
        return res


if __name__ == '__main__':
    map_sql_manager = MapSqlManager().get_instance()
    map_sql_manager.open_connection()
    way = map_sql_manager.get_way(115)
    node = map_sql_manager.get_node(248140361)
    print(way)
    print(node)
    node = map_sql_manager.get_node_by_coord('42.3300045', '12.2653073')
    print(node)
    ways = map_sql_manager.get_way_by_node(844191299)
    if ways is False:
        print("Way: Unknown")
    else:
        print(f"Way: {ways[0].get('name')}")

    node = map_sql_manager.get_nearest_node('42.3323892', '12.2695975')
    print(node)
    map_sql_manager.close_connection()
