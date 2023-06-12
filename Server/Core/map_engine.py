from Server.Persistence.map_manager import MapManager
import json


class MapEngine:

    @staticmethod
    def calculate_path(source_point, destination, avoid_ways):

        destination_point = MapManager.get_point_by_location(destination)
        if destination_point is None:
            print(f'destination point for {destination} not found') # [Test]
            return None
        paths = MapManager.get_paths(source_point, destination_point, avoid_ways)
        return paths

    @staticmethod
    def plot_path(path):
        MapManager.plot_path(path)

    @staticmethod
    def get_nearest_point(point):
        return MapManager.get_nearest_point(point)


if __name__ == "__main__":

    start_point = [42.415832, 12.106822]
    destination = 'Monumento ai caduti, Viterbo'

    paths = MapEngine.calculate_path(start_point, destination, [])
    for i in range(0, len(paths)):
        print("---------------------------------------------------")
        print(json.dumps(paths[i], indent=4))
        MapManager.plot_path(paths[i])

    paths = MapEngine.calculate_path(start_point, destination, ["Via Giuseppe Mazzini", ])
    for i in range(0, len(paths)):
        print("---------------------------------------------------")
        print(json.dumps(paths[i], indent=4))
        MapManager.plot_path(paths[i])