'''
https://github.com/IsraelHikingMap/graphhopper-docker-image-push
docker run --name graphhopper -d -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf --host 0.0.0.0
https://github.com/mediagis/nominatim-docker
docker run -d \
  -e PBF_URL=https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf \
  -p 8080:8080 \
  --name nominatim \
  mediagis/nominatim:4.2
'''

import requests
import matplotlib.pyplot as plt
import math
import json
import polyline


class MapManager:

    @staticmethod
    def get_nearest_point(point):

        point = f'{point[0]},{point[1]}'

        url = "http://localhost:8989/nearest"

        params = {
            "point": point,
            "vehicle": "car"
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print('Graphhopper error in nearest resource:', response.text)
            return None

        json_data = response.json()
        point = json_data['coordinates']
        return [float(point[1]), float(point[0])]

    @staticmethod
    def get_point_by_location(location_name):

        url = "http://localhost:8080/search"
        params = {
            "q": location_name,
            "format": "jsonv2",
            "limit": 1
        }

        try:
            response = requests.get(url, params=params, timeout=5)
        except requests.exceptions.Timeout:
            print("expired timeout for location request")
            return None

        if response.status_code != 200:
            print('Nominatim error:', response.text)
            return None

        if len(response.json()) == 0:
            return None

        location = response.json()[0]
        return [float(location["lat"]), float(location["lon"])]

    @staticmethod
    def get_location_by_point(point):
        url = "http://localhost:8080/reverse"
        params = {
            "lat": point[0],
            "lon": point[1],
            "format": "json"
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print('Nominatim error:', response.text)
            return None

        location = response.json()
        if 'display_name' in location:
            address = location['address']
            return address
        else:
            return None


    @staticmethod
    def plot_path(path):

        points = polyline.decode(path['points'])
        # [Test]
        print(points)
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

    @staticmethod
    def get_path(start_point, end_point, avid_ways):

        start_point = f'{start_point[0]},{start_point[1]}'
        end_point = f'{end_point[0]},{end_point[1]}'
        url = "http://localhost:8989/route"

        params = {
            "point": [start_point, end_point],
            "profile": "car",
            "instructions": "true",
            "points_encoded": "true",
            "locale": "it-IT",
            "details": "max_speed",
            "algorithm": "alternative_route",
            "alternative_route.max_paths": 3,
            "alternative_route.max_weight_factor": 1.5

        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print('Errore nella richiesta di routing:', response.text)
            return None

        json_data = json.loads(response.text)
        ordered_paths = sorted(json_data['paths'], key=lambda x: x['distance'])

        # refactor path
        paths = []
        for i in range(0, len(ordered_paths)):
            path = dict()
            all_distance = ordered_paths[i]['distance']
            all_time = ordered_paths[i]['time']
            instructions = ordered_paths[i]['instructions']
            points = ordered_paths[i]['points']
            max_speed = ordered_paths[i]['details']['max_speed']
            path['distance'] = all_distance
            path['time'] = all_time
            path['points'] = points
            path['ways'] = instructions
            path['max_speed'] = max_speed
            avoided = False
            for segment in instructions:
                if segment['street_name'] in avid_ways:
                    avoided = True
                    break
            if avoided:
                continue
            paths.append(path)

        return paths


if __name__ == '__main__':

    start_point = [42.415832, 12.106822]
    end_point = [42.41942, 12.10429]

    print(MapManager.get_location_by_point(start_point))
    print(MapManager.get_location_by_point(end_point))

    paths = MapManager.get_path(start_point, end_point, [])
    for i in range(0, len(paths)):
        print("---------------------------------------------------")
        print(json.dumps(paths[i], indent=4))
        MapManager.plot_path(paths[i])

    paths = MapManager.get_path(start_point, end_point, ["Via Cavour",])
    for i in range(0, len(paths)):
        print("---------------------------------------------------")
        print(json.dumps(paths[i], indent=4))
        MapManager.plot_path(paths[i])

    point = MapManager.get_point_by_location('Via XXVIII Ottobre')
    point = MapManager.get_nearest_point(point)
    paths = MapManager.get_path(start_point, point, [])
    for i in range(0, len(paths)):
        print("---------------------------------------------------")
        print(json.dumps(paths[i], indent=4))
        MapManager.plot_path(paths[i])