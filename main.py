import dash
from dash import Dash, html, dcc, callback, Output, Input
import os
import json
from utils import get_all_automations

app = Dash(__name__, use_pages=True, external_scripts=['./static/global.css'])


def get_total_time_saved_data():
    num_automations = 0
    num_runs = 0
    total_time_saved = 0

    for automation in get_all_automations():
        num_automations += 1
        num_runs += len(automation['runs'])
        total_time_saved += len(automation['runs']) * automation['hours_per_run']

    return html.Div([
        html.Div([f'{num_automations} Automations'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#9d6cff', 'padding': '10px', 'border-radius': '10px'}),
        html.Div([f'{num_runs} Runs'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#E53E3E', 'padding': '10px', 'border-radius': '10px'}),
        html.Div([f'{total_time_saved} Hours Saved'], style={'font-weight': 'bold', 'color': 'white', 'background-color': '#38A169', 'padding': '10px', 'border-radius': '10px'}),
    ], style={'display': 'grid', 'grid-template-columns': 'repeat(3, 1fr)', 'gap': '10px', 'padding': '20px', })


app.layout = html.Div([
    html.Div([  # This is the container div
        html.Div(
            [
                dcc.Link(
                    html.H1('Spreadsheet Automation Hub', style={'color': 'white'}),
                    href='/',  # This is the main/root page URL
                    style={'text-decoration': 'none'}
                ),
                # A 1-3 column grid, that contains the information about the running automations
                html.Div(get_total_time_saved_data(), id='total-metadata', style={'margin': '20px'}),
            ],
            style={'text-align': 'center', 'background-color': '#363637', 'color': 'white', 'padding': '10px', 'border-radius': '5px'}
        ),
        dash.page_container
    ], style={'max-width': '1200px', 'margin': 'auto'})  # This style ensures the content is centered and has a max width
], style={'color': 'white'})

# When the page changes, we reload the total time saved data
@callback(
    Output('total-metadata', 'children'),
    Input('url', 'pathname')
)
def update_total_time_saved(pathname):
    return get_total_time_saved_data()

if __name__ == '__main__':
    app.run(debug=True)
