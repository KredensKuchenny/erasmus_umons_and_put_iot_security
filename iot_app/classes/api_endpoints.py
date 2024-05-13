import requests
from config.api import api_config


def post_account_login(username: str, password: str):
    url = f"{api_config['url']}/account/login"

    payload = {"username": username, "password": password}
    response = requests.post(url, headers=api_config["login_headers"], data=payload)

    return {"status_code": response.status_code, "json_data": response.json()}


def post_account_register(username: str, password: str):
    url = f"{api_config['url']}/account/register"

    payload = {"username": username, "password": password}
    response = requests.post(url, headers=api_config["headers"], json=payload)

    return {"status_code": response.status_code, "json_data": response.json()}


def get_account_info(bearer_token: str):
    url = f"{api_config['url']}/account/info"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    response = requests.get(url, headers=headers)

    return {"status_code": response.status_code, "json_data": response.json()}


def put_account_change_password(
    bearer_token: str, old_password: str, new_password: str
):
    url = f"{api_config['url']}/account/change/password"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    payload = {"old_password": old_password, "new_password": new_password}
    response = requests.put(url, headers=headers, json=payload)

    return {"status_code": response.status_code, "json_data": response.json()}


def get_module_list(bearer_token: str):
    url = f"{api_config['url']}/module/list"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    response = requests.get(url, headers=headers)

    return {"status_code": response.status_code, "json_data": response.json()}


def post_module_add(
    bearer_token: str,
    serial_number: str,
    friendly_name: str,
    battery_powered: bool,
    relay: bool,
    sensor_name: str = None,
    aes_key: str = None,
):
    url = f"{api_config['url']}/module/add"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    payload = {
        "serial_number": serial_number,
        "friendly_name": friendly_name,
        "battery_powered": battery_powered,
        "relay": relay,
        "sensor_name": sensor_name,
        "aes_key": aes_key,
    }
    response = requests.post(url, headers=headers, json=payload)

    return {"status_code": response.status_code, "json_data": response.json()}


def delete_module_delete(bearer_token: str, serial_number: str):
    url = f"{api_config['url']}/module/delete?serial_number={serial_number}"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    response = requests.delete(url, headers=headers)

    return {"status_code": response.status_code, "json_data": response.json()}


def get_data_get(
    bearer_token: str, serial_number: str, hours: int = 1, get_last_record: bool = False
):
    url = f"{api_config['url']}/data/get?serial_number={serial_number}&hours={hours}&get_last_record={get_last_record}"

    headers = dict(api_config["headers"])
    headers["Authorization"] = f"Bearer {bearer_token}"

    response = requests.get(url, headers=headers)

    return {"status_code": response.status_code, "json_data": response.json()}
