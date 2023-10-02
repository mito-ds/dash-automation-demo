import json
import os

import dash
from dash import Input, Output, State, callback, dcc, html
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback

from utils import get_automation_json, get_file_name_from_automation_name, write_automation_to_file
from styles import button_style, success_button_style, input_style, text_area_style

dash.register_page(__name__)

layout = html.Div([
    html.Div([  # This is the container div
        html.H1('Create a New Automation', style={'color': 'white', 'padding': '0'}),
        html.Div('To create a new analysis, first enter the name of the analysis, as well as a description. Then, use the Mito spreadsheet to create the analysis as you would in Excel. Finally, click the "Save Automation" button to save the automation.', style={'color': 'white', 'padding-bottom': '20px'}),
        # Configuration section, with a title input as well as a text input for the automation description, as well as a number input for hours per run
        html.Div([
            html.Div('Automation Name: ', style={'color': 'white', 'padding-top': '10px', 'font-size': '20px'}),
            dcc.Input(id='automation-name', type='text', style=input_style, placeholder='Calculate Monthly Returns'),
            html.Div('Automation Description: ', style={'color': 'white', 'padding-top': '10px', 'font-size': '20px'}),
            dcc.Textarea(id='automation-description', style=text_area_style, placeholder='Calculates monthly returns for all portfolios, and then saves the results to a file. The result is a formatted excel file.'),
            html.Div('Hours per Run:', style={'color': 'white', 'padding-top': '10px', 'font-size': '20px', }),
            dcc.Input(id='hours-per-run', type='number', style=input_style, placeholder='3'),
        ], style={'margin-bottom': '20px'}),

        Spreadsheet(
            id='spreadsheet',
            import_folder='./data',
            code_options={
                'as_function': True,
                'call_function': False,
                'function_name': 'get_data',
                'function_params': ['file_name_export_excel', 'file_name_import_csv']
            }
        ),

        # A button to finalize the automation
        html.Button('Save Automation', id='create-automation', style=button_style),
        html.Div(id='output', style={'color': 'white', 'padding': '10px 0'})
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'height': '100%', 'color': 'white'})

AUTOMATION_PAGE_TEMPLATE = """

import dash
from dash import html

dash.register_page(__name__)

layout = html.Div([
    html.H1('{automation_name}'),
    html.Div('{automation_description}'),
    html.Div('This automations saves {hours_per_run} hours per run'),

    # Then, we display the spreadsheet component with the data (we need a way to save it to a file)
])

"""

OPEN_BRACKET = '{'
CLOSE_BRACKET = '}'

# When the create automation button is clicked, get state from the spreadsheet as well as the titles, and 
# write the results to the output

@mito_callback(
    Output('output', 'children'),
    Input('create-automation', 'n_clicks'),
    State('spreadsheet', 'mito_return_value'),
    State('automation-name', 'value'),
    State('automation-description', 'value'),
    State('hours-per-run', 'value'),
)
def create_automation(n_clicks, mito_return_value, automation_name, automation_description, hours_per_run):
    if n_clicks is None:
        return ''
    
    if automation_name is None or automation_name == '':
        return html.Div(['Please enter an automation name above.'], style={'color': 'red'})
    
    if automation_description is None or automation_description == '':
        return html.Div(['Please enter an automation description above.'], style={'color': 'red'})
    
    if hours_per_run is None or hours_per_run == '':
        return 
    

    analysis = get_automation_json(
        automation_name,
        automation_description,
        hours_per_run,
        mito_return_value.code(),
    )

    wrote = write_automation_to_file(automation_name, automation_description, hours_per_run, mito_return_value.code())
    if not wrote:
        return html.Div([f'An automation with the name {automation_name} already exists'], style={'color': 'red'})

    return html.Div([
        dcc.Link(html.Button(
            f"{automation_name} successfully created. Click to see", style=success_button_style), 
            href=f"/automation?automation_name={automation_name}", 
            refresh=True,
        ),
    ])