from pymongo import MongoClient


if __name__ == "__main__":
    mongo_client = MongoClient('mongodb://admin:password@localhost:27017/')
    mongo_client.drop_database('smart_navigation')
    mongodb = mongo_client['smart_navigation']
    collection = mongodb['user']
    collection = mongodb['history']

    mongodb.user.create_index("username", unique=True)
    mongodb.history.create_index([("username", 1), ("way", 1), ("timestamp", 1)])

