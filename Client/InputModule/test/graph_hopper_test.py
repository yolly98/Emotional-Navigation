# https://github.com/IsraelHikingMap/graphhopper-docker-image-push
# docker run --name graphhopper -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf --host 0.0.0.0
import requests
import matplotlib.pyplot as plt
import math
import json
from Utility.point import Point
from Utility.gnode import GNode
from Utility.way import Way
from Utility.utility_functions import calculate_distance
from Server.Persistence.mongo_map_manager import MongoMapManager

# Imposta la posizione di partenza e di arrivo
start_point = '42.33399231261333, 12.269070539901804'
end_point = '42.332018371668575, 12.264471452495334'

# Imposta la lista di ID degli archi da evitare
avoid_edges = []


def get_nearest_point(point):

    url = "http://localhost:8989/nearest"

    params = {
        "point": point,
        "vehicle": "car"
    }

    response = requests.get(url, params=params)

    # Verifica che la richiesta sia andata a buon fine
    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    json_data = response.json()
    print(json_data)


def get_path(start_point, end_point):

    url = "http://localhost:8989/route"

    params = {
        "point": [start_point, end_point],
        "profile": "car",
        "instructions": "true",
        "points_encoded": "false",
        "locale": "it-IT"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    json_data = json.loads(response.text)
    print(json_data)
    print("--------------------------")
    print(json_data['paths'])
    print("--------------------------")
    print(json_data['paths'][0]['instructions'])
    print("--------------------------")

    with open("path-example.json", "w") as f:
        json.dump(json_data, f, indent=4)
        f.close()

    # print path
    points = json_data['paths'][0]['points']['coordinates']
    fig, ax = plt.subplots()
    lats = []
    lons = []
    i = 0
    progress = 0
    last_point = None
    for point in points:
        if not progress == math.floor((i * 100) / (len(points))):
            progress = math.floor((i * 100) / (len(points)))
            print(f"calculation {progress}%", end="\r")

        if last_point is not None:
            ax.plot([point[0], last_point[0]], [point[1], last_point[1]], c='violet', alpha=1, linewidth=1)

        lats.append(float(point[1]))
        lons.append(float(point[0]))
        last_point = point
        i += 1

    ax.scatter(lons, lats, c='white', alpha=1, s=3)
    fig.set_facecolor('black')
    ax.set_title("Path")
    ax.axis('off')
    plt.show()

    '''
    # convert graphhopper path to my path
    path = []
    last_point = None
    start_node = None
    MongoMapManager.get_instance().open_connection()
    for point in points:
        if last_point is None:
            last_point = point
            start_node = MongoMapManager.get_instance().get_node_by_coord(point[1], point[0])
            continue

        way = dict()

        end_node = MongoMapManager.get_instance().get_node_by_coord(point[1], point[0])
        way_properties = MongoMapManager.get_instance().get_way_by_nodes(start_node.get('id'), end_node.get('id'))
        way['way'] = way_properties
        way['start_node'] = start_node
        way['end_node'] = end_node
        path.append(way)
        start_node = end_node
    

    MongoMapManager.get_instance().close_connection()

    print(path)
    '''

if __name__=='__main__':
    get_path(start_point, end_point)
    get_nearest_point(start_point)