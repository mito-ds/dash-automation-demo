


import inspect
import json
import os
from typing import Callable, Optional
import dash
from dash import html, callback, Input, Output, dcc, State
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback
import urllib.parse
import pandas as pd
import time

from utils import get_automation_json

dash.register_page(__name__)


layout = html.Div([
    html.Div([  # This is the container div
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.Div("", id='automation-metadata', style={'color': 'white', 'margin-bottom': '20px'}),
        Spreadsheet(id='input-data', import_folder='./data'),
        html.Button('Run Automation', id='run-automation', style={
            'background-color': '#5A67D8',
            'color': 'white',
            'padding': '10px 15px',
            'border-radius': '10px',
            'text-decoration': 'none',
            'display': 'inline-block',
            'margin': '20px 0'
        }),
        html.Div(id='automation-output', style={'color': 'white', 'padding': '10px 0'})
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'background-color': '#2D3748', 'height': '100%', 'color': 'white', 'padding': '20px 0'})



def get_function_from_code_unsafe(code: str) -> Optional[Callable]:
    """
    Given a string of code, returns the first function defined in the code. Notably, to do
    this, it executes the code, and then returns the first function defined in the code. 

    As it executes the full code string, you should only use this function if you trust the
    code string -- and in our case, if the function is not called.

    If no functions are defined, returns None
    """
    functions_before = [f for f in locals().values() if callable(f)]
    exec(code)
    functions = [f for f in locals().values() if callable(f) and f not in functions_before]

    # We then find the one function that was defined inside of this module -- as the above 
    # exec likely defines all the other mitosheet functions (none of which we actaully want)
    for f in functions:
        if inspect.getmodule(f) == inspect.getmodule(get_function_from_code_unsafe):
            return f
        
    raise ValueError(f'No functions defined in code: {code}')


def get_automation_metadata(automation_data):

    num_runs = len(automation_data['runs'])
    hours_saved = num_runs * automation_data['hours_per_run']

    header_and_description = html.Div([
        html.H1("Automation: " + automation_data['automation_name']),
        html.Div("Description", automation_data['automation_description']),
        html.Div(f'This automation has been run {num_runs} times, and has saved {hours_saved} hours'),
    ])

    # Then, from the code, we get the number of inputs and outputs 
    # (we need a way to read it nicely from a file). It would be really useful to have some Mito interface functions for dealing with generated code...
    code_string = automation_data['automation_code']
    function = get_function_from_code_unsafe(code_string)

    # Get the argument names from the function
    argument_names = list(inspect.signature(function).parameters.keys()) if function is not None else []

    # Then, allow users to configure two new dataframes
    return html.Div([
        header_and_description,
    ])

@mito_callback(
    Output('automation-output', 'children'), 
    Input('run-automation', 'n_clicks'), State('url', 'search'), 
    State('input-data', 'mito_return_value'), prevent_initial_call=True
)
def run_automation(n_clicks, search, return_value):
    # Prase the search params
    # TODO: handle errors here - if it's not included
    search = urllib.parse.parse_qs(search[1:])

    if 'automation_name' not in search:
        return html.Div([
            html.H3('No automation name provided'),
            html.A('Go back to the main page', href='/')
        ])
    
    automation_name = search['automation_name'][0]

    # If the file doesn't exist, display an error page
    if not os.path.exists(f'automations/{automation_name}.json'):
        return html.Div([
            html.H3(f'Automation {automation_name} does not exist'),
            html.A('Go back to the main page', href='/')
        ])

    # Read in this from the automations folder
    with open(f'automations/{automation_name}.json') as f:
        automation_data = json.loads(f.read())

    
    # Get the function
    code_string = automation_data['automation_code']
    function = get_function_from_code_unsafe(code_string)

    # Get the argument names from the function
    argument_names = list(inspect.signature(function).parameters.keys()) if function is not None else []

    # If there are the wrong number of arguments provided in the dfs, return an error
    if len(argument_names) != len(return_value.dfs()):
        return html.Div([
            html.H3(f'Expected {len(argument_names)} arguments, but got {len(return_value.dfs())}. Please update the mitosheet above.'),
        ])

    if function:
        file_names = []
        # Make the file tmp/{automation_name}
        os.makedirs(f'tmp/{automation_name}', exist_ok=True)

        for i, df in enumerate(return_value.dfs()):
            # Write to a file
            df.to_csv(f'tmp/{automation_name}/{i}.csv', index=False)
            file_names.append(f'tmp/{automation_name}/{i}.csv')

        result = function(*file_names)

        new_automation_json = get_automation_json(
            automation_name,
            automation_data['automation_description'],
            automation_data['hours_per_run'],
            automation_data['automation_code'],
            automation_data['runs'] + [time.time()]
        )
        # Write the automation metadata to a file in /automations/{automation_name}.json
        with open(f'automations/{automation_name}.json', 'w') as f:
            f.write(new_automation_json)

        return html.Div([
            html.H3('Result'),
            html.Div(str(result.columns))
        ])
    



@callback(Output('automation-metadata', 'children'), Input('url', 'search'))
def display_page(search):
    # Prase the search params
    search = urllib.parse.parse_qs(search[1:])

    if 'automation_name' not in search:
        return html.Div([
            html.H3('No automation name provided'),
            html.A('Go back to the main page', href='/')
        ])
    
    automation_name = search['automation_name'][0]

    # If the file doesn't exist, display an error page
    if not os.path.exists(f'automations/{automation_name}.json'):
        return html.Div([
            html.H3(f'Automation {automation_name} does not exist'),
            html.A('Go back to the main page', href='/')
        ])

    # Read in this from the automations folder
    with open(f'automations/{automation_name}.json') as f:
        automation_data = json.loads(f.read())

    return get_automation_metadata(automation_data)