import ujson as json
import requests


def read_from_file(file_path):
    with open(file_path, "r") as file:
        return str(file.read())


def read_and_send_first_line(file_path, host):
    with open(file_path, "r") as file:
        lines = file.readlines()

    if lines:
        first_line = lines[0]
        print("First line from file:", first_line.replace("\n", ""))
        code = send_json_in_post(host, first_line.replace("\n", ""))

        if code:
            with open(file_path, "w") as file:
                for line in lines[1:]:
                    file.write(line)


def save_to_file_line_by_line(file_path, json_data):
    with open(file_path, "a") as file:
        print("Saving data to file")
        file.write(json_data + "\n")


def convert_python_dictionary_to_json(python_dictionary):
    print("Converting data to JSON")
    return json.dumps(python_dictionary)


def send_json_in_post(host, json_data):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(host, headers=headers, json=json.loads(json_data))
        print("Status code: ", response.status_code)
        print("Printing entire post request")
        print(response.json())

        if response.status_code in [200, 201, 202, 422, 404]:
            return 1
        else:
            return 0
    except:
        return 0
