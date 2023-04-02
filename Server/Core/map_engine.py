from Utility.utility_functions import calculate_distance, visualize_path, print_path
from Utility.point import Point
from Server.Persistence.mongo_map_manager import MongoMapManager
from Server.Persistence.graph_manager import GraphManager


class MapEngine:

    @staticmethod
    def calculate_path(source, destination, estimated=True, excluded_way=-1):

        graph_manager = GraphManager.get_instance()
        graph_manager.open_connection()

        map = MongoMapManager.get_instance()
        map.open_connection()

        source = (map.get_nearest_node(source.get_lat(), source.get_lon()))
        if source is False:
            print("Source position not found")
            return None
        source_id = source.get('id')
        destination = (map.get_node_by_coord(destination.get_lat(), destination.get_lon()))
        if destination is False:
            print("Destination position not found")
            return None
        destination_id = destination.get('id')
        if estimated:
            ret = graph_manager.get_estimated_path(source_id, destination_id, excluded_way)
        else:
            ret = graph_manager.get_path(source_id, destination_id)
        graph_manager.close_connection()
        if ret is None:
            return None

        neo4j_path = ret['ways']
        path = []
        for relationship in neo4j_path:
            r = relationship
            start_node = map.get_node(int(r.start_node.get('id')))
            end_node = map.get_node(int(r.end_node.get('id')))
            way_properties = map.get_way(r['way_id'])
            way = dict()
            way['way'] = way_properties
            way['start_node'] = start_node
            way['end_node'] = end_node
            if way_properties.get('name') == "" and way_properties.get('alt_name') == "" and way_properties.get('ref') == "":
                way_properties.set('name', "Unknown")
            path.append(way)

        if not path:
            return None

        return path

    @staticmethod
    def calculate_path_avoid_way_name(source, destination, way_name, estimated=True):

        graph_manager = GraphManager.get_instance()
        map = MongoMapManager.get_instance()

        map.open_connection()
        ways = map.get_way_by_name(way_name)

        graph_manager.open_connection()

        if estimated:
            distance = None
            excluded_way_id = None
            for way in ways:
                node = map.get_node(way.get('start_node'))
                node = Point(node.get('lat'), node.get('lon'))
                d = calculate_distance(source, node)
                if distance is None or d < distance:
                    distance = d
                    excluded_way_id = way.get('id')

            res = MapEngine.calculate_path(source, destination, True, excluded_way_id)
        else:
            # update length with big value to avoid the way in the path calculation
            for way in ways:
                graph_manager.update_way_length(way.get('id'), 1000)
            graph_manager.close_connection()

            res = MapEngine.calculate_path(source, destination, False)

            graph_manager.open_connection()
            # restore updated length
            for way in ways:
                graph_manager.update_way_length(way.get('id'), way.get('length'))

        map.close_connection()
        graph_manager.close_connection()

        return res

# --------------------------------


if __name__ == "__main__":

    source = Point('42.3323892', '12.2695975')
    destination = Point('42.3358463', '12.3038538')

    path = MapEngine.calculate_path(source, destination, True)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    # if path:
    #    visualize_path(path, True)

    path = MapEngine.calculate_path(source, destination, False)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    # if path:
    #    visualize_path(path, True)

    path = MapEngine.calculate_path_avoid_way_name(source, destination, "Via Fontanasecca", True)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    # if path:
    #   visualize_path(path, True)

    path = MapEngine.calculate_path_avoid_way_name(source, destination, "Via Fontanasecca", False)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")
    # if path:
    #    visualize_path(path, True)
