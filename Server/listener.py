from flask import Flask, request
from flask_cors import CORS
from Server.Core.emotional_route_selector import EmotionalRouteSelector
from Server.Persistence.mongo_history_manager import MongoHistoryManager
from Server.Persistence.map_manager import MapManager
import json


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
    source = received_json['source_coord']

    path = EmotionalRouteSelector.get_path(username, source, destination_name)
    if path is None:
        return {"status": -1} # path not found

    return {"status": 0, "path": json.dumps(path)}


@app.get('/way')
def get_way():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    point = received_json['coord']
    address = MapManager.get_location_by_point(point)
    if address is None:
        return {"status": -1, "address": None}
    else:
        return {"status": 0, "address": address}


@app.get('/nearest')
def nearest():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    point = received_json['coord']

    point = MapManager.get_nearest_point(point)
    if point:
        reply = {'status': 0, 'point': point}
    else:
        reply = {'status': -1, 'point': None}
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
    way = received_json['way']
    timestamp = received_json['timestamp']
    emotion = received_json['emotion']

    MongoHistoryManager.get_instance().open_connection()
    res = MongoHistoryManager.get_instance().store_sample(username, way, emotion, timestamp)
    MongoHistoryManager.get_instance().close_connection()

    if res:
        return {"status": 0}
    else:
        return {"status": -1}
