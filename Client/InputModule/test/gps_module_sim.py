from Client.communication_manager import CommunicationManager
import time
import json
import matplotlib.pyplot as plt
import math
from Utility.point import Point
from Utility.utility_functions import calculate_distance


def prepare_test_path(gps_data):
    gps_data['gps'].sort(key=lambda x: x['datetime'])

    # remove duplicates
    new_gps_data = dict()
    new_gps_data['gps'] = []
    i = 0
    last_gps = None
    duplicated_records = 0
    for gps in gps_data['gps']:
        if last_gps is not None:
            if gps['datetime'] == last_gps['datetime']:
                # print(f"duplicate record, datetime: {gps['datetime']}")
                i += 1
                duplicated_records += 1
                continue

        new_gps_data['gps'].append(gps)
        last_gps = gps
        i += 1

    print(f"removed {duplicated_records} duplicated records")
    print("-------------------------------------")

    # remove outliers
    gps_data = new_gps_data
    new_gps_data = dict()
    new_gps_data['gps'] = []
    i = 0
    last_gps = None
    outliers = 0
    for gps in gps_data['gps']:
        point = Point(gps['pos']['lat'], gps['pos']['lon'])

        if last_gps is not None:
            last_point = Point(last_gps['pos']['lat'], last_gps['pos']['lon'])
            if gps['datetime'] == last_gps['datetime']:
                print(f"duplicate record, Error!")
                exit(1)

            distance = calculate_distance(last_point, point)
            if distance > 0.5:
                print(f"too long distance: {distance}, last_point: {last_point}, point: {point}")

                j = i + 1
                next_pos = gps_data['gps'][j]
                while next_pos == gps:
                    if j < len(gps_data['gps']) - 1:
                        j += 1
                    else:
                        break
                    next_pos = gps_data['gps'][j]

                if not next_pos == gps:
                    next_point = Point(next_pos['pos']['lat'], next_pos['pos']['lon'])
                    next_distance = calculate_distance(point, next_point)
                    print(next_distance)
                    if next_distance > 0.5:
                        print(f"detected outlier: {gps}")
                        outliers += 1
                        i += 1
                        continue

        new_gps_data['gps'].append(gps)
        last_gps = gps
        i += 1

    print(f"removed {outliers} outliers")
    print("-------------------------------------")

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

    gps_data = prepare_test_path(gps_data)
    visualize_test_path(gps_data)
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