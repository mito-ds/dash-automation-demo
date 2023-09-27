


import inspect
import json
import os
from typing import Callable, Optional
import dash
from dash import html, callback, Input, Output, dcc, State
from mitosheet.mito_dash.v1 import Spreadsheet
import urllib.parse

dash.register_page(__name__)


layout = html.Div([
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),
    html.Div("", id='automation-metadata'),
    # Then, we display the spreadsheet component with the data (we need a way to save it to a file)

    # Empty run-automaton div
    html.Div(id='automation-output')
])


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


def get_automation_page(automation_data):

    header_and_description = html.Div([
        html.H1(automation_data['automation_name']),
        html.Div(automation_data['automation_description']),
        html.Div(f'This automation saves {automation_data["hours_per_run"]} hours per run'),
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
        Spreadsheet(id='input-data', import_folder='./data'),
        # Then, we have a button that when you click it, calls the function with the inputs
        html.Button('Run Automation', id='run-automation'),
        html.Div(id='automation-output')
    ])

@callback(
    Output('automation-output', 'children'), 
    Input('run-automation', 'n_clicks'), State('url', 'search'), 
    State('input-data', 'return-value'),
    suppress_callback_exceptions=True, prevent_initial_call=True
)
def run_automation(n_clicks, search, return_value):
    # Prase the search params
    automation_name = urllib.parse.parse_qs(search[1:])['automation_name'][0]

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

    if function:
        file_names = []
        for i, df in enumerate(return_value.dfs()):
            # Write to a file
            df.to_csv(f'tmp/{automation_name}/{i}.csv', index=False)
            file_names.append(f'tmp/{automation_name}/{i}.csv')

        result = function(*file_names)
        return html.Div([
            html.H3('Result'),
            html.Div(result)
        ])
    



@callback(Output('automation-metadata', 'children'), Input('url', 'search'))
def display_page(search):
    # Prase the search params
    automation_name = urllib.parse.parse_qs(search[1:])['automation_name'][0]

    # If the file doesn't exist, display an error page
    if not os.path.exists(f'automations/{automation_name}.json'):
        return html.Div([
            html.H3(f'Automation {automation_name} does not exist'),
            html.A('Go back to the main page', href='/')
        ])

    # Read in this from the automations folder
    with open(f'automations/{automation_name}.json') as f:
        automation_data = json.loads(f.read())

    return get_automation_page(automation_data)