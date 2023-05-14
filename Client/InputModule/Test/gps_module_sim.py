from Client.communication_manager import CommunicationManager
from Client.InputModule.gps_manager import GPS
import time
import json
import matplotlib.pyplot as plt
import math
import os


class GPSsim:
    @staticmethod
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
            point = [float(gps['pos'][0]), float(gps['pos'][1])]

            if last_gps is not None:
                last_point = [float(last_gps['pos'][0]), float(last_gps['pos'][1])]
                if gps['datetime'] == last_gps['datetime']:
                    print(f"duplicate record, Error!")
                    exit(1)

                distance = GPS.calculate_distance(last_point, point)
                if distance > 200:
                    print(f"detected possible outlier {gps}")
                    print(f"too long distance: {distance}, last_point: {last_point}, point: {point}")

            new_gps_data['gps'].append(gps)
            last_gps = gps
            i += 1

        print(f"removed {outliers} outliers")
        print("-------------------------------------")

        return new_gps_data

    @staticmethod
    def visualize_test_path(gps_data):

        fig, ax = plt.subplots()
        lats = []
        lons = []
        i = 0
        progress = 0
        last_gps = None
        for gps in gps_data['gps']:
            point = [float(gps['pos'][0]), float(gps['pos'][1])]
            if not progress == math.floor((i * 100) / (len(gps_data['gps']))):
                progress = math.floor((i * 100) / (len(gps_data['gps'])))
                print(f"calculation {progress}%")

            if last_gps is not None:
                last_point = [float(last_gps['pos'][0]), float(last_gps['pos'][1])]
                line_lat = [last_point[0], point[0]]
                line_lon = [last_point[1], point[1]]
                ax.plot(line_lon, line_lat, c='violet', alpha=1, linewidth=1)

            lats.append(point[0])
            lons.append(point[1])
            last_gps = gps
            i += 1

        ax.scatter(lons, lats, c='white', alpha=1, s=3)
        fig.set_facecolor('black')
        ax.set_title("Path")
        ax.axis('off')
        plt.show()

    @staticmethod
    def run(is_thread=True):
        route_path = os.path.dirname(__file__)

        with open(os.path.join(route_path, 'gps-test.json'), 'r') as f:
            gps_data = json.load(f)

        gps_data = GPSsim.prepare_test_path(gps_data)
        if not is_thread:
            GPSsim.visualize_test_path(gps_data)

        i = 0
        while i < len(gps_data['gps']):
            # print(gps_data['gps'][i]) [Test]
            request = dict()
            request['pos'] = gps_data['gps'][i]['pos']
            request['datetime'] = gps_data['gps'][i]['datetime']
            CommunicationManager.send(
                ip='127.0.0.1',
                port='6000',
                type='POST',
                data=request,
                resource='gps-collector'
            )
            i += 1
            time.sleep(1)


if __name__ == '__main__':
    GPSsim.run(is_thread=False)