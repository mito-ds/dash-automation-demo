


import base64
import inspect
import json
import os
from typing import Callable, Optional
import dash
from dash import html, callback, Input, Output, dcc, State
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback, RunnableAnalysis
import urllib.parse
import pandas as pd
import time
from mitosheet.public.v3 import *

from utils import get_automation_json, read_automation_from_file, write_automation_to_file
from styles import button_style, disabled_button_style, mito_theme

dash.register_page(__name__)


layout = html.Div([
    html.Div([  # This is the container div
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.Div("", id='automation-metadata', style={'color': 'white', 'margin-bottom': '10px'}),
        html.Div("", id='automation-num-uploads', style={'color': 'white', 'margin-bottom': '20px'}),
        Spreadsheet(
            id='input-data', 
            import_folder='./data',
            theme=mito_theme),
        html.Button('Run Automation', id='run-automation', style=disabled_button_style),
        dcc.Download(id="download-dataframe-csv"),
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'height': '100%', 'color': 'white'})

def get_automation_metadata(automation):

    num_runs = len(automation['runs'])
    hours_saved = num_runs * automation['hours_per_run']

    header_and_description = html.Div([
        html.H1("Automation: " + automation['automation_name']),
        html.Div("Description: " + automation['automation_description']),
        html.Div(f'This automation has been run {num_runs} times, and has saved {hours_saved} hours'),
    ])

    # Then, allow users to configure two new dataframes
    return html.Div([
        header_and_description,
        html.H2('Configure Inputs', style={'color': 'white', 'padding': '10px 0'}),
    ])

@mito_callback(
    Output('download-dataframe-csv', 'data'), 
    Input('run-automation', 'n_clicks'), State('url', 'search'), 
    State('input-data', 'spreadsheet_result'), prevent_initial_call=True
)
def run_automation(n_clicks, search, spreadsheet_result):
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
   

    # Then, we use the analysis JSON to create a runnable analysis
    # and we get the import parameters, and tell the user to configure them
    runnable_analysis = RunnableAnalysis.from_json(automation['analysis_json'])
    import_params = runnable_analysis.get_param_metadata('import')
       

    # If there are the wrong number of arguments provided in the dfs, return an error
    if len(import_params) != len(spreadsheet_result.dfs()):
        return html.Div([
            html.H3(f'Expected {len(import_params)} arguments, but got {len(spreadsheet_result.dfs())}.'),
        ])

    arguments = {param['name']: df for param, df in zip(import_params, spreadsheet_result.dfs())}    
    result = runnable_analysis.run(*arguments)

    write_automation_to_file(
        automation['automation_name'],
        automation['automation_description'],
        automation['hours_per_run'],
        runnable_analysis,
        automation['runs'] + [time.time()],
        overwrite=True
    )

    if isinstance(result, pd.DataFrame):
        df = result
    else:
        df = result[-1]

    return dcc.send_data_frame(df.to_csv, "mydf.csv")


@mito_callback(
    Output('automation-num-uploads', 'children'), 
    Output('run-automation', 'style'),
    Input('url', 'search'), Input('input-data', 'spreadsheet_result')
)
def display_number_of_uploads_remaining(search, spreadsheet_result):
    # Prase the search params
    search = urllib.parse.parse_qs(search[1:])

    if 'automation_name' not in search:
        return ''
    
    automation_name = search['automation_name'][0]
    automation = read_automation_from_file(automation_name)

    # If the file doesn't exist, display an error page
    if automation is None:
        return ''
    
    # Then, we use the analysis JSON to create a runnable analysis
    # and we get the import parameters, and tell the user to configure them
    runnable_analysis = RunnableAnalysis.from_json(automation['analysis_json'])
    import_params = runnable_analysis.get_param_metadata('import')


    # Then, build a helpful message for the user -- a list of the parameters, and their original values
    argument_list = html.Ul([
        html.Li([
            html.Div(f'Parameter {index}: {param["name"]}={param["original_value"]}')
        ]) for index, param in enumerate(import_params)
    ])
    
    num_dfs = len(spreadsheet_result.dfs()) if spreadsheet_result is not None else 0

    # Return colored text based on the number of arguments
    if num_dfs == len(import_params):
        return html.Div([f'You have uploaded {num_dfs} of {len(import_params)} required arguments'], style={'color': 'green'}), button_style
    
    if num_dfs > len(import_params):
        return html.Div([
                f'You have uploaded {num_dfs} of {len(import_params)} required arguments',
                html.Div('You have uploaded too many arguments. Please delete some of them.', style={'color': 'red'}),
                argument_list
            ], 
            style={'color': 'red'}
        ), disabled_button_style
    
    if num_dfs < len(import_params):
        return html.Div([
                f'You have uploaded {num_dfs} of {len(import_params)} required arguments',
                argument_list
            ], 
            style={'color': 'orange'}
        ), disabled_button_style


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

