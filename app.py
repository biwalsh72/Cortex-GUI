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

    html.Div(id="head", children=(html.H2(
        id="header", children='EMOTIV PERFORMANCE METRICS'), dcc.Dropdown(id='menu',
                                                                          options=[
                                                                              {'label': 'Channel: AF3',
                                                                                  'value': 'AF3'},
                                                                              {'label': 'Channel: AF4',
                                                                                  'value': 'AF4'},
                                                                          ],
                                                                          value='AF3'
                                                                          ))),

    # dcc.Interval(
    #    id='graph-pow-update',
    #    interval=1000,
    #    n_intervals=0
    # ),

    html.Div(id='stats', children=(html.H3(className='stats-text', children='Engagement '),
                                   html.H3(className='stats-text', children='Fatigue'), html.H4())),

    html.Div(id='line-graph', children=dcc.Graph(id='live-pow-line',
                                                 animate=True, figure={'data': [
                                                     {'x': [0, 2, 3], 'y':[
                                                         1, 2, 3], 'name':'Low Beta', 'type':'line'},
                                                     {'x': [1, 2, 8], 'y':[
                                                         1, 3, 4], 'name':'High Beta', 'type':'line'},
                                                     {'x': [2, 3, 5], 'y':[
                                                         1, 2, 3], 'name':'Alpha', 'type':'line'},
                                                     {'x': [1, 5, 6], 'y':[
                                                         1, 7, 9], 'name':'Theta', 'type':'line'},
                                                 ], 'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power',
                                                                   xaxis=dict(automargin=True, title=dict(
                                                                       text='Time', font=dict(size=30))),
                                                                   yaxis=dict(automargin=True, title=dict(
                                                                       text='AF3', font=dict(size=30))),
                                                                   margin=dict(l=45, r=250, t=50, b=40), )})),
]
)


@app.callback(
    Output(component_id='live-pow-line', component_property='figure'),
    [Input(component_id='menu', component_property='value')]
)
def update_graphChannel(channel):
    if channel == 'AF3':
        yaxiss = 'AF4'
    else:
        yaxiss = 'AF3'

    return {'data': [{'x': [0, 2, 3], 'y':[1, 2, 3], 'name':'Low Beta', 'type':'line'},
                                                     {'x': [1, 2, 8], 'y':[
                                                         1, 3, 4], 'name':'High Beta', 'type':'line'},
                                                     {'x': [2, 3, 5], 'y':[
                                                         1, 2, 3], 'name':'Alpha', 'type':'line'},
                                                     {'x': [1, 5, 6], 'y':[
                                                         1, 7, 9], 'name':'Theta', 'type':'line'},
                                                 ], 'layout': dict(plot_bgcolor='#ffffff', paper_bgcolor='#dddddd', autosize=True, title='Band Power',
                                                                   xaxis=dict(automargin=True, title=dict(
                                                                       text='Time', font=dict(size=30))),
                                                                   yaxis=dict(automargin=True, title=dict(
                                                                       text=yaxiss, font=dict(size=30))),
                                                                   margin=dict(l=45, r=250, t=50, b=40), )}



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
        power=['pow']
        print(*power)
        # print pow list

        while cortex.packet_count < 10:
            await cortex.get_data()
        await cortex.inject_marker(label='halfway', value=1,
                                   time=cortex.to_epoch())
        while cortex.packet_count < 20:
            await cortex.get_data()
        await cortex.close_session()


def cortexService():
    cortex=Cortex('./cortex_creds')
    asyncio.run(authorize(cortex))
    cortex.close()


# run test function when server starts
# cortexService()

# Output pow data type onto dcc graph and update values


if __name__ == '__main__':
    app.run_server(debug=True)
