import dash
from dash.dependencies import Output, Input, State
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
import random
import numpy as np

#THINGS TO DO
#1. Make reset button actually reset the grpah back to 0
#2. Change random variables to generate a random array

# global array to store ['pow'] values
power = []

# x-axis of graph of
time = deque(maxlen=100)
time.append(0)
time2 = deque(maxlen=100)
time2.append(0)

# AF3 Data Values
thetaval = deque(maxlen=100)
thetaval.append(0)
alphaval = deque(maxlen=100)
alphaval.append(0)
lowval = deque(maxlen=100)
lowval.append(0)
highval = deque(maxlen=100)
highval.append(0)
engagementval = deque(maxlen=100)
engagementval.append(0)
fatigueval = deque(maxlen=100)
fatigueval.append(0)

# AF4 Data Values
thetaval2 = deque(maxlen=100)
thetaval2.append(0)
alphaval2 = deque(maxlen=100)
alphaval2.append(0)
lowval2 = deque(maxlen=100)
lowval2.append(0)
highval2 = deque(maxlen=100)
highval2.append(0)
engagementval2 = deque(maxlen=100)
engagementval2.append(0)
fatigueval2 = deque(maxlen=100)
fatigueval2.append(0)

external_stylesheets = [{'href': "https://fonts.googleapis.com/css?family=Roboto:300&display=swap",
                         'rel': "stylesheet"},
                        ]

async def authorize(cortex):
    '''
    await cortex.inspectApi()
    
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
    '''
    global power
    power = np.random.randint(99, size=24)
    #power = await cortex.subscribe(['pow'])
    # put pow stream into power variable
    # power = ['pow']
    # print pow list


def cortexService():
    cortex = Cortex('./cortex_creds')
    asyncio.run(authorize(cortex))
    # cortex.close()


cortexService()


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
        id="header", children='EMOTIV PERFORMANCE METRICS'))),

    html.Div(id='line-graph', children=[html.Div(id='stats-top', children=(html.H4(id='intro', children='Press the Start Recording Button below to retrieve band power.'),html.Button('Start Recording', id='start'), html.Button('Reset', id='reset'))),
                                        dcc.Graph(
                                            id='live-pow-line-af3', animate=True, style= { 'height': '47.5vh'}),
                                        dcc.Graph(
                                            id='live-pow-line-af4', animate=True, style= { 'height': '47.4vh'}),
                                        html.Div(id='stats', children=(html.H3(className='stats-text', children='Engagement'),
                                                                       html.H3(className='stats-text', children='Fatigue'))),
                                        dcc.Interval(
        id='graph-update', interval=1*1000, n_intervals=0, disabled=True 
    )]
    )
]
)

@app.callback(
    Output('start', 'children'),
    [Input('start', 'n_clicks')]
)
def button_text(n):
    if n == None:
        return 'Start Recording'
    if n != None and n % 2 == 0:
        return 'Start Recording'
    elif n != None and n % 2 != 0:
        return 'Stop Recording'

@app.callback(
    Output('graph-update', 'disabled'),
    [Input('start', 'n_clicks')],
    [State('graph-update', 'disabled')],
)
def toggle_interval(n, disabled):
    if n:
        return not disabled
    return disabled

@app.callback(
    Output('live-pow-line-af3', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def updateGraph(n):

    data = []

    global time
    time.append(time[-1]+1)
    # retreiving / calculating band power values
    theta = power[0]
    alpha = power[1]
    low_beta = power[2]
    high_beta = power[3]
    engagement = (high_beta / alpha + theta)
    fatigue = (theta + alpha / (low_beta))

    thetaval.append(theta)
    alphaval.append(alpha)
    lowval.append(low_beta)
    highval.append(high_beta)
    engagementval.append(engagement)
    fatigueval.append(fatigue)

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
            'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power for channel AF3',
                           xaxis=dict(range=[min(time), max(time)], automargin=True, title=dict(
                               text='Time', font=dict(size=30))),
                           yaxis=dict(
                               range=[0, 100], title=dict(text='Band Power', font=dict(size=30)), automargin=True),
                           margin=dict(l=45, t=50))}


@app.callback(Output('live-pow-line-af4', 'figure'),
              [Input('start', 'n_clicks'), Input('graph-update', 'n_intervals')])
def graphUpdate2(click, n):

    data = []
    
    #generate random numbers to be used for the graphs
    global power
    power = np.random.randint(1, 100, size=24)
    
    global time2
    time2.append(time[-1]+1)
    # retreiving / calculating band power values
    theta = power[20]
    alpha = power[21]
    low_beta = power[22]
    high_beta = power[23]
    engagement = (high_beta / alpha + theta)
    fatigue = (theta + alpha / (low_beta))

    thetaval2.append(theta)
    alphaval2.append(alpha)
    lowval2.append(low_beta)
    highval2.append(high_beta)
    engagementval2.append(engagement)
    fatigueval2.append(fatigue)

    # create each individual line for the data values
    data.append(go.Scatter(x=list(time), y=list(thetaval2),
                           name='Theta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(alphaval2),
                           name='Alpha', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(lowval2),
                           name='Low beta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(highval2),
                           name='High Beta', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(engagementval2),
                           name='Engagement', mode='lines+markers'))
    data.append(go.Scatter(x=list(time), y=list(fatigueval2),
                           name='Fatigue', mode='lines+markers'))

    return {'data': data,
            'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power for channel AF4',
                           xaxis=dict(range=[min(time2), max(time2)], automargin=True, title=dict(
                               text='Time', font=dict(size=30))),
                           yaxis=dict(
                               range=[0, 100],title=dict(text='Band Power', font=dict(size=30)), automargin=True),
                           margin=dict(l=45, t=50))}


if __name__ == '__main__':
    app.run_server(debug=True)
