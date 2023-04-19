# https://github.com/IsraelHikingMap/graphhopper-docker-image-push
# docker run --name graphhopper -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf
# inside the container: > ./graphhopper.sh
import requests
import matplotlib.pyplot as plt
import math
import json
import geocoder
import polyline

# Imposta la posizione di partenza e di arrivo
start_point = '42.42946750460835, 12.097280142026138'
end_point = '42.43763731982727, 12.103273686426927'

# Imposta la lista di ID degli archi da evitare
avoid_edges = []


def get_nearest_point(point):

    url = "http://localhost:8989/nearest"

    params = {
        "point": point,
        "vehicle": "car",
        "details": "street_name, max_speed"
    }

    response = requests.get(url, params=params)

    # Verifica che la richiesta sia andata a buon fine
    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    json_data = response.json()
    print(json_data)

def get_way_by_coord(point):
    print(geocoder.osm(point, method='reverse').address)

def plot_path(path):
    points = polyline.decode(path['points'])
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

def get_path(start_point, end_point):

    url = "http://localhost:8989/route"

    params = {
        "point": [start_point, end_point],
        "profile": "car",
        "instructions": "true",
        "points_encoded": "true",
        "locale": "it-IT",
        "details": 'max_speed'
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print('Errore nella richiesta di routing:', response.text)
        exit()

    json_data = json.loads(response.text)
    print(json.dumps(json_data, indent=4))
    paths = sorted(json_data['paths'], key=lambda x: x['distance'])

    print("--------------------------")

    # refactor path
    path = dict()
    all_distance = paths[0]['distance']
    all_time = paths[0]['time']
    instructions = paths[0]['instructions']
    points = paths[0]['points']
    max_speed = paths[0]['details']['max_speed']
    path['distance'] = all_distance
    path['time'] = all_time
    path['points'] = points
    path['ways'] = instructions
    path['max_speed'] = max_speed

    print(json.dumps(path, indent=4))
    return path


if __name__ == '__main__':
    path = get_path(start_point, end_point)
    plot_path(path)
    get_way_by_coord('42.331194, 12.265865')
    get_nearest_point(start_point)