from dash import Input, Output, html, dcc, Dash, dash_table  # pip install dash
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import pandas as pd  # pip install pandas
from dash import dash_table
import plotly_express as px  # pip install plotly_express
import datetime as dt
from dash import dcc
import numpy as np
import dash_bootstrap_components as dbc

df = pd.read_csv("Sample_Data.csv")

df['Release_Date'] = df['Release_Date'].apply(
    lambda x: dt.datetime.strptime(x, '%Y-%d-%m').date())

app = Dash(external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([dbc.Row(
    dbc.Col(html.H3('Software Comparison Tool',
                    style={'text-align': 'center', 'margin': '5px'}), style={'padding': '5px'}),
    style={'background-color': '#1a75ff', 'margin-left': '1px', 'margin-right': '1px', 'margin-bottom': '10px'}),
    dbc.Row([dbc.Col(dcc.Dropdown(
        id="applicationdropdown",
        options=[
            {"label": x, "value": x}
            for x in df.sort_values("Application")["Application"].unique()
        ],
        value="application A",
        multi=False,
        clearable=False,
    )),
        dbc.Col(dcc.Dropdown(
            id="serverdropdown",
            options=[],
            multi=False,
            clearable=False,
            placeholder='Select Server'
        )),
        dbc.Col(dcc.Dropdown(
            id="benchmarkdropdown",
            multi=False,
            clearable=False,
            placeholder='Select Benchmark'
        )),
        dbc.Col(dcc.Dropdown(
            id="releasedatedropdown",
            multi=False,
            clearable=False,
            placeholder='Select Release Date'
        ))]
    ),
    dbc.Row([dbc.Col([html.H4("Status1 Results", style={'text-align': 'center', }), dcc.Graph(id="piechart1")],
                     style={'width': '50%'}),
             dbc.Col([html.H4("Status2 Results", style={'text-align': 'center', }), dcc.Graph(id="piechart2")],
                     style={'width': '50%'})], style={'margin-top': '20px'}),
    dbc.Row(
        dbc.Col(html.H3('Software Version Differences Table',
                        style={'text-align': 'center', 'margin': '5px'}), style={'padding': '5px'}),
        style={'background-color': '#1a75ff', 'margin-left': '1px', 'margin-right': '1px', 'margin-bottom': '10px',
               'margin-top': '20px'}),
    dbc.Row(dbc.Col(dash_table.DataTable(
        id='result-table',
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'border': '1px solid grey',
        },
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Status1',
                },
                'color': 'red'
            },
            {
                'if': {
                    'column_id': 'Status2',
                },
                'color': 'red'
            }
        ],
        page_size=10,
        style_cell={'textAlign': 'center', 'background-color': 'white', 'color': 'black', 'height': 'auto', },
        style_header={'textAlign': 'center', 'background-color': 'black', "font-size": "1vw", 'color': 'white'},
        tooltip_delay=0,
        tooltip_duration=None, page_action='native'
    ))),
    dbc.Row(
        dbc.Col(html.H3('Benchmark Performance Overtime',
                        style={'text-align': 'center', 'margin': '5px'}), style={'padding': '5px'}),
        style={'background-color': '#1a75ff', 'margin-left': '1px', 'margin-right': '1px', 'margin-bottom': '10px',
               'margin-top': '20px'}),
    dbc.Row(dbc.Col(dcc.Graph(id="line-chart")))

], style={'padding': '15px', 'background-color': '#e0ebeb'}, fluid=True)


@app.callback(Output(component_id="serverdropdown", component_property="options"),
              [Input(component_id="applicationdropdown", component_property="value")])
def generate_server_dropdown(application: str):
    if not application:
        return []
    server_list = df[df["Application"] ==
                     application]["Server"].unique().tolist()
    return [{"label": server_name, "value": server_name}
            for server_name in server_list]


@app.callback(Output(component_id="benchmarkdropdown", component_property="options"),
              [Input(component_id="applicationdropdown", component_property="value"),
               Input(component_id="serverdropdown", component_property="value")])
def generate_benchmark_dropdown(application: str, server: str):
    if not application or not server:
        return []

    benchmark_list = df[(df["Application"] == application) & (
            df["Server"] == server)]["Benchmark"].unique().tolist()
    return [{"label": benchmark, "value": benchmark}
            for benchmark in benchmark_list]


@app.callback(Output(component_id="releasedatedropdown", component_property="options"),
              [Input(component_id="applicationdropdown", component_property="value"),
               Input(component_id="serverdropdown", component_property="value"),
               Input(component_id="benchmarkdropdown", component_property="value")])
def generate_benchmark_dropdown(application: str, server: str, benchmark: str):
    if not application or not server or not benchmark:
        return []

    date_list = df[(df["Application"] == application) & (
            df["Server"] == server) & (
                           df["Benchmark"] == benchmark)]["Release_Date"].unique().tolist()
    return [{"label": date, "value": date}
            for date in date_list]


@app.callback(
    [Output(component_id="piechart1", component_property="figure"),
     Output(component_id="piechart2", component_property="figure")],
    [Input(component_id="applicationdropdown", component_property="value"),
     Input(component_id="serverdropdown", component_property="value"),
     Input(component_id="benchmarkdropdown", component_property="value"),
     Input(component_id="releasedatedropdown", component_property="value")]
)
def update_graphs(applicationdropdown, serverdropdown, benchmarkdropdown, releasedatedropdown):
    if (
            applicationdropdown is None
            or serverdropdown is None
            or benchmarkdropdown is None
            or releasedatedropdown is None
    ):
        raise PreventUpdate

    releasedatedropdown = dt.datetime.strptime(
        releasedatedropdown, '%Y-%m-%d').date()

    filtered_df = df[(df.Application == applicationdropdown) & (df.Server == serverdropdown) & (
            df.Benchmark == benchmarkdropdown) & (df.Release_Date == releasedatedropdown)]

    version1_counts = filtered_df.Status1.value_counts().rename_axis(
        'unique_values').reset_index(name='counts')
    version2_counts = filtered_df.Status2.value_counts().rename_axis(
        'unique_values').reset_index(name='counts')

    fig1 = px.pie(version1_counts, values='counts', names='unique_values', color='unique_values',
                  color_discrete_map={'Open': 'Red',
                                      'Not a Finding': 'Green',
                                      'Not Reviewed': 'Black',
                                      'Not Applicable': 'Grey'})

    fig2 = px.pie(version2_counts, values='counts', names='unique_values', color='unique_values',
                  color_discrete_map={'Open': 'Red',
                                      'Not a Finding': 'Green',
                                      'Not Reviewed': 'Black',
                                      'Not Applicable': 'Grey'})

    return fig1, fig2


@app.callback(
    [Output("result-table", "data"), Output('result-table', 'columns')],
    [Input(component_id="applicationdropdown", component_property="value")],
    [Input(component_id="serverdropdown", component_property="value")],
    [Input(component_id="benchmarkdropdown", component_property="value")],
    [Input(component_id="releasedatedropdown", component_property="value")],
)
def generate_result_table(application: str, server: str, benchmark: str, release_date: str):
    if not application or not server or not benchmark or not release_date:
        raise PreventUpdate
    release_date_obj = dt.datetime.strptime(
        release_date, '%Y-%m-%d').date()

    df_filterd = df[(df["Application"] == application) & (df["Server"] == server) & (
            df["Benchmark"] == benchmark) & (df["Release_Date"] == release_date_obj)]

    unmatch_data = df_filterd[df_filterd['T/F'] == False]
    unmatch_data.drop(['T/F', 'TRUE/FALSE'], axis=1, inplace=True)
    return unmatch_data.to_dict('Records'), [{'name': i, 'id': i} for i in unmatch_data.columns]


@app.callback(
    Output(component_id="line-chart", component_property="figure"),
    [Input(component_id="applicationdropdown", component_property="value")],
    [Input(component_id="serverdropdown", component_property="value")],
    [Input(component_id="benchmarkdropdown", component_property="value")],
)
def generate_line_chart(application: str, server: str, benchmark: str):
    if not application or not server or not benchmark:
        raise PreventUpdate

    df_filterd = df[(df["Application"] == application) & (df["Server"] == server) & (
            df["Benchmark"] == benchmark)]

    unique_dates = df_filterd["Release_Date"].unique()
    unique_dates = np.sort(unique_dates).tolist()

    true_arr = []
    false_arr = []

    for release_date in unique_dates:
        df_date_filtered = df_filterd[df_filterd["Release_Date"] == release_date]
        true_arr.append(df_date_filtered[df_date_filtered['T/F'] == True]['T/F'].count())
        false_arr.append(df_date_filtered[df_date_filtered['T/F'] == False]['T/F'].count())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=unique_dates, y=true_arr,
                             mode='lines',
                             name='True'))
    fig.add_trace(go.Scatter(x=unique_dates, y=false_arr,
                             mode='lines',
                             name='False'))
    return fig


if __name__ == '__main__':
    app.run_server()
