from flask import Flask, request
from Server.Persistence.map_sql_manager import MapSqlManager
from Server.Core.map_engine import MapEngine
from Utility.point import Point
from Utility.utility_functions import path_to_json


class Listener:

    listener = None

    def __init__(self):
        # Flask instance to receive data
        self.app = Flask(__name__)

    @staticmethod
    def get_instance():
        if Listener.listener is None:
            Listener.listener = Listener()
        return Listener.listener

    def listen(self, ip, port):
        # execute the listening server, for each message received, it will be handled by a thread
        self.app.run(host=ip, port=port, debug=False, threaded=True)

    def get_app(self):
        return self.app


app = Listener.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json

    if received_json['type'] == "get_path":

        destination_name = received_json['destination_name']
        source = Point(received_json['source_coord']['lat'], received_json['source_coord']['lon'])
        sql_map = MapSqlManager.get_instance()
        sql_map.open_connection()

        # find destination coordinates
        ways = sql_map.get_way_by_name(destination_name)
        if not ways:
            return {"status": -1} # invalid destination

        way = ways[0]
        destination_node = sql_map.get_node(way.get('start_node'))
        destination = Point(destination_node.get('lat'), destination_node.get('lon'))
        sql_map.close_connection()

        path = MapEngine.calculate_path(source, destination)
        if path is None:
            return {"status": -2} # path not found

        return {"status": 0, "path": path_to_json(path)}

    else:
        return {"status": -10}, 200