import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import asyncio
from lib.cortex import Cortex
from flask import Flask, request, make_response
import operator

# global array to store ['pow'] values
power = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
         16, 17, 18, 19, 10, 20, 1, 2, 4, 5, 6, 1, 46, 7, 2, 3, 6]

# x-axis of graph of
time = deque(maxlen=20)
time.append(1)

thetaval = deque(maxlen=10)
alphaval = deque(maxlen=10)
lowval = deque(maxlen=10)
highval = deque(maxlen=10)
engagementval = deque(maxlen=10)
fatigueval = deque(maxlen=10)

external_stylesheets = [{'href': "https://fonts.googleapis.com/css?family=Roboto:300&display=swap",
                         'rel': "stylesheet"},
                        ]


async def authorize(cortex):
    # await cortex.inspectApi()
    print("** USER LOGIN **")
    await cortex.get_user_login()
    print("** GET CORTEX INFO **")
    await cortex.get_cortex_info()
    print("** HAS ACCESS RIGHT **")
    await cortex.has_access_right()
    print("** REQUEST ACCESS **")
    await cortex.request_access()
    print("** AUTHORIZE **")
    await cortex.authorize()
    print("** GET LICENSE INFO **")
    await cortex.get_license_info()
    print("** QUERY HEADSETS **")
    await cortex.query_headsets()
    if len(cortex.headsets) > 0:
        print("** CREATE SESSION **")
        await cortex.create_session(activate=True,
                                    headset_id=cortex.headsets[0])
        print("** CREATE RECORD **")
        await cortex.create_record(title="test record 1")
        print("** SUBSCRIBE TO POW **")
        await cortex.subscribe(['pow'])
        # put pow stream into power variable
        power = ['pow']
        print(power)
        # print pow list

        while cortex.packet_count < 10:
            await cortex.get_data()
        await cortex.inject_marker(label='halfway', value=1,
                                   time=cortex.to_epoch())
        while cortex.packet_count < 20:
            await cortex.get_data()
        await cortex.close_session()


def cortexService():
    cortex = Cortex('./cortex_creds')
    asyncio.run(authorize(cortex))
    cortex.close()


data_set = {
    'band-power': {
        'data': [

        ]
    },
    'perf-metrics': {
        'data': [

        ]
    }
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='container', children=[

    html.Div(id="head", children=(html.H2(
        id="header", children='EMOTIV PERFORMANCE METRICS'),
        dcc.Dropdown(id='menu',
                     options=[
                         {'label': 'Channel: AF3',
                          'value': 'AF3'},
                         {'label': 'Channel: AF4',
                          'value': 'AF4'},
                     ],
                     value='AF3'
                     ))),

    html.Div(id='line-graph', children=[html.Div(id='stats-top', children=(html.H3(className='eeg-text', children='EEG Info Here '))),
                                        dcc.Graph(id='live-pow-line'),
                                        html.Div(id='stats', children=(html.H3(className='stats-text', children='Engagement '),
                                                                       html.H3(className='stats-text', children='Fatigue'))),
                                        dcc.Interval(
        id='graph-update', interval=1*1000, n_intervals=0
    )
    ]
    )
]
)


@app.callback(
    Output('live-pow-line', 'figure'),
    [Input('menu', 'value'), Input('graph-update', 'n_intervals')]
)
def update_graphChannel(channel, n):

    # TO DO
    # update data when channel is changed and output updated graph based on ['pow'] values (beta, alpha, theta, etc.)

    arr = []

    if channel == 'AF3':
        theta = power[0]
        alpha = power[1]
        low_beta = power[2]
        high_beta = power[3]
        engagement = (high_beta / alpha + theta)
        fatigue = (theta + alpha / (low_beta))
    elif channel == 'AF4':
        theta = power[20]
        alpha = power[21]
        low_beta = power[22]
        high_beta = power[23]
        engagement = (high_beta / alpha + theta)
        fatigue = (theta + alpha / (low_beta))

    arr = [theta, alpha, low_beta, high_beta, engagement, fatigue]

    global time
    time.append(time[-1]+1)

    thetaval.append(theta)
    alphaval.append(alpha)
    lowval.append(low_beta)
    highval.append(high_beta)
    engagementval.append(engagement)
    fatigueval.append(fatigue)

    data = []

    # create each individual line for the data values
    data.append(go.Scatter(x=list(time), y=list(thetaval),
                           name='Theta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(alphaval),
                           name='Alpha', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(lowval),
                           name='Low beta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(highval),
                           name='High Beta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(engagementval),
                           name='Engagement', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(fatigueval),
                           name='Fatigue', mode='lines+markers'))

    return {'data': data,
            'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power for channel ' + channel,
                           xaxis=dict(range=[min(time), max(time)], automargin=True, title=dict(
                               text='Time', font=dict(size=30))),
                           yaxis=dict(
                               range=[min(n.y for n in data), max(n.y for n in data)]),
                           margin=dict(l=45, t=50, b=40), )}


if __name__ == '__main__':
    app.run_server(debug=True)
