from Client.communication_manager import CommunicationManager
import time
import json
import matplotlib.pyplot as plt
import math
from Utility.point import Point
from Utility.utility_functions import calculate_distance


def sanitize_test_path(gps_data):

    new_gps_data = dict()
    new_gps_data['gps'] = []
    i = 0
    progress = 0
    last_gps = None
    for gps in gps_data['gps']:
        point = Point(gps['pos']['lat'], gps['pos']['lon'])
        if not progress == math.floor((i * 100) / (len(gps_data['gps']))):
            progress = math.floor((i * 100) / (len(gps_data['gps'])))
            print(f"calculation {progress}%")

        if last_gps is not None:
            last_point = Point(last_gps['pos']['lat'], last_gps['pos']['lon'])
            if gps['datetime'] == last_gps['datetime']:
                print(f"duplicate record, datetime: {gps['datetime']}")
                continue
            distance = calculate_distance(last_point, point)
            if distance > 0.5:
                print(f"too long distance: {distance}, last_point: {last_point}, point: {point}")

        new_gps_data['gps'].append(gps)
        last_gps = gps
        i += 1

    return new_gps_data


def visualize_test_path(gps_data):

    fig, ax = plt.subplots()
    lats = []
    lons = []
    i = 0
    progress = 0
    last_gps = None
    for gps in gps_data['gps']:
        point = Point(gps['pos']['lat'], gps['pos']['lon'])
        if not progress == math.floor((i * 100) / (len(gps_data['gps']))):
            progress = math.floor((i * 100) / (len(gps_data['gps'])))
            print(f"calculation {progress}%")

        if last_gps is not None:
            last_point = Point(last_gps['pos']['lat'], last_gps['pos']['lon'])

            if gps['datetime'] == last_gps['datetime']:
                print(f"duplicate record, datetime: {gps['datetime']}")
            distance = calculate_distance(last_point, point)
            if distance > 0.5:
                print(f"too long distance: {distance}, last_point: {last_point}, point: {point}")
            line_lat = [last_point.get_lat(), point.get_lat()]
            line_lon = [last_point.get_lon(), point.get_lon()]
            ax.plot(line_lon, line_lat, c='violet', alpha=1, linewidth=1)

        lats.append(point.get_lat())
        lons.append(point.get_lon())
        last_gps = gps
        i += 1

    ax.scatter(lons, lats, c='white', alpha=1, s=3)
    fig.set_facecolor('black')
    ax.set_title("Path")
    ax.axis('off')
    plt.show()


if __name__ == '__main__':
    with open('gps-test.json', 'r') as f:
        gps_data = json.load(f)

    # visualize_test_path(sanitize_test_path(gps_data))
    # exit(0)

    i = 0
    while i < len(gps_data['gps']):
        print(gps_data['gps'][i])
        request = dict()
        request['lat'] = gps_data['gps'][i]['pos']['lat']
        request['lon'] = gps_data['gps'][i]['pos']['lon']
        request['datetime'] = gps_data['gps'][i]['datetime']
        CommunicationManager.send(
            ip='127.0.0.1',
            port='4000',
            type='POST',
            data=request,
            resource='gps'
        )
        i += 1
        time.sleep(1)