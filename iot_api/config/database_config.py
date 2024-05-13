from classes.dist_to_object import DictToObject

database_login = {
    "host": "127.0.0.1",
    "port": "27017",
    "authentication_database": "iot_app",
    "user": "iot_app_user",
    "password": "iot_app_password",
}

database_login_object = DictToObject(**database_login)