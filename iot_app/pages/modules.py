import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from classes.api_endpoints import (
    get_module_list,
    post_module_add,
    delete_module_delete,
    get_data_get,
)
from classes.modules import is_logged
from datetime import datetime, timedelta

dash.register_page(__name__, path="/modules", name="Modules 🔧")

layout = html.Div(
    [
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="add-module",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 mt-4 rounded",
                            children=[
                                html.H3("Add module", className="text-center"),
                                html.Label("Serial number"),
                                dcc.Input(
                                    id="serial-number-input",
                                    type="text",
                                    placeholder="sn001",
                                    className="form-control mb-2",
                                    required=True,
                                ),
                                html.Label("Name"),
                                dcc.Input(
                                    id="name-input",
                                    type="text",
                                    placeholder="My module",
                                    className="form-control mb-3",
                                    required=True,
                                ),
                                html.Label("AES key"),
                                dcc.Input(
                                    id="aes-input",
                                    type="text",
                                    placeholder="q68dd47e8223272e69e108817521378e9",
                                    className="form-control mb-3",
                                ),
                                html.Label("Has battery"),
                                dcc.RadioItems(
                                    id="battery-powered-radio-input",
                                    options=[
                                        {"label": " Yes", "value": 1},
                                        {"label": " No", "value": 0},
                                    ],
                                    value=0,
                                    className="form-control mb-3",
                                ),
                                html.Label("Is relay"),
                                dcc.RadioItems(
                                    id="relay-radio-input",
                                    options=[
                                        {"label": " Yes", "value": 1},
                                        {"label": " No", "value": 0},
                                    ],
                                    value=0,
                                    className="form-control mb-3",
                                ),
                                html.Label("Sensor name"),
                                dcc.Input(
                                    id="sensor-name-input",
                                    type="text",
                                    placeholder="bmp280",
                                    className="form-control mb-3",
                                ),
                                html.Div(
                                    id="add-module-feedback",
                                    className="container text-center m-1 mb-2",
                                ),
                                html.Div(
                                    className="text-center",
                                    children=[
                                        html.Button(
                                            "Add",
                                            id="add-button",
                                            n_clicks=0,
                                            className="btn btn-success m-1 button-width-100",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="module-to-delete",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 mb-4 rounded",
                            children=[
                                html.H3("Delete module", className="text-center"),
                                html.Label("Select module to delete"),
                                dcc.Dropdown(
                                    id="module-to-delete-dropdown",
                                    className="form-control mb-3",
                                ),
                                html.Div(
                                    id="delete-module-feedback",
                                    className="container text-center m-1 mb-2",
                                ),
                                html.Div(
                                    className="text-center",
                                    children=[
                                        html.Button(
                                            "Delete",
                                            id="delete-module-button",
                                            n_clicks=0,
                                            className="btn btn-danger m-1 button-width-100",
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="modules-info-show",
                    className="row justify-content-center",
                ),
            ],
        ),
        html.Div(
            id="go-back-to-login-modules",
            className="text-center",
        ),
    ]
)


@callback(
    Output("go-back-to-login-modules", "children"),
    Output("go-back-to-login-modules", "hidden"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def show_or_hide_back_to_login_modules(login_time, bearer_token, n_intervals):

    if is_logged(login_time, bearer_token):
        return (
            None,
            True,
        )
    else:
        return (
            html.Div(
                children=[
                    html.A(
                        "Back to login!",
                        id="back-to-login-btn",
                        className="btn btn-dark m-2 fs-5 text-center",
                        href="/",
                    ),
                ]
            ),
            False,
        )


@callback(
    Output("add-module", "hidden"),
    Output("add-module-feedback", "children"),
    Output("add-module-feedback", "hidden"),
    Output("serial-number-input", "value"),
    Output("name-input", "value"),
    Output("aes-input", "value"),
    Output("battery-powered-radio-input", "value"),
    Output("relay-radio-input", "value"),
    Output("sensor-name-input", "value"),
    Output("add-button", "n_clicks"),
    Input("add-button", "n_clicks"),
    State("serial-number-input", "value"),
    State("name-input", "value"),
    State("aes-input", "value"),
    State("battery-powered-radio-input", "value"),
    State("relay-radio-input", "value"),
    State("sensor-name-input", "value"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def add_new_module(
    n_clicks,
    serial_number,
    name,
    aes_key,
    has_battery,
    is_relay,
    sensor_name,
    login_time,
    bearer_token,
    n_intervals,
):

    if is_logged(login_time, bearer_token):

        if not aes_key:
            aes_key = None
        if not serial_number:
            serial_number = None
        if not name:
            name = None
        if not sensor_name:
            sensor_name = None

        if (not serial_number or not name) and n_clicks > 0:
            return (
                False,
                html.Div(
                    "Serial number and name are required fields.",
                    className="text-danger",
                ),
                False,
                serial_number,
                name,
                aes_key,
                has_battery,
                is_relay,
                sensor_name,
                0,
            )

        modules_info_response = get_module_list(bearer_token)
        if modules_info_response["status_code"] == 200:
            modules_info = modules_info_response["json_data"]
            serial_numbers = [module["serial_number"] for module in modules_info]
            if serial_number in serial_numbers:
                return (
                    False,
                    html.Div("Serial number must be unique.", className="text-danger"),
                    False,
                    serial_number,
                    name,
                    aes_key,
                    has_battery,
                    is_relay,
                    sensor_name,
                    0,
                )

        if n_clicks > 0:
            add_module_response = post_module_add(
                bearer_token,
                serial_number,
                name,
                has_battery,
                is_relay,
                sensor_name,
                aes_key,
            )

            if add_module_response["status_code"] == 200:
                return (
                    False,
                    html.Div("Module added successfully.", className="text-success"),
                    False,
                    "",
                    "",
                    "",
                    0,
                    0,
                    "",
                    0,
                )
            else:
                return (
                    False,
                    html.Div(
                        "Failed to add module. Please try again.",
                        className="text-danger",
                    ),
                    False,
                    serial_number,
                    name,
                    aes_key,
                    has_battery,
                    is_relay,
                    sensor_name,
                    0,
                )
        return (
            False,
            True,
            True,
            serial_number,
            name,
            aes_key,
            has_battery,
            is_relay,
            sensor_name,
            0,
        )
    else:
        return (
            True,
            True,
            True,
            serial_number,
            name,
            aes_key,
            has_battery,
            is_relay,
            sensor_name,
            0,
        )


@callback(
    Output("module-to-delete-dropdown", "options"),
    Output("module-to-delete", "hidden"),
    Output("delete-module-feedback", "children"),
    Output("delete-module-feedback", "hidden"),
    Output("delete-module-button", "n_clicks"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("delete-module-button", "n_clicks"),
    Input("add-button", "n_clicks"),
    State("module-to-delete-dropdown", "value"),
    Input("refresh-trigger", "n_intervals"),
)
def select_module_to_delete(
    login_time,
    bearer_token,
    n_clicks_delete,
    n_clicks_update,
    serial_number,
    n_intervals,
):

    if is_logged(login_time, bearer_token):
        modules_info_response = get_module_list(bearer_token)
        if modules_info_response["status_code"] == 200:
            modules_info = modules_info_response["json_data"]

            module_options = [
                {
                    "label": f'{module["friendly_name"]} - {module["serial_number"]}',
                    "value": module["serial_number"],
                }
                for module in modules_info
            ]

            if n_clicks_delete > 0 and serial_number:
                delete_response = delete_module_delete(bearer_token, serial_number)
                if delete_response["status_code"] == 200:
                    module_options = [
                        module
                        for module in module_options
                        if module["value"] != serial_number
                    ]
                    return (
                        module_options,
                        False,
                        html.Div(
                            "Module deleted successfully.",
                            className="text-success",
                        ),
                        False,
                        0,
                    )
                else:
                    return (
                        module_options,
                        False,
                        html.Div(
                            "Failed to delete module. Please try again.",
                            className="text-danger",
                        ),
                        False,
                        0,
                    )

            return module_options, False, None, True, 0

    return [], True, None, True, 0


@callback(
    Output("modules-info-show", "children"),
    Output("modules-info-show", "hidden"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("delete-module-button", "n_clicks"),
    Input("add-button", "n_clicks"),
    Input("refresh-trigger", "n_intervals"),
)
def show_module(login_time, bearer_token, n_clicks_delete, n_clicks_add, n_intervals):

    if is_logged(login_time, bearer_token):
        modules_info_response = get_module_list(bearer_token)
        if modules_info_response["status_code"] == 200:
            modules_info = modules_info_response["json_data"]

            current_time = datetime.now()

            for module in modules_info:
                if not module["relay"]:
                    data_about_module_response = get_data_get(
                        bearer_token, module["serial_number"], 1, True
                    )
                    if (
                        data_about_module_response["status_code"] == 200
                        and data_about_module_response["json_data"]
                    ):
                        time_format = "%Y-%m-%dT%H:%M:%S"
                        time = datetime.strptime(
                            data_about_module_response["json_data"][0]["time"],
                            time_format,
                        )
                        time_plus_sleep_time = time + timedelta(
                            seconds=(
                                data_about_module_response["json_data"][0]["sleep_time"]
                                + data_about_module_response["json_data"][0][
                                    "sleep_time"
                                ]
                                + (
                                    data_about_module_response["json_data"][0][
                                        "sleep_time"
                                    ]
                                    * 0.1
                                )
                            )
                        )

                        module["sleep_time"] = (
                            str(
                                data_about_module_response["json_data"][0]["sleep_time"]
                            )
                            + "s"
                        )
                        module["last_seen"] = time

                        if module["battery_powered"]:

                            data_about_module_response["json_data"][0]["data"]["vol"]
                            battery_vol = data_about_module_response["json_data"][0][
                                "data"
                            ]["vol"]

                            min_voltage = 2.5
                            max_voltage = 4.2

                            battery_percent = (
                                (battery_vol - min_voltage)
                                / (max_voltage - min_voltage)
                            ) * 100
                            battery_percent = int(round(battery_percent, 0))
                            module["last_battery_level"] = f"{battery_percent}% ± 5%"

                        else:
                            module["last_battery_level"] = "Not available"

                        if time_plus_sleep_time > current_time:
                            module["status"] = "Alive"
                        elif time_plus_sleep_time < current_time:
                            module["status"] = "Dead"
                    else:
                        module["last_battery_level"] = "Not available"
                        module["sleep_time"] = "No sleep time"
                        module["last_seen"] = "Not available"
                        module["status"] = "Not available"
                else:
                    module["last_battery_level"] = "Not available"
                    module["sleep_time"] = "No sleep time"
                    module["last_seen"] = "Not available"
                    module["status"] = "Not available"

            modules_layout = [
                html.Div(
                    className="col-md-6 bg-light p-4 m-2 rounded",
                    children=[
                        html.H3(f"{module['friendly_name']}", className="text-center"),
                        html.B("Name: "),
                        f"{module['friendly_name']}",
                        html.Br(),
                        html.B("Serial number: "),
                        f"{module['serial_number']}",
                        html.Br(),
                        html.B("Has battery: "),
                        f"{'Yes' if module['battery_powered'] else 'No'}",
                        html.Br(),
                        html.B("Is relay: "),
                        f"{'Yes' if module['relay'] else 'No'}",
                        html.Br(),
                        html.B("Sensor inside: "),
                        f"{module['sensor_name'] if module['sensor_name'] else 'No'}",
                        html.Br(),
                        html.B("Status: "),
                        f"{module['status']}",
                        html.Br(),
                        html.B("Sleep time: "),
                        f"{module['sleep_time']}",
                        html.Br(),
                        html.B("Last seen: "),
                        f"{module['last_seen']}",
                        html.Br(),
                        html.B("Last battery level: "),
                        f"{module['last_battery_level']}",
                    ],
                )
                for module in modules_info
            ]

            return modules_layout, False

        else:
            return None, True
    else:
        return None, True
