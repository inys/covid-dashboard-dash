import yaml
import requests
import os
import time

import pandas as pd
from pandas.core.frame import DataFrame
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import updateData

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# ------------------------------------------------------------------------------
# Update Data
updateData.updateData()

# ------------------------------------------------------------------------------
# Load Austria Data
austria_tests_pos = pd.read_table('data/austria/covidFaelle.csv', sep=';')

austria_bundeslands = austria_tests_pos[['Bundesland', 'BundeslandID']].drop_duplicates()

austria_hosp_total = pd.read_table('data/austria/covidFallzahlen.csv', sep=';')

# ------------------------------------------------------------------------------
# Load France Data
france_depts = pd.read_table('cache/depts2018.txt')

france_hosp_total = pd.read_csv("data/france/hospTotal.csv", sep=';')
france_hosp_total = france_hosp_total[france_hosp_total['sexe'] == 0]

france_tests_pos = pd.read_csv("data/france/testsDep.csv", sep=';')

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Covid-19 in Austria', href='/austria'),
    html.Br(),
    dcc.Link('Covid-19 in France', href='/france'),
])

austria_layout = html.Div([
    html.H1("Covid-19 in Austria", style={'text-align': 'center'}),

    dcc.Dropdown(id="select-austria-land",
        options=austria_bundeslands.rename(columns={'Bundesland': 'label', 'BundeslandID': 'value'}).to_dict('records'),
        multi=False,
        value='2',
        style={'width': "40%"}
        ),

    html.Div(id='austria-output-container', children=[]),
    html.Br(),

    dcc.Graph(id='austria-hosp-total-graph', figure={}),

    html.Br(),

    dcc.Graph(id='austria-tests-pos-graph', figure={}),

    html.Br(),

    dcc.Graph(id='austria-tests-pos-rolling-graph', figure={}),
])

france_layout = html.Div([
    html.H1("Covid-19 in France", style={'text-align': 'center'}),

    dcc.Dropdown(id="select-france-departement",
        options=france_depts.loc[:, ('NCCENR','DEP')].rename(columns={'NCCENR': 'label', 'DEP': 'value'}).to_dict('records'),
        multi=False,
        value='54',
        style={'width': "40%"}
        ),

    html.Div(id='france-output-container', children=[]),

    html.Br(),

    dcc.Graph(id='france-hosp-total-graph', figure={}),

    html.Br(),

    dcc.Graph(id='france-tests-pos-graph', figure={}),

    html.Br(),

    dcc.Graph(id='france-tests-pos-rolling-graph', figure={}),
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback([
        Output('austria-output-container', 'children'),
        Output('austria-hosp-total-graph', 'figure'),
        Output('austria-tests-pos-graph', 'figure'),
        Output('austria-tests-pos-rolling-graph', 'figure')
    ],
    [Input('select-austria-land', 'value')]
)
def update_austria(option_slctd):
    container = "The Bundesland chosen by user was: {}".format(option_slctd)

    austria_hosp_total_land = austria_hosp_total.copy()
    austria_hosp_total_land = austria_hosp_total_land[austria_hosp_total_land['BundeslandID'] == option_slctd]

    fig_austria_hosp_total_land = px.line(
        data_frame=austria_hosp_total_land,
        x='Meldedat',
        y='FZHosp',
        title='Hospitalization per day'
    )
    fig_austria_hosp_total_land.update_layout(
        xaxis_title="Day",
        yaxis_title="Hospitalizations", 
    )

    austria_tests_pos_land = austria_tests_pos.copy()
    austria_tests_pos_land = austria_tests_pos_land[austria_tests_pos_land['BundeslandID'] == option_slctd]
    austria_tests_pos_land.loc[:, ('rolling_P')] = austria_tests_pos_land['AnzahlFaelle'].rolling(7).sum()
    austria_tests_pos_land.loc[:, ('rolling_PP')] = austria_tests_pos_land['rolling_P'] * 100000 / austria_tests_pos_land['AnzEinwohner']

    fig_austria_tests_pos_land = px.line(
        data_frame=austria_tests_pos_land,
        x='Time',
        y='AnzahlFaelle',
        title='Positive tests per day'
    )
    fig_austria_tests_pos_land.update_layout(
        xaxis_title="Day",
        yaxis_title="Positive tests" 
    )

    fig_austria_tests_pos_rolling_land = px.line(
        data_frame=austria_tests_pos_land,
        x='Time',
        y='rolling_PP',
        title='Positive tests per rolling week',
    )
    fig_austria_tests_pos_rolling_land.update_layout(
        xaxis_title="Rolling week",
        yaxis_title="Positive tests" 
    )

    return container, fig_austria_hosp_total_land, fig_austria_tests_pos_land, fig_austria_tests_pos_rolling_land


@app.callback([
    Output('france-output-container', 'children'),
    Output('france-hosp-total-graph', 'figure'),
    Output('france-tests-pos-graph', 'figure'),
    Output('france-tests-pos-rolling-graph','figure')],
    [Input('select-france-departement', 'value')]
)
def update_france(option_slctd):
    container = "The departement chosen by user was: {}".format(option_slctd)

    france_hosp_total_dep = france_hosp_total.copy()
    france_hosp_total_dep = france_hosp_total_dep[france_hosp_total_dep['dep'] == option_slctd]

    fig_france_hosp_total_dep = px.line(
        data_frame=france_hosp_total_dep,
        x='jour',
        y='hosp',
        title='Hospitalization per day'
    )
    fig_france_hosp_total_dep.update_layout(
        xaxis_title="Day",
        yaxis_title="Hospitalizations", 
    )

    france_tests_pos_dep = france_tests_pos.copy()
    france_tests_pos_dep = france_tests_pos_dep[france_tests_pos_dep['dep'] == option_slctd]
    france_tests_pos_dep.loc[:, ('rolling_P')] = france_tests_pos_dep['P'].rolling(7).sum()
    france_tests_pos_dep.loc[:, ('rolling_PP')] = france_tests_pos_dep['rolling_P'] * 100000 / france_tests_pos_dep['pop']

    fig_france_tests_pos_dep = px.line(
        data_frame=france_tests_pos_dep,
        x='jour',
        y='P',
        title='Positive tests per day',
    )
    fig_france_tests_pos_dep.update_layout(
        xaxis_title="Day",
        yaxis_title="Positive tests" 
    )

    fig_france_tests_pos_rolling_dep = px.line(
        data_frame=france_tests_pos_dep,
        x='jour',
        y='rolling_PP',
        title='Positive tests per rolling week',
    )
    fig_france_tests_pos_rolling_dep.update_layout(
        xaxis_title="Rolling week",
        yaxis_title="Positive tests" 
    )

    return container, fig_france_hosp_total_dep, fig_france_tests_pos_dep, fig_france_tests_pos_rolling_dep

# ------------------------------------------------------------------------------
# Routing
@app.callback(Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/austria':
        return austria_layout
    elif pathname == '/france':
        return france_layout
    else:
        return index_page

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

