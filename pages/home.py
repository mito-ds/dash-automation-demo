import json
import os
import dash
from dash import html, Output, Input, callback, dcc

from utils import get_all_automations

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([  # This is the container div
        html.H2('What is this app?', style={'color': 'white'}),
        html.Div(
            'This app is a demo of the Mito for Dash component. Use this Dash app to create and run Python automations, all while just editing a spreadsheet..',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        html.Div(
            'To see a demo of this application in action, watch the video below: (coming soon)',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        html.Iframe(
            src="https://www.youtube.com/embed/7qHMXu99d88",
            style={"height": "500px", "width": "100%", "border": "none", "border-radius": "10px", "margin": "20px 0"}
        ),
        html.H2('Re-run Existing Automations' if len(list(get_all_automations(1))) > 0 else '', style={'color': 'white', 'padding': '10px 0'}),
        # A list of all the automations in the automations folder
        html.Div(id='automation-list'),
        html.H2('Create A New Automation', style={'color': 'white', 'padding': '10px 0'}),
        html.Div(
            'To create a new automation, click the "Create New Automation" button below.',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        # make a link to the new automation page
        html.A(
            'Create New Automation',
            href='/new-automation',
            style={
                'background-color': '#9d6cff',
                'color': 'white',
                'padding': '10px 15px',
                'border-radius': '10px',
                'text-decoration': 'none',
                'display': 'inline-block',
                'margin': '10px 0'
            }
        ),
        
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'}),  # This style ensures the content is centered and has a max width
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
    )
], style={'height': '100%', 'color': 'white'})


# Whenever this page is loaded, we want to load the automation list from the automations folder
@callback(
    Output('automation-list', 'children'),
    Input('interval-component', 'n_intervals')
)
def load_automations(n):
    return html.Ul(
        [
            html.Li(
                [
                    html.A([
                        html.H3(automation['automation_name'], style={'color': 'white', 'margin-top': '0px', 'margin-bottom': '5px'}),
                        html.Div('Description: ' + automation['automation_description'], style={'color': 'white', 'margin': '0'})
                    ], href=f"/automation?automation_name={automation['automation_name']}")
                ],
                style={'color': 'white', 'padding': '10px', 'background-color': '#363637', 'border-radius': '10px', 'margin': '10px 0'}
            ) for automation in get_all_automations(5)
        ],
        style={'list-style-type': 'none', 'padding': '0'}
    )