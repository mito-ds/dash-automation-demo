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
        html.Div([f'{num_automations} Automation']),
        html.Div([f'{num_runs} Total Runs']),
        html.Div([f'{total_time_saved} Total Hours Saved']),
    ])


app.layout = html.Div([
    html.H1('Spreadsheet Automation Hub'),
    # A 1-3 column grid, that contains the information about the running automations
    html.Div(get_total_time_saved_data(), id='total-metadata'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

# When the page changes, we reload the total time saved data
@callback(
    Output('total-metadata', 'children'),
    Input('url', 'pathname')
)
def update_total_time_saved(pathname):
    return get_total_time_saved_data()

if __name__ == '__main__':
    app.run(debug=True)