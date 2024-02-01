from dash import html
from dash import dcc


def classify_time(hour):
    if 8 <= hour < 14:
        return '[08 a.m - 2 p.m)'
    elif 14 <= hour < 20:
        return '[2 p.m - 8 p.m)'
    elif 20 <= hour < 3:
        return '[8 p.m - 3 a.m)'
    else:
        return '[3 a.m - 8 a.m)'


def Header(app, license_id, package_id, start_date, end_date):
    # return html.Div([get_header(app,license_id, package_id), html.Br([]), get_menu()])
    return html.Div([get_header(app, license_id, package_id, start_date, end_date)])


def get_header(app, license_id, package_id, start_date, end_date):
    header = html.Div(
        [
            html.Div(
                [
                    html.A(
                        html.Img(
                            src=app.get_asset_url("identy_logo.png"),
                            className="logo",
                        )
                    )
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H5("Finger Basic Report")],
                        className="twelve columns main-title",
                    ),
                    html.Div(
                        [html.H6(f"License ID: {license_id} - Package ID: {package_id} - Dates: {start_date} - {end_date} " )],
                        style={"margin-bottom": "20px"},
                        className="twelve columns main-title"
                    ),
                    html.Div(
                        [
                            # html.H5("Product Summary"),
                            html.P(
                                "Analyzing Finger SDK data helps to make informed decisions, identify patterns and user"
                                " behaviors, and enhance your services to align more effectively with customer"
                                " requirements.",
                                className="product",
                                style={"font-size": "14px", "text-align": "justify", "margin-right": "7%"}
                            ),
                        ]
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "5%"},
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link(
                "Overview",
                href="/overview",
                className="tab first"
            ),
            dcc.Link(
                "Activity",
                href="/activity",
                className="tab",
            ),
            dcc.Link(
                "Security",
                href="/security",
                className="tab",
            )
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
