
class Way:

    def __init__(self, id, name, alt_name, ref, speed, length, start_node, end_node):
        self.way = dict()
        self.way['id'] = id
        self.way['name'] = name
        self.way['alt_name'] = alt_name
        self.way['ref'] = ref
        self.way['speed'] = speed
        self.way['length'] = length
        self.way['start_node'] = start_node
        self.way['end_node'] = end_node

    def get(self, key):
        if key in self.way:
            return self.way[key]
        else:
            return -1

    def set(self, key, value):
        if key in self.way:
            self.way[key] = value
            return 0
        else:
            return -1

    def __str__(self):
        return self.way.__str__()
