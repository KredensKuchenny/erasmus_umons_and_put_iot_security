import dash
from dash import Dash, html, dcc, Output, Input
from classes.modules import is_logged

external_css = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css",
]

app = Dash(
    __name__,
    pages_folder="pages",
    use_pages=True,
    external_stylesheets=external_css,
    assets_folder="assets",
    suppress_callback_exceptions=True,
)

# server = app.server

app.layout = html.Div(
    [
        html.Link(href="/assets/style/styles.css", rel="stylesheet"),
        dcc.Store(id="bearer-token-storage", storage_type="session"),
        dcc.Store(id="login-time-storage", storage_type="session"),
        dcc.Interval(id="refresh-trigger", interval=5000),
        html.Br(),
        html.P("iot-app.cebulowe.it", className="text-dark text-center fw-bold fs-1"),
        html.Div(id="page-links", className="text-center"),
        dash.page_container,
    ],
    className="col-8 mx-auto",
)


@app.callback(
    Output("page-links", "children"),
    Input("login-time-storage", "data"),
    Input("bearer-token-storage", "data"),
    Input("refresh-trigger", "n_intervals"),
)
def show_page_links(login_time, bearer_token, n_intervals):
    if is_logged(login_time, bearer_token):
        return html.Div(
            children=[
                dcc.Link(
                    page["name"],
                    href=page["relative_path"],
                    className="btn btn-dark m-2 fs-5",
                )
                for page in dash.page_registry.values()
                if page["name"] != "Login or register"
                and page["name"] != "404 - Page not found 🤷‍♂️"
            ]
        )
    else:
        return None


if __name__ == "__main__":
    app.run(debug=True)
