from pymongo import MongoClient
import certifi


def get_db(db_name):
    connection_string = 'mongodb+srv://kerstAdmin:kerstAdmin123@kerst1.1cyvc.mongodb.net/kerst_db?retryWrites=true&w=majority'
    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    return client[db_name]
