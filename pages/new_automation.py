import dash
from dash import html, dcc, callback, Input, Output, State
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback
import json
from utils import get_automation_json

dash.register_page(__name__)

layout = html.Div([
    html.Div([  # This is the container div
        html.H1('Create a New Automation', style={'color': 'white', 'padding': '10px 0'}),
        # Configuration section, with a title input as well as a text input for the automation description, as well as a number input for hours per run
        html.Div([
            html.Div('Automation Name', style={'color': 'white', 'padding': '10px 0'}),
            dcc.Input(id='automation-name', type='text', style={'width': '100%', 'margin': '10px 0'}),
            html.Div('Automation Description', style={'color': 'white', 'padding': '10px 0'}),
            dcc.Textarea(id='automation-description', style={'width': '100%', 'height': '100px', 'margin': '10px 0'}),
            html.Div('Hours per Run', style={'color': 'white', 'padding': '10px 0'}),
            dcc.Input(id='hours-per-run', type='number', style={'width': '100%', 'margin': '10px 0'}),
        ], style={'margin': '20px'}),

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
        html.Button('Create Automation', id='create-automation', style={
            'background-color': '#5A67D8',
            'color': 'white',
            'padding': '10px 15px',
            'border-radius': '10px',
            'text-decoration': 'none',
            'display': 'inline-block',
            'margin': '20px 0'
        }),
        html.Div(id='output', style={'color': 'white', 'padding': '10px 0'})
    ], style={'max-width': '1200px', 'margin': 'auto', 'padding': '20px'})  # This style ensures the content is centered and has a max width
], style={'background-color': '#2D3748', 'height': '100%', 'color': 'white', 'padding': '20px 0'})

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
    
    analysis = get_automation_json(
        automation_name,
        automation_description,
        hours_per_run,
        mito_return_value.code(),
    )

    # Write the automation metadata to a file in /automations/{automation_name}.json
    with open(f'automations/{automation_name}.json', 'w') as f:
        f.write(analysis)

    return html.Div([
        f'Automation {automation_name} created with {mito_return_value.dfs()} rows, {automation_description}, and {hours_per_run} hours per run. Check it out at',
        dcc.Link(html.Button("here"), href=f"/automation?automation_name={automation_name}", refresh=True),
    ])