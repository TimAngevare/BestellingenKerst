from pymongo import MongoClient
import certifi
import os


def get_db(db_name):
    # connection_string = 'mongodb+srv://kerstAdmin:kerstAdmin123@kerst1.1cyvc.mongodb.net/kerst_db?retryWrites=true&w=majority'
    connection_string = os.environ['MONGODB_CONNECTION']
    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    return client[db_name]
