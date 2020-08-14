import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

import json

import pandas as pd
import numpy as np

import redis


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

market_prices = 0

weather_cols = ['Date','Year','Month','Day','Time','Temperature','Dew Point Temp','Rel Humidity','Wind Dir','Wind Spd','Visibility','Stn Press','Hmdx','Wind Chill','Weather']

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_connection = redis.Redis(connection_pool=pool)
pipe = redis_connection.pipeline()

app.layout = html.Div(
    html.Div([
        dcc.Interval(
                    id='interval-component',
                    interval=1*1000, # in milliseconds
                    n_intervals=0
                ),
        html.Div([

            html.H1("Climate Data"),
            html.Div([
                html.H4(id='live-stn-press'),
            ], className="one-third column"),
            html.Div([
                html.H4(id='live-weather'),
            ], className="two-thirds column")
        ]), 
        html.Div([
            html.Div([
            html.H4(id='live-temp'),
            
            ], className="one-half column"),
            html.Div([
                html.H4(id='live-hum'),
            ], className="one-half column")
        ]), 
        html.Div([
            html.Div([
            html.H4(id='live-visibility'),
            
            ], className="one-half column"),
            html.Div([
                html.H4(id='live-wind-dir'),
            ], className="one-half column")
        ]),
        html.Div([
            html.Div([
            html.H4(id='live-wind-spd'),
            
            ], className="one-half column"),
            html.Div([
                html.H4(id='live-dew'),
            ], className="one-half column")
        ]), 
        html.H1("Market Data"),
        html.Div([
            html.H4(id='market'),
        ]), 
        html.H1("Battery"),
        html.Div([
            html.H4(id='battery'),
        ]), 
        html.H1("Renewables"),
        html.Div([
            html.H4(id='renewables'),
        ]), 
    ],
    className="row"
    ),
)

@app.callback(Output('live-temp', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Temperature', title='Temperature')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('live-visibility', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Visibility', title='Visibility')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('live-wind-dir', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Wind Dir', title='Wind Dir')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]


@app.callback(Output('live-wind-spd', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Wind Spd', title='Wind Speed')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('live-weather', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Weather', title='Weather')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]


@app.callback(Output('live-dew', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Dew Point Temp', title='Dew Point Temp')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('live-stn-press', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Stn Press', title='Stn Press')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('live-hum', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)

    temperature = px.line(df, x='Date', y='Rel Humidity', title='Rel Humidity')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('market', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    arr = json.loads(redis_connection.get('market'))
    df = pd.DataFrame(arr, columns=['energy_price'])

    df['Date'] = range(0, len(arr))

    temperature = px.line(df, x='Date', y='energy_price', title='Energy Price')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]

@app.callback(Output('battery', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    arr = json.loads(redis_connection.get('battery'))
    df = pd.DataFrame(arr)

    battery = px.line(df, x='timestep', y='charged', title='Battery')

    return [
        html.Div([
            dcc.Graph(figure=battery)
        ])
    ]


@app.callback(Output('renewables', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    pv = json.loads(redis_connection.get('pv'))
    wind = json.loads(redis_connection.get('wind'))
    
    df = pd.DataFrame(pv, columns = ['pv'])
    df['timestep'] = range(0, len(pv))
    df['wind'] = wind

    pvplot = px.line(df, x='timestep', y='pv', title='Solar Power')
    windplot = px.line(df, x='timestep', y='wind', title='Wind')


    return [

        html.Div([
            html.Div([
            dcc.Graph(figure=pvplot),
            
            ], className="one-half column"),
            html.Div([
                dcc.Graph(figure=windplot),
            ], className="one-half column")
        ]), 
        html.Div([
            
        ])
    ]





if __name__ == '__main__':
    app.run_server(debug=True)