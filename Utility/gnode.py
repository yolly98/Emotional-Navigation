
class GNode:

    def __init__(self, id, type, name, lat, lon):
        self.node = dict()
        self.node['id'] = id
        self.node['type'] = type
        self.node['name'] = name
        self.node['lat'] = str(lat)
        self.node['lon'] = str(lon)

    def get(self, key):
        if key in self.node:
            return self.node[key]
        return -1

    def set(self, key, value):
        if key in self.node:
            self.node[key] = value
            return 0
        else:
            return -1

    def __str__(self):
        return self.node.__str__()