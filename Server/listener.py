from flask import Flask, request
from Server.Persistence.map_sql_manager import MapSqlManager
from Server.Core.map_engine import MapEngine
from Utility.point import Point
from Utility.utility_functions import path_to_json, calculate_distance
from Server.Persistence.history_manager import HistoryManager


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


@app.get('/path')
def get_path():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json

    destination_name = received_json['destination_name']
    source = Point(received_json['source_coord']['lat'], received_json['source_coord']['lon'])
    sql_map = MapSqlManager.get_instance()
    sql_map.open_connection()

    # find destination coordinates
    ways = sql_map.get_way_by_name(destination_name)
    if not ways:
        return {"status": -1} # invalid destination

    # get the way with the start node nearest the source node
    distance = None
    destination = None
    for way in ways:
        node = sql_map.get_node(way.get('start_node'))
        node = Point(node.get('lat'), node.get('lon'))
        d = calculate_distance(source, node)
        if distance is None or d < distance:
            distance = d
            destination = node

    sql_map.close_connection()

    path = MapEngine.calculate_path(source, destination)
    if path is None:
        return {"status": -2} # path not found

    return {"status": 0, "path": path_to_json(path)}


@app.get('/user')
def get_user():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    username = received_json['username']
    HistoryManager.get_instance().open_connection()
    image = HistoryManager.get_instance().get_user_image(username)
    HistoryManager.get_instance().close_connection()
    if image is None:
        return {"status": -1, "image": None}
    else:
        return {"status": 0, "image": image}


@app.post('/user')
def post_user():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    username = received_json['username']
    image = received_json['image']
    HistoryManager.get_instance().open_connection()
    res = HistoryManager.get_instance().create_user(username, image)
    HistoryManager.get_instance().close_connection()

    if res:
        return {"status": 0}
    else:
        return {"status": -1}


@app.post('/history')
def post_history():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json

    return {"status": 0}