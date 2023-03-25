from py2neo import Graph
from Utility.utility import Point


class GraphManager:

    graph_manager = None

    def __init__(self):
        self.graph = None

    @staticmethod
    def get_instance():
        if GraphManager.graph_manager is None:
            GraphManager.graph_manager = GraphManager()
        return GraphManager.graph_manager

    def open_connection(self):
        try:
            self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
        except Exception as e:
            print("Connection to graph db failed")
            self.graph = None
            return False
        return True

    def close_connection(self):
        self.graph = None

    def get_path(self, source, destination):

        if self.graph is None:
            print("Graph DB not connected")
            return False

        # query that takes in account weights
        query = f"MATCH (a), (b)\
                WHERE a.id = '{source}' and b.id = '{destination}' \
                CALL apoc.algo.dijkstra(a, b, 'TO', 'length') \
                YIELD path \
                RETURN relationships(path) as ways"

        try:
            path = self.graph.run(query)
        except Exception as e:
            print(f"path not found [{e}]")
            return []

        path = path.data()
        if not path:
            print("Path not found")
            return None

        path = path[0]

        return path

    def update_way_length(self, way_id, new_length):
        if self.graph is None:
            print("Graph DB not connected")
            return False

        query = f"MATCH ()-[r:TO]-() WHERE r.way_id = {way_id} SET r.length = {new_length}"
        try:
            self.graph.run(query)
        except Exception as e:
            print(f"Update error for way_id: {way_id} [{e}]")
            return False
        return True

