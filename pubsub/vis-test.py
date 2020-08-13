import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    return html.H1('The time is: ' + str(datetime.datetime.now()))

app.layout = html.Div(
    html.Div([
        html.H4(id='live-date'),
        dcc.Interval(
            id='interval-component',
            interval=1*100, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-date', 'children'),[Input('interval-component', 'n_intervals')])
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.H1('The time is: ' + str(datetime.datetime.now()))
    ]


if __name__ == '__main__':
    app.run_server(debug=True)