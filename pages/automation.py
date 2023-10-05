


import base64
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
from mitosheet.public.v3 import *

from utils import get_automation_json, read_automation_from_file, write_automation_to_file
from styles import button_style

dash.register_page(__name__)


layout = html.Div([
    html.Div([  # This is the container div
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.Div("", id='automation-metadata', style={'color': 'white', 'margin-bottom': '20px'}),
        Spreadsheet(id='input-data', import_folder='./data'),
        html.Button('Run Automation', id='run-automation', style=button_style),
        dcc.Download(id="download-dataframe-csv"),
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'height': '100%', 'color': 'white'})



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


def get_automation_metadata(automation):

    num_runs = len(automation['runs'])
    hours_saved = num_runs * automation['hours_per_run']

    header_and_description = html.Div([
        html.H1("Automation: " + automation['automation_name']),
        html.Div("Description", automation['automation_description']),
        html.Div(f'This automation has been run {num_runs} times, and has saved {hours_saved} hours'),
    ])

    # Then, from the code, we get the number of inputs and outputs 
    # (we need a way to read it nicely from a file). It would be really useful to have some Mito interface functions for dealing with generated code...
    code_string = automation['automation_code']
    function = get_function_from_code_unsafe(code_string)

    # Get the argument names from the function
    argument_names = list(inspect.signature(function).parameters.keys()) if function is not None else []

    # Tell them how many arguments there are

    # Then, allow users to configure two new dataframes
    return html.Div([
        header_and_description,
        html.H2('Configure Inputs', style={'color': 'white', 'padding': '10px 0'}),
        html.Div(f'Please use the Mito spreadsheet to configure the {len(argument_names)} argument{"s" if len(argument_names) > 2 else ""} for this automation'),
    ])

@mito_callback(
    Output('download-dataframe-csv', 'data'), 
    Input('run-automation', 'n_clicks'), State('url', 'search'), 
    State('input-data', 'spreadsheet_result'), prevent_initial_call=True
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
    automation = read_automation_from_file(automation_name)
    
    # If the file doesn't exist, display an error page
    if automation is None:
        return html.Div([
            html.H3(f'Automation {automation_name} does not exist'),
            html.A('Go back to the main page', href='/')
        ])
   
    
    # Get the function
    code_string = automation['automation_code']
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

        # Remove all file paths
        for file_name in file_names:
            os.remove(file_name)

        write_automation_to_file(
            automation['automation_name'],
            automation['automation_description'],
            automation['hours_per_run'],
            automation['automation_code'],
            automation['runs'] + [time.time()],
            overwrite=True
        )

        df = result[-1]

        return dcc.send_data_frame(df.to_csv, "mydf.csv")


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
    automation = read_automation_from_file(automation_name)

    # If the file doesn't exist, display an error page
    if automation is None:
        return html.Div([
            html.H3(f'Automation {automation_name} does not exist'),
            html.A('Go back to the main page', href='/')
        ])

    return get_automation_metadata(automation)

