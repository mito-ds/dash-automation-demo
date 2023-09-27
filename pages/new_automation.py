import dash
from dash import html, dcc, callback, Input, Output, State
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback
import json

dash.register_page(__name__)

layout = html.Div([
    html.H1('Create a New Automation'),
    # Configuration section, with a title input as well as a text input for the automation description, as well as a number input for hours per run
    html.Div([
        html.Div('Automation Name'),
        dcc.Input(id='automation-name', type='text'),
        html.Div('Automation Description'),
        dcc.Textarea(id='automation-description'),
        html.Div('Hours per Run'),
        dcc.Input(id='hours-per-run', type='number'),
    ]),


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
    html.Button('Create Automation', id='create-automation'),
    html.Div(id='output')
])

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
    State('spreadsheet', 'return_value'),
    State('automation-name', 'value'),
    State('automation-description', 'value'),
    State('hours-per-run', 'value'),
)
def create_automation(n_clicks, return_value, automation_name, automation_description, hours_per_run):
    if n_clicks is None:
        return ''
    
    # Write the automation metadata to a file in /automations/{automation_name}.json
    with open(f'automations/{automation_name}.json', 'w') as f:
        f.write(json.dumps({
           "automation_name": automation_name,
            "automation_description": automation_description,
            "hours_per_run": hours_per_run,
            "automation_code": return_value.code()
        }))

    return html.Div([
        f'Automation {automation_name} created with {return_value.dfs()} rows, {automation_description}, and {hours_per_run} hours per run. Check it out at',
        dcc.Link(html.Button("here"), href=f"/automations?automation_name={automation_name}", refresh=True),
    ])