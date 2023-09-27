import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)


def get_automation_metadata():
    return '1 Automation', '4 runs', '3 hours saved'




app.layout = html.Div([
    html.H1('Spreadsheet Automation Hub'),
    # A 1-3 column grid, that contains the information about the running automations
    html.Div([
        html.Div(get_automation_metadata()[0]),
        html.Div(get_automation_metadata()[1]),
        html.Div(get_automation_metadata()[2]),
    ]),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)