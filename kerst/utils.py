from pymongo import MongoClient
import certifi
import os


def get_db(db_name):
    connection_string = os.environ['MONGODB_CONNECTION']
    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    return client[db_name]
