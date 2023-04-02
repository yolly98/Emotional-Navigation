# take the data exported from openstreetmap in osm format and upload it to neo4j

# openstreetmap link --> https://www.openstreetmap.org/export#map=14/42.3283/12.2792

import xmltodict
import json
import math
from Utility.utility_functions import calculate_distance
from Utility.point import Point
from py2neo import Graph, Node, Relationship
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from Utility.gnode import GNode
from Utility.way import Way

START_WAY_ID = 0


def load_map():
    # open osm file in xml format
    with open("Resources/map.osm", "r") as f:
        data = f.read()

    # convert data in json format
    json_data = xmltodict.parse(data)

    with open("Resources/map.json", "w") as json_file:
        json.dump(json_data, json_file)

    print("The map.json file created with success!")

    # -------------- graph db initialization ----------------------
    # create connection to neo4j database
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

    try:
        graph.run("Match (n) Return n Limit 1")
        print('database connected')
    except Exception:
        print('database offline')
        return

    # delete all nodes and relationship in ne4jdb
    graph.run("MATCH (n) DETACH DELETE n")

    # ----------------- mongo db initialization ------------------------------

    mongo_client = MongoClient('mongodb://admin:password@localhost:27017/')
    mongo_client.drop_database('smart_navigation')
    mongodb = mongo_client['smart_navigation']
    collection = mongodb['map_node']
    collection = mongodb['map_way']
    collection = mongodb['user']
    collection = mongodb['history']

    mongodb.map_node.create_index("id", unique=True)
    mongodb.map_node.create_index([("lat", 1), ("lon", 1)])
    mongodb.map_way.create_index("id", unique=True)
    mongodb.map_way.create_index([("name", "text")])
    mongodb.user.create_index("username", unique=True)


    # ----------------------------------------------------------------------

    with open("Resources/map.json", "r") as json_file:
        data = json.load(json_file)

    # dictionary to map the ID of nodes with no4j's nodes
    neo4j_nodes = {}
    neo4j_reduced_nodes = {}

    # ---- laod nodes ---------
    '''
    example of node 1

    {
        '@id': '72964091', 
        '@visible': 'true', 
        '@version': '4', 
        '@changeset': '46761722', 
        '@timestamp': '2017-03-11T12:49:49Z', 
        '@user': 'sbiribizio', 
        '@uid': '354284', 
        '@lat': '42.3351260', 
        '@lon': '12.2997670', 
        'tag': [
            {'@k': 'gfoss_id', '@v': '4802'},
            {'@k': 'name', '@v': 'Fabrica di Roma'}, 
            {'@k': 'place', '@v': 'village'}, 
            {'@k': 'population', '@v': '8340'}, 
            {'@k': 'source', '@v': 'geodati.gfoss.it'}, 	
            {'@k': 'wikidata', '@v': 'Q160967'}, 
            {'@k': 'wikipedia', '@v': 'it:Fabrica di Roma'}
        ]
    }

    example 2 of node

    {
        '@id': '248140358',
        '@visible': 'true',
        '@version': '4', 
        '@changeset': '43666159', 
        '@timestamp': '2016-11-15T10:10:58Z', 
        '@user': 'Dino Michelini', 
        '@uid': '3151555', 
        '@lat': '42.3071169', 
        '@lon': '12.2040968'
    }
    '''
    i = 0
    for node in data["osm"]["node"]:

        i += 1
        if i % 100 == 0:
            print(f"node: {i}")
        id = node["@id"]
        type = ""
        name = "null"
        lat = node["@lat"]
        lon = node["@lon"]
        if 'tag' in node:
            for elem in node['tag']:
                if elem == '@k' or elem == '@v':
                    continue
                if elem['@k'] == 'name':
                    name = elem['@v']

        # create node
        neo4j_node = Node("Node", id=id, lat=lat, lon=lon, name=name, type=type)
        neo4j_reduced_node = Node("Node", id=id)
        # add nodes to dict
        neo4j_nodes[id] = neo4j_node
        neo4j_reduced_nodes[id] = neo4j_reduced_node

    print("nodes loads with success")

    # ---- load ways --------------
    '''
    example 1 of a way
    {
        '@id': '23029665',
        '@visible': 'true',
        '@version': '11', 
        '@changeset': '124385216', 
        '@timestamp': '2022-08-02T10:40:34Z', 
        '@user': 'Dino Michelini', 
        '@uid': '3151555', 
        'nd': [
            {'@ref': '248140388'}, 
            {'@ref': '248459449'}, 
            {'@ref': '248459450'}, 
            ...
            {'@ref': '248459483'},
            {'@ref': '7615879711'}
        ],
        'tag': [
            {'@k': 'highway', '@v': 'tertiary'}, 
            {'@k': 'lanes', '@v': '2'}, 
            {'@k': 'lanes:backward', '@v': '1'}, 
            {'@k': 'lanes:forward', '@v': '1'}, 
            {'@k': 'name', '@v': 'Strada Comunale Caproceca'}, 
            {'@k': 'surface', '@v': 'asphalt'}
        ]
    }

    example 2 of a way

    {
        '@id': '27758601', 
        '@visible': 'true', 
        '@version': '9', 
        '@changeset': '114752913', 
        '@timestamp': '2021-12-09T17:17:52Z', 
        '@user': 'Dino Michelini', 
        '@uid': '3151555', 
        'nd': [
            {'@ref': '304812181'},
            {'@ref': '304812183'},
            ...
             {'@ref': '304812202'}
        ],
        'tag': [
            {'@k': 'alt_name', '@v': 'Strada Provinciale Ronciglionese'}, 
            {'@k': 'highway', '@v': 'secondary'}, 
            {'@k': 'name', '@v': 'Via Madonna delle Grazie'}, 
            {'@k': 'ref', '@v': 'SP35'}
        ]
    }
    
    example 3 of way
    
    {
        "@id": "475759834", 
        "@visible": "true", 
        "@version": "1", 
        "@changeset": "46233911", 
        "@timestamp": "2017-02-20T06:08:43Z", 
        "@user": "Michele Aquilani", 
        "@uid": "3860151", 
        "nd": [
            {"@ref": "4694735441"}, 
            {"@ref": "4694735442"}, 
            {"@ref": "4694735443"}, 
            {"@ref": "4694735444"}, 
            {"@ref": "4694735445"}, 
            {"@ref": "4694735446"}, 
            {"@ref": "4694735447"}, 
            {"@ref": "4694735448"}, 
            {"@ref": "4694735449"}, 
            {"@ref": "4694735450"}, 
            {"@ref": "4694735441"}
        ], 
        "tag": [
            {"@k": "building", "@v": "yes"}, 
            {"@k": "landuse", "@v": "plant_nursery"}
        ]}


    '''
    i = 0
    way_id = START_WAY_ID
    for way in data["osm"]["way"]:
        # take nodes that build the path
        i += 1
        if i % 100 == 0:
            print(f"way: {i} / {len(data['osm']['way'])}")
        nodes = way["nd"]
        alt_name = ""
        name = ""
        ref = ""
        lim_speed = 0
        if 'tag' in way:
            for elem in way['tag']:
                if elem == '@k' or elem == '@v':
                    continue
                if elem['@k'] == 'alt_name':
                    alt_name = elem['@v']
                elif elem['@k'] == 'name':
                    name = elem['@v']
                elif elem['@k'] == 'ref':
                    ref = elem['@v']
                elif elem['@k'] == 'maxspeed':
                    lim_speed = elem['@v']

        if name == "" and alt_name == "" and ref == "":
            continue

        if lim_speed == 0:
            if not ref.find("A") == -1:
                lim_speed = 130
            elif not ref.find("SS") == -1:
                lim_speed = 110
            elif not ref.find("SR") == -1:
                lim_speed = 90
            elif not ref.find("SP") == -1:
                lim_speed = 70
            elif not ref.find("SC") == -1:
                lim_speed = 50
            else:
                lim_speed = 50

        # take the first node
        start_node = neo4j_nodes[nodes[0]["@ref"]]
        reduced_start_node = neo4j_reduced_nodes[nodes[0]["@ref"]]
        # take next nodes
        for node in nodes[1:]:

            # take the next node
            end_node = neo4j_nodes[node["@ref"]]
            reduced_end_node = neo4j_reduced_nodes[node["@ref"]]

            # save node to mongodb
            start_gnode = GNode(start_node.get('id'), start_node.get('type'), start_node.get('name'), start_node.get('lat'), start_node.get('lon'))
            try:
                mongodb.map_node.insert_one(start_gnode.to_json())
            except DuplicateKeyError as e:
                pass

            # create a relationship between nodes
            p1 = Point(start_node.get('lat'), start_node.get('lon'))
            p2 = Point(end_node.get('lat'), end_node.get('lon'))
            length = math.floor(calculate_distance(p1, p2) * 1000)  # in meters

            # save the way and nodes to neo4j
            relationship = Relationship(reduced_start_node, "TO", reduced_end_node, way_id=way_id, length=length)
            graph.create(relationship)

            # save the way to mongodb
            way = Way(way_id, name, alt_name, ref, lim_speed, length, start_node.get('id'), end_node.get('id'))
            mongodb.map_way.insert_one(way.to_json())

            # update the starting node
            start_node = end_node
            reduced_start_node = reduced_end_node
            way_id += 1

        # store the last node of the way to mongodb
        start_gnode = GNode(start_node.get('id'), start_node.get('type'), start_node.get('name'), start_node.get('lat'), start_node.get('lon'))
        try:
            mongodb.map_node.insert_one(start_gnode.to_json())
        except DuplicateKeyError as e:
            pass

    print("loading map data completed")

    mongo_client.close()



if __name__ == "__main__":
    load_map()

