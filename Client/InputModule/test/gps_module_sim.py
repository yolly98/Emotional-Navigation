from Client.communication_manager import CommunicationManager
import time
import json


if __name__ == '__main__':
    with open('gps-test.json', 'r') as f:
        gps_data = json.load(f)

    i = 0
    while i < len(gps_data['gps']):
        print(gps_data['gps'][i])
        request = gps_data['gps'][i]['pos']
        CommunicationManager.send(
            ip='127.0.0.1',
            port='4000',
            type='POST',
            data=request,
            resource='gps'
        )
        i += 1
        time.sleep(1)