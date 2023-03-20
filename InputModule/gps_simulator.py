import geocoder
from Utility.utility import Point

class GPS:
    @staticmethod
    def get_coord(sim=False):
        if not sim:
            g = geocoder.ip('me')
            return Point(g.latlng[0], g.latlng[1])
        else:
            return Point('42.3333569', '12.2692692')


    @staticmethod
    def get_address():
        return geocoder.ip('me').address


if __name__ == '__main__':
    print(GPS.get_coord())
    print(GPS.get_address())