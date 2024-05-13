import dash
from dash import html

dash.register_page(__name__, name="404 - Page not found 🤷‍♂️")

layout = html.Div(
    [
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="login-welcome-message",
                    className="row justify-content-center",
                    children=[
                        html.Div(
                            className="col-md-6 bg-light p-4 m-2 mt-4 rounded text-center",
                            children=[
                                html.H4(
                                    "404 - Page not found 🤷‍♂️",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
)
