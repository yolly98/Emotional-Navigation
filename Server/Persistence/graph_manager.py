from py2neo import Graph

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

    def get_path(self, source, destination, excluded_way=-1):

        if self.graph is None:
            print("Graph DB not connected")
            return False

        # query that takes in account weights
        query = f"MATCH (a), (b), \
                path = shortestPath((a)-[r*]-(b)) \
                WHERE a.id = '{source}' and b.id = '{destination}' and NONE(rel in r WHERE rel.way_id = {excluded_way}) \
                RETURN relationships(path) as path"

        try:
            path = self.graph.run(query)
        except Exception as e:
            print(f"path not found [{e}]")
            return []

        path = path.data()
        if not path:
            print("Path not found")
            return None

        return path[0]['path']
