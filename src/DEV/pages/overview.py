from dash import html, dcc

from src.DEV.utils.utils_dash import Header, make_dash_table
import plotly.express as px
import plotly.graph_objects as go

# Read finger CSV
'''
trx_summary = 'data/summary_ocr.csv'
df_trx_summary = pd.read_csv(trx_summary)

weekday_usage = 'data/df_agg_trx_weekdays.csv'
df_weekday_usage = pd.read_csv(weekday_usage)
'''


def add_separator(text):
    return html.Div([
        html.Div([
            html.H6(text, className="section"),
            html.Hr(style={'margin-top': '0px', 'margin-bottom': '10px', 'margin-left': '6%', 'margin-right': '6%'})
        ])
    ], className="row")


def add_summary_data(df_trx_summary, df_detection_mode):
    # Create Graph for Transaction type
    fig_trx_type = px.bar(
        df_detection_mode,
        x='DetectionMode',
        y='Total',
        color='SdkVersion',
        color_discrete_sequence=px.colors.sequential.Blues[1:],
    )

    fig_trx_type.update_layout(
        legend_title='SDK Version'  # Título de la leyenda
    )

    fig_trx_type.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.5, title=''),
        xaxis=dict(showgrid=False, title=''),
        plot_bgcolor='white',
        height=200,
        width=330,
        autosize=False,
        bargap=0.2,
        font={"family": "Raleway", "size": 10},
        hovermode="closest",
        margin={
            "r": 10,
            "t": 0,
            "b": 0,
            "l": 10,
        },
        legend={
            "orientation": "v",
            "yanchor": "top",
        },
        showlegend=True,
        title="",
    )

    return html.Div([
        html.Div([
            html.H6("Volumetry", className="subtitle padded"),
            html.Table(make_dash_table(df_trx_summary)),
        ], className="six columns", style={'padding-right': '30px'}),
        html.Div([
            html.H6("Detection Mode", className="subtitle padded"),
            dcc.Graph(
                id='transaction-type',
                figure=fig_trx_type,
            )
        ], className="six columns"),
    ], className="row_graphics row")


def add_pattern_usage(df_weekday_usage):
    # Create Graph for weekday usage
    fig_weekday_usage = px.bar(
        df_weekday_usage,
        x='Weekday',
        y='Total',
        color='Daytime',
        color_discrete_sequence=px.colors.qualitative.Pastel2,
        category_orders={"Weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]})

    fig_weekday_usage.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.5, title=''),
        xaxis=dict(showgrid=False, title=''),
        plot_bgcolor='white',
        autosize=True,
        bargap=0.2,
        font={"family": "Raleway", "size": 10},
        hovermode="closest",
        margin={
            "r": 10,
            "t": 0,
            "b": 0,
            "l": 10,
        },
        height=400,
        width=700,
        legend={
            "orientation": "v",
            "yanchor": "top",
        },
        showlegend=True,
        title="",
    )

    return html.Div([
        html.Div([
            html.H6("Weekday usage", className="subtitle padded"),
            dcc.Graph(
                id='weekday-usage',
                figure=fig_weekday_usage,
            )
        ], className="twelve columns"),
    ], className="row_graphics row")


def add_trx_over_time(df_trx_action_spoof_over_time):
    df_trx_over_time = df_trx_action_spoof_over_time.groupby(['Date', 'Action'])['Transactions'].sum().reset_index()

    # Figure for transaction over time
    fig_action_over_time = px.line(df_trx_over_time,
                                   x='Date', y='Transactions', color='Action',
                                   color_discrete_sequence=px.colors.qualitative.Pastel2)
    # color_discrete_sequence=px.colors.sequential.Bluered)

    fig_action_over_time.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.5, title=''),
        xaxis=dict(showgrid=False, title=''),
        plot_bgcolor='white',
        autosize=True,
        bargap=0.2,
        font={"family": "Raleway", "size": 10},
        hovermode="closest",
        margin={
            "r": 10,
            "t": 0,
            "b": 0,
            "l": 10,
        },
        height=400,
        width=700,
        legend={
            "orientation": "v",
            "yanchor": "top",
        },
        showlegend=True,
        title="",
    )

    # SDK usage
    df_sdk_over_time = df_trx_action_spoof_over_time.groupby(['Date', 'SdkVersion'])['Transactions'].sum().reset_index()

    # Figure for transaction over time
    fig_sdk_over_time = px.line(df_sdk_over_time,
                                x='Date', y='Transactions', color='SdkVersion',
                                color_discrete_sequence=px.colors.qualitative.Pastel2)

    fig_sdk_over_time.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.5, title=''),
        xaxis=dict(showgrid=False, title=''),
        plot_bgcolor='white',
        autosize=True,
        bargap=0.2,
        font={"family": "Raleway", "size": 10},
        hovermode="closest",
        margin={
            "r": 40,
            "t": 0,
            "b": 0,
            "l": 40,
        },
        height=400,
        width=700,
        legend={
            "orientation": "v",
            "yanchor": "top",
        },
        showlegend=True,
        title="",
    )

    return html.Div([
        html.Div([
            html.H6("Transactions done per day", className="subtitle padded"),
            dcc.Graph(
                id='action-over-time',
                figure=fig_action_over_time,
            ),
            html.Br(),
            html.Br(),
            html.Br(),
        ], className="twelve columns"),

        html.Br(),
        html.H6("2 of 3", style={'textAlign': 'center'}),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div([
            html.H6("SDK", className="subtitle padded"),
            dcc.Graph(
                id='sdk-over-time',
                figure=fig_sdk_over_time,
            )
        ], className="twelve columns"),
    ], className="row_graphics row")


def add_liveness_over_time(df_trx_action_spoof_over_time):
    df_spoof_over_time = df_trx_action_spoof_over_time.groupby(['Date', 'Spoof'])['Transactions'].sum().reset_index()
    df_spoof_over_time.loc[df_spoof_over_time['Spoof'] == 'N', 'Spoof'] = 'Legitimate'
    df_spoof_over_time.loc[df_spoof_over_time['Spoof'] == 'Y', 'Spoof'] = 'Spoof'

    df_spoof_percentage = df_spoof_over_time.pivot(index='Date', columns='Spoof',
                                                   values='Transactions').reset_index()

    columns_to_check = ['Spoof', 'Legitimate']
    if all(column in df_spoof_percentage.columns for column in columns_to_check):
        df_spoof_percentage['SPOOF_LEG_PER'] = (df_spoof_percentage['Spoof'] / df_spoof_percentage['Legitimate']) * 100
    else:
        df_spoof_percentage['SPOOF_LEG_PER'] = 0

    df_spoof_over_time = df_spoof_over_time.merge(df_spoof_percentage[['Date', 'SPOOF_LEG_PER']], on='Date')

    # Figure for liveness transaction over time
    fig_spoof_over_time = px.line(df_spoof_over_time,
                                  x='Date', y='Transactions', color='Spoof',
                                  color_discrete_sequence=px.colors.qualitative.Pastel2)

    fig_spoof_over_time.add_trace(go.Scatter(x=df_spoof_over_time['Date'], y=df_spoof_over_time['SPOOF_LEG_PER'],
                                             mode='lines', name='% of spoofs', line=dict(color='grey', dash='dot',
                                                                                         width=1.5),
                                             yaxis='y2'))

    fig_spoof_over_time.update_layout(
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.5, title='Transactions', side='left'),
        yaxis2=dict(showgrid=False, title='%', side='right', overlaying='y', range=[0, 100]),
        xaxis=dict(showgrid=False, title=''),
        plot_bgcolor='white',
        autosize=True,
        bargap=0.2,
        font={"family": "Raleway", "size": 10},
        hovermode="closest",
        margin={
            "r": 0,
            "t": 0,
            "b": 0,
            "l": 0,
        },
        height=400,
        width=700,
        legend={
            "orientation": "v",
            "yanchor": "top",
        },
        showlegend=True,
        title="",
    )

    return html.Div([
        html.Div([
            html.H6("Liveness classification per day", className="subtitle padded"),
            dcc.Graph(
                id='spoof-over-time',
                figure=fig_spoof_over_time,
            )
        ], className="twelve columns"),
    ], className="row_graphics row")


# App design
def create_layout(app, license_id, package_id, start_date, end_date,
                  df_trx_summary, df_detection_modes, df_agg_trx_weekdays, df_agg_trx_over_time):
    return html.Div([
        Header(app, license_id, package_id, start_date, end_date),
        add_separator("SUMMARY"),
        add_summary_data(df_trx_summary, df_detection_modes),
        add_separator("CUSTOMER USAGE"),
        add_pattern_usage(df_agg_trx_weekdays),
        html.H6("1 of 3", style={'textAlign': 'center'}),
        html.Br(),
        html.Br(),
        add_separator("LIVENESS"),
        add_liveness_over_time(df_agg_trx_over_time),
        add_separator("PRODUCT USAGE"),
        add_trx_over_time(df_agg_trx_over_time),
        html.Br(),
        html.H6("3 of 3", style={'textAlign': 'center'}),

    ], className="page")
