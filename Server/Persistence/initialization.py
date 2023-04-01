# take the data exported from openstreetmap in osm format and upload it to neo4j

# openstreetmap link --> https://www.openstreetmap.org/export#map=14/42.3283/12.2792

import xmltodict
import json
import math
from Utility.utility_functions import calculate_distance
from Utility.point import Point
from py2neo import Graph, Node, Relationship
import mysql.connector

START_WAY_ID = 0
# ---------------------------------------------------------------------------
#  SCRIPT TO BE PERFORMED ONLY ONCE TO LOAD THE DATABASE THROUGH AN osm FILE

# docker command
'''
docker run --name neo4j_smart_navigation \
-p 7474:7474 -p 7687:7687 -d \
-v /mnt/c/Users/gianl/neo4j/data:/data \
-v /mnt/c/Users/gianl/neo4j/logs:/logs \
-v /mnt/c/Users/gianl/neo4j/import:/import \
-v /mnt/c/Users/gianl/neo4j/plugins:/plugins \
--env NEO4J_AUTH=neo4j/password neo4j  
'''

# configure timeout query in neo4j
'''
> docker exec -it neo4j_smart_navigation bash
> cd /var/lib/neo4j/conf
> vim neo4j.conf
add line 'dbms.transaction.timeout=10s'
'''

# install apoc plugin for neo4j
'''
download apoc from https://github.com/neo4j/apoc/releases
put apoc-(last-version)-all.jar in plugins folder
of the neo4j main folder
(then restart)
'''

# docker command for msyql
'''
docker run --name mysql-smart-navigation \
-p 3306:3306 -d \
-v mysql_volume:/var/lib/mysql/ \
-e "MYSQL_ROOT_PASSWORD=password" mysql
'''
# -------------------


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

    # --------------- mysql db initialization -------------------

    mysql_conn = None
    try:
        mysql_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password"
        )
    except mysql.connector.Error as e:
        print(f"Mysql connection error [{e}]")
        return
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute("DROP DATABASE IF EXISTS smart_navigation")
    mysql_cursor.execute("CREATE DATABASE IF NOT EXISTS smart_navigation")
    mysql_cursor.execute("USE smart_navigation")

    # table creations
    mysql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS user ( \
        id BIGINT AUTO_INCREMENT, \
        username VARCHAR(100), \
        UNIQUE(username), \
        PRIMARY KEY (id)\
        ) "
    )

    mysql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS way ( \
        id BIGINT, \
        name VARCHAR(100), \
        alt_name VARCHAR(100), \
        ref VARCHAR(100), \
        lim_speed INT, \
        length INT , \
        start_node BIGINT, \
        end_node BIGINT, \
        PRIMARY KEY (id) \
        ) "
    )

    mysql_cursor.execute("CREATE INDEX way_name on way(name)")

    mysql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS node ( \
        id BIGINT, \
        type VARCHAR(100), \
        name VARCHAR(100), \
        lat DOUBLE, \
        lon DOUBLE, \
        PRIMARY KEY (id) \
        ) "
    )

    mysql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS history ( \
        user_id BIGINT, \
        way_id BIGINT, \
        emotion VARCHAR(100), \
        timestamp BIGINT, \
        PRIMARY KEY (user_id, way_id, timestamp) \
        ) "
    )
    mysql_conn.commit()
    mysql_cursor = mysql_conn.cursor(prepared=True)

    # -----------------------------------------------------------

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

            # save nodes to mysql db
            sql = "INSERT INTO node (id, type, name, lat, lon ) \
                            VALUES( %s, %s, %s, %s, %s)"
            try:
                mysql_cursor.execute(sql, (start_node.get('id'), start_node.get('type'), start_node.get('name'), start_node.get('lat'), start_node.get('lon')))
            except mysql.connector.Error as e:
                pass
            sql = "INSERT INTO node (id, type, name, lat, lon ) \
                                        VALUES( %s, %s, %s, %s, %s)"
            try:
                mysql_cursor.execute(sql, (end_node.get('id'), end_node.get('type'), end_node.get('name'), end_node.get('lat'), end_node.get('lon')))
            except mysql.connector.Error as e:
                pass

            # create a relationship between nodes
            p1 = Point(start_node.get('lat'), start_node.get('lon'))
            p2 = Point(end_node.get('lat'), end_node.get('lon'))
            length = math.floor(calculate_distance(p1, p2) * 1000)  # in meters
            # crate the way and nodes in neo4j
            relationship = Relationship(reduced_start_node, "TO", reduced_end_node, way_id=way_id, length=length)
            graph.create(relationship)

            # create the way for mysql
            sql = "INSERT INTO way ( \
                   id, name, alt_name, ref, lim_speed, length, start_node, end_node) \
                   VALUES( %s, %s, %s, %s, %s, %s, %s, %s)"
            mysql_cursor.execute(sql, (way_id, name, alt_name, ref, lim_speed, length, start_node.get('id'), end_node.get('id')))
            mysql_conn.commit()

            # update the starting node
            start_node = end_node
            reduced_start_node = reduced_end_node
            way_id += 1

    print("loading map data completed")

    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(
        "CREATE TABLE ordered_points_table AS \
        SELECT node.id as id, node.type as type, node.name as name, node.lat as lat, node.lon as lon \
        FROM node \
        INNER JOIN way \
        ON node.id = way.start_node \
        ORDER BY node.lat, node.lon;"
    )

    mysql_cursor.execute("CREATE INDEX lat_index on ordered_points_table(lat)")
    mysql_cursor.execute("CREATE INDEX lon_index on ordered_points_table(lon)")
    mysql_conn.commit()

    mysql_conn.close()


if __name__ == "__main__":
    load_map()

