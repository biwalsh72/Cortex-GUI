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

external_stylesheets = [{'href': "https://fonts.googleapis.com/css?family=Roboto:300&display=swap",
                         'rel': "stylesheet"},
                        ]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='container', children=[

    html.Div(id="head", children=html.H2(id="header", children='EMOTIV PERFORMANCE METRICS')),


    #dcc.Graph(id='live-pow-line', animate=True),
    # dcc.Interval(
    #    id='graph-pow-update',
    #    interval=1000,
    #    n_intervals=0
    # ),

    html.Div(id='line-graph', children=dcc.Graph(id='live-pow-line', animate=True, figure={'layout': { 'title': 'Band Power', 'height': '45%'}})),

    html.Div(id='bar-graph', children=dcc.Graph(id='live-met-bar', animate=True, figure={'layout': {'title': 'Affective State', 'height': '45%', 'padding': 0}}))
]
)

# @app.callback(Output('live-pow-line', 'figure'),
#              [Input('graph-pow-update', 'n_intervals')])
# def update_graph_scatter(n):
# update with pow data type
'''
    X.append(X[-1]+1)
    Y.append(Y[-1]+Y[-1]*random.uniform(-0.1, 0.1))

    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                                yaxis=dict(range=[min(Y), max(Y)]),)}
'''


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
        power = ['pow']
        print(*power)
        # print pow array
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


# run test function when server starts
# cortexService()

# Output pow data type onto dcc graph and update values


if __name__ == '__main__':
    app.run_server(debug=True)
