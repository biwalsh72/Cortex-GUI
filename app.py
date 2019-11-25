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

# global array to store ['pow'] values
power = []

# x-axis of graph of
time = deque(maxlen=10)
time.append(1)

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

    html.Div(id='stats', children=(html.H3(className='stats-text', children='Engagement '),
                                   html.H3(className='stats-text', children='Fatigue'), html.H4())),

    html.Div(id='line-graph', children=[dcc.Graph(id='live-pow-line'),
                                        dcc.Interval(
        id='graph-update', interval=1*1000, n_intervals=0
    )
    ]
    )
]
)


@app.callback(
    Output('live-pow-line', 'figure'),
    [Input('menu', 'value')]
)
def update_graphChannel(channel):
    return {'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power for channel ' + channel,
                           xaxis=dict(automargin=True, title=dict(
                               text='Time', font=dict(size=30))),
                           margin=dict(l=45, r=250, t=50, b=40), )}


'''
@app.callback(
    Output(component_id='live-pow-line', component_property='figure'),
    [Input(component_id='graph-update', component_property='interval')]
)
def updateGraph():
    val = 0
    global time
    time.append(time[-1]+1)
    val.append(power[-1]+1)

    data = go.Scatter(
        x=list(time),
        y=list(val),
        name='scatter',
        mode='lines+markers'
    )

    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(time), max(time)]),
                                                yaxis=dict(range=[min(val), max(val)]))}
'''

# run test function when server starts
# cortexService()

# Output pow data type onto dcc graph and update values


if __name__ == '__main__':
    app.run_server(debug=True)
