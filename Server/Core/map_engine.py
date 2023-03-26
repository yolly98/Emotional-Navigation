from Utility.utility_functions import calculate_distance, visualize_path, print_path
from Utility.point import Point
from Server.Persistence.map_sql_manager import MapSqlManager
from Server.Persistence.graph_manager import GraphManager


class MapEngine:

    @staticmethod
    def calculate_path(source, destination):

        graph_manager = GraphManager.get_instance()
        graph_manager.open_connection()

        sql_manager = MapSqlManager.get_instance()
        sql_manager.open_connection()

        source = (sql_manager.get_nearest_node(source.get_lat(), source.get_lon()))
        if source is False:
            print("Source position not found")
            return None
        source_id = source.get('id')
        destination = (sql_manager.get_node_by_coord(destination.get_lat(), destination.get_lon()))
        if destination is False:
            print("Destination position not found")
            return None
        destination_id = destination.get('id')
        ret = graph_manager.get_path(source_id, destination_id)
        graph_manager.close_connection()
        if ret is None:
            return {}

        neo4j_path = ret['ways']
        path = []
        for relationship in neo4j_path:
            r = relationship
            start_node = sql_manager.get_node(int(r.start_node.get('id')))
            end_node = sql_manager.get_node(int(r.end_node.get('id')))
            way_properties = sql_manager.get_way(r['way_id'])
            way = dict()
            way['way'] = way_properties
            way['start_node'] = start_node
            way['end_node'] = end_node
            if way_properties.get('name') == "" and way_properties.get('alt_name') == "" and way_properties.get('ref') == "":
                way_properties.set('name', "Unknown")
            path.append(way)

        return path

    @staticmethod
    def calculate_path_avoid_street(path, source, destination, way_name):

        graph_manager = GraphManager.get_instance()
        sql_manager = MapSqlManager.get_instance()

        sql_manager.open_connection()
        ways = sql_manager.get_instance().get_way_by_name(way_name)
        sql_manager.get_instance().close_connection()

        graph_manager.open_connection()
        # update length with big value to avoid the way in the path calculation
        for way in ways:
            graph_manager.update_way_length(way.get('id'), 1000)
        graph_manager.close_connection()

        res = MapEngine.calculate_path(source, destination)

        graph_manager.open_connection()
        # restore updated length
        for way in ways:
            graph_manager.update_way_length(way.get('id'), way.get('length'))
        graph_manager.close_connection()

        if path == res:
            return None
        return res

# --------------------------------


if __name__ == "__main__":

    source = Point('42.3333569', '12.2692692')
    destination = Point('42.3295099', '12.2659779')

    path = MapEngine.calculate_path(source, destination)
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")

    if path:
        visualize_path(path)

    path = MapEngine.calculate_path_avoid_street(path, source, destination, "Via Santa Maria")
    if path:
        print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")

    if path:
       visualize_path(path)
