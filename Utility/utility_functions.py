import math


def calculate_distance(Point1, Point2): # in m

    lat1 = float(Point1[0])
    lon1 = float(Point1[1])
    lat2 = float(Point2[0])
    lon2 = float(Point2[1])

    R = 6371000  # Earth radius in m
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return distance
