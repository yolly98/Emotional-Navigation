import serial
from Client.communication_manager import CommunicationManager
from datetime import datetime
import pynmea2
import time


class GPSExternModule:

    gps_extern_module = None

    def __init__(self):
        self.usb_port = None
        self.server_ip = None
        self.server_port = None
        self.target_resource = None
        self.interval = None

    @staticmethod
    def get_instance():
        if GPSExternModule.gps_extern_module is None:
            GPSExternModule.gps_extern_module = GPSExternModule()
        return GPSExternModule.gps_extern_module

    def config(self, usb_port, server_ip, server_port, target_resource, interval):
        self.usb_port = usb_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.target_resource = target_resource
        self.interval = interval

    def run(self, log=False):
        gps_nmea_module = serial.Serial(self.usb_port, 9600, timeout=1)

        # set updating time to 1000ms
        cmd = f'$PMTK220,{self.interval*1000}*1F\r\n'
        gps_nmea_module.write(cmd.encode('utf-8'))
        time.sleep(1)

        while True:
            line = gps_nmea_module.readline().decode('ascii', errors='replace')

            if line.startswith('$GPGGA'):
                data = pynmea2.parse(line)

                lat_dd = data.latitude
                lon_dd = data.longitude
                if log:
                    fix_quality = data.gps_qual
                    num_satellites = data.num_sats
                    hdop = data.horizontal_dil
                    altitude = data.altitude
                    altitude_units = data.altitude_units

                    print("Latitude:", lat_dd)
                    print("Longitude:", lon_dd)
                    print("Fix quality:", fix_quality)
                    print("Number of satellites:", num_satellites)
                    print("HDOP:", hdop)
                    print("Altitude:", altitude, altitude_units)

                    print("------------------------------------------")

                if lat_dd and lon_dd and not lat_dd == 0.0 and not lon_dd == 0.0:
                    now = datetime.now()
                    formatted_datetime = now.strftime('%Y-%m-%d %H:%M:%S')
                    request = {'lat': lat_dd, 'lon': lon_dd, 'datetime': formatted_datetime}
                    print(request)
                    CommunicationManager.send(self.server_ip, self.server_port, 'POST', request, self.target_resource)


if __name__ == '__main__':
    GPSExternModule.get_instance().config(
        usb_port='COM12',
        server_ip='127.0.0.1',
        server_port='4000',
        target_resource='gps-collector',
        interval=1

    )
    GPSExternModule.get_instance().run(log=True)