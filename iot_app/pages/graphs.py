import dash
from dash import dcc, html, callback
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from classes.modules import is_logged
from classes.api_endpoints import get_module_list, get_data_get
from datetime import datetime
import re


dash.register_page(__name__, path="/graphs", name="Graphs 📈")

layout = html.Div(
    [
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="select-section",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-10 bg-light p-4 m-2 mt-4 mb-4 rounded",
                            children=[
                                html.H3("Selector", className="text-center"),
                                html.Label("Select module to get data list"),
                                dcc.Dropdown(
                                    id="module-selector",
                                    className="form-control mb-3",
                                ),
                                html.Label("Select type of data to show"),
                                dcc.Dropdown(
                                    id="data-selector",
                                    className="form-control mb-3",
                                ),
                                html.Label("Select time"),
                                dcc.Dropdown(
                                    options=[
                                        {"label": "1 hour", "value": 1},
                                        {"label": "3 hours", "value": 3},
                                        {"label": "6 hours", "value": 6},
                                        {"label": "12 hours", "value": 12},
                                        {"label": "1 day", "value": 24},
                                        {"label": "3 days", "value": 72},
                                        {"label": "7 days", "value": 168},
                                        {"label": "14 days", "value": 336},
                                        {"label": "30 days", "value": 720},
                                        {"label": "90 days", "value": 2160},
                                    ],
                                    value=1,
                                    id="hour-selector",
                                    className="form-control mb-3",
                                ),
                                html.Div(
                                    id="create-graph-feedback",
                                    className="container text-center m-1 mb-2",
                                ),
                                html.Div(
                                    className="buttons-display",
                                    children=[
                                        html.Button(
                                            "Show graph",
                                            id="show-button",
                                            n_clicks=0,
                                            className="btn btn-primary m-1 button-width",
                                        ),
                                        html.Button(
                                            "Clear graphs",
                                            id="clear-button",
                                            n_clicks=0,
                                            className="btn btn-danger m-1 button-width",
                                        ),
                                        html.Button(
                                            "Add next graph",
                                            id="add-graph-button",
                                            n_clicks=0,
                                            className="btn btn-success m-1 button-width",
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
                    id="show-graph",
                    className="row justify-content-center",
                ),
            ],
        ),
        html.Div(
            id="go-back-to-login-graphs",
            className="text-center",
        ),
    ]
)


def get_data_to_graph(bearer_token, serial_number, data_type, time):
    x_axis = []
    y_axis = []
    modules_info_response = get_module_list(bearer_token)
    data_about_module_response = get_data_get(bearer_token, serial_number, time, False)

    if (
        data_about_module_response["status_code"] == 200
        and modules_info_response["status_code"] == 200
        and modules_info_response["json_data"]
        and data_about_module_response["json_data"]
    ):
        modules_info = modules_info_response["json_data"]
        data_about_module = data_about_module_response["json_data"]
        module_info = []

        for module in modules_info:
            if module["serial_number"] == serial_number:
                module_info = module
                break

        if not module_info:
            return [], []

        sorted_data_about_module = sorted(data_about_module, key=lambda x: x["time"])

        if data_type == "rssi" or data_type == "snr":
            for data in sorted_data_about_module:
                x_axis.append(datetime.fromisoformat(data["time"]))
                y_axis.append(data["signal"][data_type])

        elif data_type == "vol":
            for data in sorted_data_about_module:
                x_axis.append(datetime.fromisoformat(data["time"]))
                y_axis.append(data["data"]["vol"])

        elif data_type == "press" or data_type == "temp" or data_type == "hum":
            for data in sorted_data_about_module:
                x_axis.append(datetime.fromisoformat(data["time"]))
                y_axis.append(data["data"][module_info["sensor_name"]][data_type])

        return x_axis, y_axis

    return [], []


@callback(
    Output("go-back-to-login-graphs", "children"),
    Output("go-back-to-login-graphs", "hidden"),
    Output("select-section", "hidden"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def show_or_hide_back_to_login_graphs(login_time, bearer_token, n_intervals):

    if is_logged(login_time, bearer_token):
        return (
            None,
            True,
            False,
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
            True,
        )


@callback(
    Output("module-selector", "options"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
)
def select_module(
    login_time,
    bearer_token,
):

    if is_logged(login_time, bearer_token):
        modules_info_response = get_module_list(bearer_token)
        if (
            modules_info_response["status_code"] == 200
            and modules_info_response["json_data"]
        ):
            modules_info = modules_info_response["json_data"]

            module_options = [
                {
                    "label": f'{module["friendly_name"]} - {module["serial_number"]}',
                    "value": module["serial_number"],
                }
                for module in modules_info
                if not module.get("relay")
            ]

            return module_options

    return []


@callback(
    Output("data-selector", "options"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("module-selector", "value"),
)
def select_data(
    login_time,
    bearer_token,
    selected_module,
):
    if is_logged(login_time, bearer_token):
        modules_info_response = get_module_list(bearer_token)
        data_about_module_response = get_data_get(
            bearer_token, selected_module, 1, True
        )

        if (
            data_about_module_response["status_code"] == 200
            and modules_info_response["status_code"] == 200
            and data_about_module_response["json_data"]
            and modules_info_response["json_data"]
        ):
            module_info = []
            modules_info = modules_info_response["json_data"]
            data_about_module = data_about_module_response["json_data"][0]

            for module in modules_info:
                if module["serial_number"] == selected_module:
                    module_info = module
                    break

            if not module_info:
                return []

            data = []

            if module_info["battery_powered"]:
                temp = {
                    "label": "Battery Voltage [V]",
                    "value": "vol",
                }
                data.append(temp)

            for k, v in data_about_module["data"][module_info["sensor_name"]].items():
                temp = {}

                if k == "press":
                    temp = {
                        "label": "Pressure [hPa]",
                        "value": "press",
                    }
                    data.append(temp)

                elif k == "temp":
                    temp = {
                        "label": "Temperature [°C]",
                        "value": "temp",
                    }
                    data.append(temp)

                elif k == "hum":
                    temp = {
                        "label": "Relative Humidity [% RH]",
                        "value": "hum",
                    }
                    data.append(temp)

            for k, v in data_about_module.items():
                temp = {}

                if k == "signal":
                    for signal_key, signal_value in v.items():
                        if signal_key != "crcok":
                            if signal_key == "rssi":
                                temp = {
                                    "label": "RSSI [dBm]",
                                    "value": signal_key,
                                }
                                data.append(temp)
                            elif signal_key == "snr":
                                temp = {
                                    "label": "SNR [dB]",
                                    "value": signal_key,
                                }
                                data.append(temp)

            return data

    return []


@callback(
    Output("show-graph", "hidden"),
    Output("show-graph", "children"),
    Output("show-button", "n_clicks"),
    Output("clear-button", "n_clicks"),
    Output("add-graph-button", "n_clicks"),
    Output("create-graph-feedback", "children"),
    Output("create-graph-feedback", "hidden"),
    Input("show-button", "n_clicks"),
    Input("clear-button", "n_clicks"),
    Input("add-graph-button", "n_clicks"),
    Input("show-graph", "children"),
    State("login-time-storage", "data"),
    State("bearer-token-storage", "data"),
    State("module-selector", "value"),
    State("data-selector", "value"),
    State("hour-selector", "value"),
    Input("refresh-trigger", "n_intervals"),
)
def manage_graph(
    n_clicks_show,
    n_clicks_clear,
    n_clicks_add,
    show_graph,
    login_time,
    bearer_token,
    serial_number,
    data_type,
    time,
    n_intervals,
):
    if is_logged(login_time, bearer_token):
        x_axis = 0
        y_axis = 0

        if n_clicks_show > 0:
            if serial_number and data_type and time:
                x_axis, y_axis = get_data_to_graph(
                    bearer_token, serial_number, data_type, time
                )

            if x_axis and y_axis:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_axis, y=y_axis, mode="lines"))

                data_type_name = ""

                if data_type == "press":
                    data_type_name = "Pressure [hPa]"
                elif data_type == "temp":
                    data_type_name = "Temperature [°C]"
                elif data_type == "hum":
                    data_type_name = "Relative Humidity [% RH]"
                elif data_type == "rssi":
                    data_type_name = "RSSI [dBm]"
                elif data_type == "snr":
                    data_type_name = "SNR [dB]"
                elif data_type == "vol":
                    data_type_name = "Battery Voltage [V]"

                pattern = r"\[(.*?)\]"
                data_type_name_result = re.sub(pattern, "", data_type_name)

                fig.update_layout(
                    title=f"{serial_number} - {data_type_name_result}over Time",
                    title_x=0.5,
                    xaxis_title="Time",
                    yaxis_title=data_type_name,
                    margin=dict(l=10, r=10, b=10, t=60),
                    paper_bgcolor="#f8f9fa",
                )

                graph_div = html.Div(
                    className="col-md-10 bg-light p-2 m-2 rounded",
                    children=[
                        dcc.Graph(
                            figure=fig,
                        )
                    ],
                )

                return (
                    False,
                    graph_div,
                    0,
                    0,
                    0,
                    html.Div(
                        "Graph generated successfully.",
                        className="text-success",
                    ),
                    False,
                )

            else:
                return (
                    False,
                    None,
                    0,
                    0,
                    0,
                    html.Div(
                        "No data to show, generate graph failed.",
                        className="text-danger",
                    ),
                    False,
                )

        elif n_clicks_clear > 0:
            return (
                True,
                None,
                0,
                0,
                0,
                html.Div(
                    "Graphs cleared successfully.",
                    className="text-success",
                ),
                False,
            )

        elif n_clicks_add > 0:
            if serial_number and data_type and time:
                x_axis, y_axis = get_data_to_graph(
                    bearer_token, serial_number, data_type, time
                )

            if x_axis and y_axis:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_axis, y=y_axis, mode="lines"))

                data_type_name = ""

                if data_type == "press":
                    data_type_name = "Pressure [hPa]"
                elif data_type == "temp":
                    data_type_name = "Temperature [°C]"
                elif data_type == "hum":
                    data_type_name = "Relative Humidity [% RH]"
                elif data_type == "rssi":
                    data_type_name = "RSSI [dBm]"
                elif data_type == "snr":
                    data_type_name = "SNR [dB]"
                elif data_type == "vol":
                    data_type_name = "Battery Voltage [V]"

                pattern = r"\[(.*?)\]"
                data_type_name_result = re.sub(pattern, "", data_type_name)

                fig.update_layout(
                    title=f"{serial_number} - {data_type_name_result}over Time",
                    title_x=0.5,
                    xaxis_title="Time",
                    yaxis_title=data_type_name,
                    margin=dict(l=10, r=10, b=10, t=60),
                    paper_bgcolor="#f8f9fa",
                )

                graph_div = html.Div(
                    className="col-md-10 bg-light p-2 m-2 rounded",
                    children=[
                        dcc.Graph(
                            figure=fig,
                        )
                    ],
                )

                if show_graph is not None:
                    return_graph_div = []

                    if isinstance(show_graph, dict):
                        return_graph_div.append(show_graph)
                        return_graph_div.append(graph_div)
                    elif isinstance(show_graph, list):
                        for element_of_show_graph in show_graph:
                            return_graph_div.append(element_of_show_graph)

                        return_graph_div.append(graph_div)

                    return (
                        False,
                        return_graph_div,
                        0,
                        0,
                        0,
                        html.Div(
                            "Graph generated successfully.",
                            className="text-success",
                        ),
                        False,
                    )

                return (
                    False,
                    graph_div,
                    0,
                    0,
                    0,
                    html.Div(
                        "Graph generated successfully.",
                        className="text-success",
                    ),
                    False,
                )

            else:
                return (
                    False,
                    show_graph,
                    0,
                    0,
                    0,
                    html.Div(
                        "No data to show, generate graph failed.",
                        className="text-danger",
                    ),
                    False,
                )

        else:
            return False, show_graph, 0, 0, 0, None, True

    return True, None, 0, 0, 0, None, True
