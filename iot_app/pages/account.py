import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from classes.api_endpoints import (
    get_account_info,
    put_account_change_password,
    get_module_list,
)
from classes.modules import is_logged

dash.register_page(__name__, path="/account", name="Account 👨‍💼")

layout = html.Div(
    [
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="my-account",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 mt-4 rounded",
                            children=[
                                html.H3("Account information", className="text-center"),
                                html.Div(id="account-info"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # html.Div(
        #     className="container",
        #     children=[
        #         html.Div(
        #             id="my-modules",
        #             className="row justify-content-center",
        #             children=[
        #                 html.Div(
        #                     className="col-md-6 bg-light p-4 m-2 rounded",
        #                     children=[
        #                         html.H3("My modules", className="text-center"),
        #                         html.Div(id="modules-info"),
        #                     ],
        #                 ),
        #             ],
        #         ),
        #     ],
        # ),
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="change-password",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 rounded",
                            children=[
                                html.H3("Change password", className="text-center"),
                                html.Label("Old password"),
                                dcc.Input(
                                    id="old-password-input",
                                    type="password",
                                    placeholder="Enter your old password",
                                    className="form-control mb-2",
                                    required=True,
                                ),
                                html.Label("New password"),
                                dcc.Input(
                                    id="new-password-input",
                                    type="password",
                                    placeholder="Enter your new password",
                                    className="form-control mb-3",
                                    required=True,
                                ),
                                html.Div(
                                    id="change-password-feedback",
                                    className="container text-center m-1 mb-2",
                                ),
                                html.Div(
                                    className="text-center",
                                    children=[
                                        html.Button(
                                            "Change",
                                            id="change-button",
                                            n_clicks=0,
                                            className="btn btn-danger m-1 button-width-100",
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
            id="go-back-to-login-account",
            className="text-center",
        ),
    ]
)


@callback(
    Output("go-back-to-login-account", "children"),
    Output("go-back-to-login-account", "hidden"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def show_or_hide_back_to_login_account(login_time, bearer_token, n_intervals):

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
    Output("account-info", "children"),
    Output("my-account", "hidden"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def display_account_info(login_time, bearer_token, n_intervals):

    if is_logged(login_time, bearer_token):
        account_info_response = get_account_info(bearer_token)
        if account_info_response["status_code"] == 200:
            account_info = account_info_response["json_data"]

            account_info_elements = [
                html.B("ID: "),
                f"{account_info['id']}",
                html.Br(),
                html.B("Username: "),
                f"{account_info['username']}",
                html.Div(
                    className="text-center mt-2",
                    children=[
                        html.A(
                            "Logout",
                            id="logout-btn",
                            className="btn btn-secondary m-1 button-width-100",
                            href="/?logout=true",
                        ),
                    ],
                ),
            ]

            return account_info_elements, False
    else:
        return None, True


# @callback(
#     Output("modules-info", "children"),
#     Output("my-modules", "hidden"),
#     Input("login-time-storage", "data"),
#     Input("bearer-token-storage", "data"),
#     Input("refresh-trigger", "n_intervals"),
# )
# def display_modules_info(login_time, bearer_token, n_intervals):

#     if is_logged(login_time, bearer_token):
#         modules_info_response = get_module_list(bearer_token)

#         if modules_info_response["status_code"] == 200:
#             modules_info = modules_info_response["json_data"]

#             modules_info_elements = [
#                 html.Ul(
#                     [
#                         html.Li(
#                             [
#                                 html.B("Name: "),
#                                 f"{module['friendly_name']}",
#                                 html.Ul(
#                                     [
#                                         html.Li(
#                                             [
#                                                 html.B("Serial number: "),
#                                                 f"{module['serial_number']}",
#                                             ]
#                                         ),
#                                         html.Li(
#                                             [
#                                                 html.B("Has battery: "),
#                                                 f"{'Yes' if module['battery_powered'] else 'No'}",
#                                             ]
#                                         ),
#                                         html.Li(
#                                             [
#                                                 html.B("Is relay: "),
#                                                 f"{'Yes' if module['relay'] else 'No'}",
#                                             ]
#                                         ),
#                                         html.Li(
#                                             [
#                                                 html.B("Sensor inside: "),
#                                                 f"{module['sensor_name'] if module['sensor_name'] else 'No'}",
#                                             ]
#                                         ),
#                                     ]
#                                 ),
#                             ]
#                         )
#                         for module in modules_info
#                     ]
#                 ),
#             ]
#             return modules_info_elements, False

#         else:
#             return None, True
#     else:
#         return None, True


@callback(
    Output("old-password-input", "value"),
    Output("new-password-input", "value"),
    Output("change-password", "hidden"),
    Output("change-password-feedback", "children"),
    Output("change-password-feedback", "hidden"),
    Output("change-button", "n_clicks"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("change-button", "n_clicks"),
    State("old-password-input", "value"),
    State("new-password-input", "value"),
)
def change_account_password(
    login_time, bearer_token, n_clicks_change, old_password, new_password
):
    if is_logged(login_time, bearer_token):
        if n_clicks_change > 0 and is_logged(login_time, bearer_token):

            if not old_password:
                old_password = None
            if not new_password:
                new_password = None

            if old_password is not None and new_password is not None:
                password_change_response = put_account_change_password(
                    bearer_token, old_password, new_password
                )

                if password_change_response["status_code"] == 200:
                    return (
                        "",
                        "",
                        False,
                        html.Div(
                            className="text-success",
                            children="Password changed successfully.",
                        ),
                        False,
                        0,
                    )
                else:
                    return (
                        old_password,
                        new_password,
                        False,
                        html.Div(
                            className="text-danger",
                            children="Failed to change password. Please try again.",
                        ),
                        False,
                        0,
                    )
            else:
                return (
                    old_password,
                    new_password,
                    False,
                    html.Div(
                        "Old password and new password required fields.",
                        className="text-danger",
                    ),
                    False,
                    0,
                )

        return old_password, new_password, False, None, True, 0
    else:
        return "", "", True, None, True, 0
