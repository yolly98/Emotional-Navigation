from Utility.point import Point
from flask import Flask, request, send_file
from flask_cors import CORS
import json
import geocoder
from threading import Lock

GPS_IP = "0.0.0.0"
GPS_PORT = '4000'


class GPSCollector:

    gps_collector = None

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.file_lock = Lock()

    @staticmethod
    def get_instance():
        if GPSCollector.gps_collector is None:
            GPSCollector.gps_collector = GPSCollector()
        return GPSCollector.gps_collector

    def get_app(self):
        return self.app

    def listener(self):
        self.app.run(host=GPS_IP, port=GPS_PORT, debug=False, threaded=True)


app = GPSCollector.get_instance().get_app()


@app.get('/gps')
def get_gps():
    return send_file('send_GPS.html')

@app.post('/gps-collector')
def post_gps_collector():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    lat = received_json['lat']
    lon = received_json['lon']
    time_pos = received_json['datetime']

    gps_data = None

    with GPSCollector.get_instance().file_lock:
        try:
            with open('gps-test.json', 'r') as f:
                gps_data = json.load(f)
                f.close()
        except Exception:
            print("gps-test.json not exists")
            pass

        if gps_data is None:
            gps_data = dict()
            gps_data['gps'] = []

        g = geocoder.osm([lat, lon], method='reverse')
        coords = Point(lat, lon).to_json()
        address = g.address
        new_pos = {'pos': coords, 'address': address, 'datetime': time_pos}
        print(new_pos)
        gps_data['gps'].append(new_pos)

        with open('gps-test.json', 'w') as f:
            json.dump(gps_data, f, indent=4)
            f.close()

    return {"status": 0}


if __name__ == '__main__':
    GPSCollector.get_instance().listener()