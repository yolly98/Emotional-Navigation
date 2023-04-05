from flask import Flask, request
from flask_cors import CORS
from Server.Core.emotional_route_selector import EmotionalRouteSelector
from Server.Persistence.mongo_map_manager import MongoMapManager
from Utility.point import Point
from Utility.utility_functions import path_to_json, calculate_distance
from Server.Persistence.mongo_history_manager import MongoHistoryManager


class Listener:

    listener = None

    def __init__(self):
        # Flask instance to receive data
        self.app = Flask(__name__)
        CORS(self.app)

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

    username = received_json['username']
    destination_name = received_json['destination_name']
    source = Point(received_json['source_coord']['lat'], received_json['source_coord']['lon'])
    map = MongoMapManager.get_instance()
    map.open_connection()

    # find destination coordinates
    ways = map.get_way_by_name(destination_name)
    if not ways:
        return {"status": -1} # invalid destination

    # get the way with the start node nearest the source node
    distance = None
    destination = None
    for way in ways:
        node = map.get_node(way.get('start_node'))
        node = Point(node.get('lat'), node.get('lon'))
        d = calculate_distance(source, node)
        if distance is None or d < distance:
            distance = d
            destination = node

    map.close_connection()

    path = EmotionalRouteSelector.get_path(username, source, destination)
    if path is None:
        return {"status": -2} # path not found

    return {"status": 0, "path": path_to_json(path)}


@app.get('/way')
def get_way():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    lat = received_json['lat']
    lon = received_json['lon']

    MongoMapManager.get_instance().open_connection()
    nearest_node = MongoMapManager.get_instance().get_nearest_node(lat, lon)
    if not nearest_node:
        MongoMapManager.get_instance().close_connection()
        return {'status': -1}
    way = MongoMapManager.get_instance().get_way_by_start_node(nearest_node.get('id'))[0]
    if not way:
        MongoMapManager.get_instance().close_connection()
        return {'status': -1}
    end_node = MongoMapManager.get_instance().get_node(way.get('end_node'))
    if not way:
        MongoMapManager.get_instance().close_connection()
        return {'status': -1}

    MongoMapManager.get_instance().close_connection()
    reply = dict()
    reply['status'] = 0
    reply['way'] = way.to_json()
    reply['start_node'] = nearest_node.to_json()
    reply['end_node'] = end_node.to_json()
    return reply

@app.get('/user')
def get_user():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    username = received_json['username']
    MongoHistoryManager.get_instance().open_connection()
    image = MongoHistoryManager.get_instance().get_user_image(username)
    MongoHistoryManager.get_instance().close_connection()
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
    MongoHistoryManager.get_instance().open_connection()
    res = MongoHistoryManager.get_instance().create_user(username, image)
    MongoHistoryManager.get_instance().close_connection()

    if res:
        return {"status": 0}
    else:
        return {"status": -1}


@app.post('/history')
def post_history():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    username = received_json['username']
    way_id = received_json['way_id']
    timestamp = received_json['timestamp']
    emotion = received_json['emotion']

    MongoHistoryManager.get_instance().open_connection()
    res = MongoHistoryManager.get_instance().store_sample(username, way_id, emotion, timestamp)
    MongoHistoryManager.get_instance().close_connection()

    if res:
        return {"status": 0}
    else:
        return {"status": -1}
