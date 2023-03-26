
class Point:

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def __str__(self):
        return str(f"({self.lat}, {self.lon})")