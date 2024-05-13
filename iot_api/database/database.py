from config.database_config import database_login_object
from pymongo import MongoClient


MONGODB_CONN = ("mongodb://{}:{}@{}:{}/?authSource={}").format(
    database_login_object.user,
    database_login_object.password,
    database_login_object.host,
    database_login_object.port,
    database_login_object.authentication_database,
)


def create_connection(mongodb_conn):
    try:
        client = MongoClient(mongodb_conn)
        db = client.get_database(database_login_object.authentication_database)
        return client, db
    except Exception as e:
        print("Error connecting to MongoDB:", e)


def get_db():
    client, db = create_connection(MONGODB_CONN)
    if client is None:
        exit()
    else:
        try:
            yield db
        finally:
            client.close()
