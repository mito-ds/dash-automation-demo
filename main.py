import dash
from dash import Dash, html, dcc, callback, Output, Input
import os
import json

app = Dash(__name__, use_pages=True)


def get_total_time_saved_data():
    # Read in the number of automations
    num_automations = len(os.listdir('automations'))
    # Read in the number of runs
    num_runs = 0
    total_time_saved = 0
    for automation in os.listdir('automations'):
        with open(f'automations/{automation}') as f:
            automation_data = json.load(f)
            num_runs += len(automation_data['runs'])
            total_time_saved += len(automation_data['runs']) * automation_data['hours_per_run']

    return html.Div([
        html.Div([f'{num_automations} Automations'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#5A67D8', 'padding': '10px', 'border-radius': '10px'}),
        html.Div([f'{num_runs} Total Runs'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#E53E3E', 'padding': '10px', 'border-radius': '10px'}),
        html.Div([f'{total_time_saved} Total Hours Saved'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#38A169', 'padding': '10px', 'border-radius': '10px'}),
    ], style={'display': 'grid', 'grid-template-columns': 'repeat(3, 1fr)', 'gap': '10px', 'padding': '20px', 'background-color': '#2D3748'})


app.layout = html.Div([
    html.Div([  # This is the container div
        dcc.Link(
            html.H1('Spreadsheet Automation Hub', style={'text-align': 'center', 'background-color': '#4A5568', 'color': 'white', 'padding': '10px'}),
            href='/',  # This is the main/root page URL
            style={'text-decoration': 'none'}
        ),
        # A 1-3 column grid, that contains the information about the running automations
        html.Div(get_total_time_saved_data(), id='total-metadata', style={'margin': '20px'}),
        dash.page_container
    ], style={'max-width': '1200px', 'margin': 'auto'})  # This style ensures the content is centered and has a max width
], style={'background-color': '#2D3748', 'color': 'white'})

# When the page changes, we reload the total time saved data
@callback(
    Output('total-metadata', 'children'),
    Input('url', 'pathname')
)
def update_total_time_saved(pathname):
    return get_total_time_saved_data()

if __name__ == '__main__':
    app.run(debug=True)
