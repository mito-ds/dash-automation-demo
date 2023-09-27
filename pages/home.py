import json
import os
import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H2('What is this app?'),
    html.Div('This app is a hub for all of your spreadsheet automations. It allows you to create new automations, as well as view and run existing automations.'),
    html.Div('To see a demo of this app in use, view the embeded video below'),
    html.Iframe(
        src="https://www.youtube.com/embed/7qHMXu99d88",
        style={"height": "500px", "width": "100%"}
    ),
    html.H2('How do I use this app?'),
    html.Div('To use this app, you need to create a new automation. To do this, click the "Create New Automation" button below.'),
    # make a link to the new automation page
    html.A('Create New Automation', href='/new-automation'),
    html.H2('See existing automations:'),
    # A list of all the automations in the automations folder
    html.Ul([
        html.Li([
            html.A(json.loads(open('automations/' + file, 'r').read())['automation_name'], href=f"/automation?automation_name={json.loads(open('automations/' + file, 'r').read())['automation_name']}")
        ]) for file in os.listdir('automations') if file.endswith('.json')
    ])
])