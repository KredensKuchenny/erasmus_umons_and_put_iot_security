import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from classes.api_endpoints import (
    post_account_login,
    post_account_register,
    get_account_info,
)
from classes.modules import is_logged
import datetime
from config.api import api_config
from furl import furl

dash.register_page(__name__, path="/", name="Login or register")
layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="login-register-form",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 rounded",
                            children=[
                                html.H3(
                                    "Login or register", className="mb-4 text-center"
                                ),
                                html.Label("Username"),
                                dcc.Input(
                                    id="username-input",
                                    type="text",
                                    placeholder="Enter your username",
                                    className="form-control mb-2",
                                ),
                                html.Label("Password"),
                                dcc.Input(
                                    id="password-input",
                                    type="password",
                                    placeholder="Enter your password",
                                    className="form-control mb-3",
                                ),
                                html.Div(
                                    id="login-or-register-feedback",
                                    className="container text-center m-1 mb-2",
                                ),
                                html.Div(
                                    className="buttons-display",
                                    children=[
                                        html.Button(
                                            "Login",
                                            id="login-button",
                                            n_clicks=0,
                                            className="btn btn-primary m-1 button-width",
                                        ),
                                        html.Button(
                                            "Register",
                                            id="register-button",
                                            n_clicks=0,
                                            className="btn btn-secondary m-1 button-width",
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
                    id="login-welcome-message",
                    className="row justify-content-center",
                ),
            ],
        ),
    ]
)


@callback(
    Output("bearer-token-storage", "data"),
    Output("login-time-storage", "data"),
    Output("login-register-form", "hidden"),
    Output("login-welcome-message", "hidden"),
    Output("login-welcome-message", "children"),
    Output("login-or-register-feedback", "hidden"),
    Output("login-or-register-feedback", "children"),
    Output("register-button", "n_clicks"),
    Output("login-button", "n_clicks"),
    Input("login-button", "n_clicks"),
    Input("register-button", "n_clicks"),
    Input("url", "href"),
    State("login-time-storage", "data"),
    State("bearer-token-storage", "data"),
    State("username-input", "value"),
    State("password-input", "value"),
)
def login_or_register(
    n_clicks_login,
    n_clicks_register,
    href: str,
    login_time,
    bearer_token,
    username,
    password,
):
    try:
        link = furl(href)
        param = link.args["logout"]
        if bool(param) and n_clicks_login == 0 and n_clicks_register == 0:
            return (None, None, False, True, None, False, None, 0, 0)
    except:
        pass

    if n_clicks_register > 0:
        register_response = post_account_register(username, password)

        if register_response["status_code"] == 201:
            login_response = post_account_login(username, password)

            if login_response["status_code"] == 202:
                login_time_get = datetime.datetime.now() + datetime.timedelta(
                    minutes=api_config["token_time"]
                )
                bearer_token_get = login_response["json_data"]["access_token"]
                account_info_response = get_account_info(bearer_token_get)

                if account_info_response["status_code"] == 200:
                    account_username = account_info_response["json_data"]["username"]
                else:
                    account_username = "Undefined"

                return (
                    bearer_token_get,
                    login_time_get,
                    True,
                    False,
                    html.Div(
                        className="col-md-6 bg-light p-4 m-2 mt-4 rounded text-center",
                        children=[
                            html.H4(
                                f"Welcome 👋 {account_username} in control panel!",
                            ),
                        ],
                    ),
                    True,
                    None,
                    0,
                    0,
                )
        else:
            return (
                None,
                None,
                False,
                True,
                None,
                False,
                html.Div(
                    className="text-danger",
                    children="Failed to register. Please check your credentials and try again.",
                ),
                0,
                0,
            )

    if n_clicks_login > 0:
        login_response = post_account_login(username, password)

        if login_response["status_code"] == 202:
            login_time_get = datetime.datetime.now() + datetime.timedelta(
                minutes=api_config["token_time"]
            )

            bearer_token_get = login_response["json_data"]["access_token"]
            account_info_response = get_account_info(bearer_token_get)

            if account_info_response["status_code"] == 200:
                account_username = account_info_response["json_data"]["username"]
            else:
                account_username = "Undefined"
            return (
                bearer_token_get,
                login_time_get,
                True,
                False,
                html.Div(
                    className="col-md-6 bg-light p-4 m-2 mt-4 rounded text-center",
                    children=[
                        html.H4(
                            f"Welcome 👋 {account_username} in control panel!",
                        ),
                    ],
                ),
                True,
                None,
                0,
                0,
            )
        else:
            return (
                None,
                None,
                False,
                True,
                None,
                False,
                html.Div(
                    className="text-danger",
                    children="Failed to login. Please check your credentials and try again.",
                ),
                0,
                0,
            )

    if is_logged(login_time, bearer_token):
        account_info_response = get_account_info(bearer_token)
        if account_info_response["status_code"] == 200:
            account_username = account_info_response["json_data"]["username"]
        else:
            account_username = "Undefined"

        return (
            bearer_token,
            login_time,
            True,
            False,
            html.Div(
                className="col-md-6 bg-light p-4 m-2 mt-4 rounded text-center",
                children=[
                    html.H4(
                        f"Welcome 👋 {account_username} in control panel!",
                    ),
                ],
            ),
            True,
            None,
            0,
            0,
        )
    else:
        return (None, None, False, True, None, False, None, 0, 0)
