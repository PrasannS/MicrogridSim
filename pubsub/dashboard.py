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
        html.H4(id='live-date'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-date', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global redis_connection
    global weather_cols
    style = {'padding': '5px', 'fontSize': '16px'}

    df = pd.DataFrame(json.loads(redis_connection.get('climate')), columns=weather_cols)
    print(df['Date'])
    print(df['Temperature'])

    temperature = px.line(df, x='Date', y='Temperature', title='Temperature')

    return [
        html.Div([
            dcc.Graph(figure=temperature)
        ])
    ]


if __name__ == '__main__':
    app.run_server(debug=True)