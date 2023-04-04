from Utility.utility_functions import calculate_distance, visualize_path, print_path
from Utility.point import Point
from Utility.way import Way
from Utility.gnode import GNode
from Server.Persistence.mongo_map_manager import MongoMapManager
from Server.Persistence.graph_manager import GraphManager


class MapEngine:

    @staticmethod
    def calculate_path(source, destination, excluded_way=-1):

        graph_manager = GraphManager.get_instance()
        graph_manager.open_connection()

        map = MongoMapManager.get_instance()
        map.open_connection()

        source = (map.get_nearest_node(source.get_lat(), source.get_lon()))
        if source is False:
            print("Source position not found")
            return None
        source_id = source.get('id')
        destination = (map.get_nearest_node(destination.get_lat(), destination.get_lon()))
        if destination is False:
            print("Destination position not found")
            return None
        destination_id = destination.get('id')
        ret = graph_manager.get_path(source_id, destination_id, excluded_way)
        graph_manager.close_connection()
        if ret is None:
            return None

        neo4j_path = ret
        path = []

        for relationship in neo4j_path:
            way = dict()
            neo4j_way = relationship
            neo4j_start_node = relationship.start_node
            neo4j_end_node = relationship.end_node

            start_node = GNode(
                id=neo4j_start_node.get('id'),
                type=neo4j_start_node.get('type'),
                name=neo4j_start_node.get('name'),
                lat=neo4j_start_node.get('lat'),
                lon=neo4j_start_node.get('lon')
            )
            end_node = GNode(
                id=neo4j_end_node.get('id'),
                type=neo4j_end_node.get('type'),
                name=neo4j_end_node.get('name'),
                lat=neo4j_end_node.get('lat'),
                lon=neo4j_end_node.get('lon')
            )
            way_properties = Way(
                id=neo4j_way['way_id'],
                name=neo4j_way['name'],
                alt_name=neo4j_way['alt_name'],
                ref=neo4j_way['ref'],
                speed=neo4j_way['speed'],
                length=neo4j_way['length'],
                start_node=neo4j_way['start_node'],
                end_node=neo4j_way['end_node']
            )
            way['way'] = way_properties
            way['start_node'] = start_node
            way['end_node'] = end_node
            path.append(way)

        if not path:
            return None

        return path

    @staticmethod
    def calculate_path_avoid_way_name(source, destination, way_name):

        graph_manager = GraphManager.get_instance()
        map = MongoMapManager.get_instance()

        map.open_connection()
        ways = map.get_way_by_name(way_name)

        graph_manager.open_connection()


        distance = None
        excluded_way_id = None
        for way in ways:
            node = map.get_node(way.get('start_node'))
            node = Point(node.get('lat'), node.get('lon'))
            d = calculate_distance(source, node)
            if distance is None or d < distance:
                distance = d
                excluded_way_id = way.get('id')

        res = MapEngine.calculate_path(source, destination, excluded_way_id)

        map.close_connection()
        graph_manager.close_connection()

        return res

# --------------------------------


if __name__ == "__main__":

    source = Point('42.3323892', '12.2695975')
    destination = Point('42.3358463', '12.3038538')

    path = MapEngine.calculate_path(source, destination)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    if path:
        visualize_path(path, True)

    path = MapEngine.calculate_path_avoid_way_name(source, destination, "Via Fontanasecca")
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    if path:
        visualize_path(path, True)
