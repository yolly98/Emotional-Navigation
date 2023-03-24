from Utility.utility import Point


class GPS:
    @staticmethod
    def get_coord(sim=False):
        if not sim:
            # TODO
            pass
        else:
            return Point('42.3333569', '12.2692692')


if __name__ == '__main__':
    print(GPS.get_coord(True))