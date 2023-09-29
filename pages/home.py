import json
import os
import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([  # This is the container div
        html.H2('What is this app?', style={'color': 'white', 'padding': '10px 0'}),
        html.Div(
            'This app is a hub for all of your spreadsheet automations. It allows you to create new automations, as well as view and run existing automations.',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        html.Div(
            'To see a demo of this app in use, view the embedded video below',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        html.Iframe(
            src="https://www.youtube.com/embed/7qHMXu99d88",
            style={"height": "500px", "width": "100%", "border": "none", "border-radius": "10px", "margin": "20px 0"}
        ),
        html.H2('How do I use this app?', style={'color': 'white', 'padding': '10px 0'}),
        html.Div(
            'To use this app, you need to create a new automation. To do this, click the "Create New Automation" button below.',
            style={'color': 'white', 'padding': '10px 0'}
        ),
        # make a link to the new automation page
        html.A(
            'Create New Automation',
            href='/new-automation',
            style={
                'background-color': '#5A67D8',
                'color': 'white',
                'padding': '10px 15px',
                'border-radius': '10px',
                'text-decoration': 'none',
                'display': 'inline-block',
                'margin': '10px 0'
            }
        ),
        html.H2('See existing automations:', style={'color': 'white', 'padding': '10px 0'}),
        # A list of all the automations in the automations folder
        html.Ul(
            [
                html.Li(
                    [
                        html.A(
                            json.loads(open('automations/' + file, 'r').read())['automation_name'],
                            href=f"/automation?automation_name={json.loads(open('automations/' + file, 'r').read())['automation_name']}",
                            style={'color': '#5A67D8', 'text-decoration': 'none'}
                        )
                    ],
                    style={'color': 'white', 'padding': '5px 0'}
                ) for file in os.listdir('automations') if file.endswith('.json')
            ],
            style={'list-style-type': 'none', 'padding': '0'}
        )
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'background-color': '#2D3748', 'height': '100%', 'color': 'white', 'padding': '20px 0'})

