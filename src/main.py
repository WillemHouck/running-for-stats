from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import utils
import plotly.express as px


# load and process data
data = utils.collect_strava_data()
runs = utils.preprocess_runs(data)

runs_plotdata = utils.add_weeks_without_runs(runs)

# build application layout
app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='Runnalytics', style={'textAlign': 'center'}),
    dcc.Graph(figure=px.bar(runs_plotdata,
                            x='year_week',
                            y='distance'), id='graph-content'),
])


@callback(
    Output('graph-content', 'figure')
)
def update_graph():
    filtered_data = runs_plotdata
    return px.bar(filtered_data, x='year_week', y='distance')


if __name__ == '__main__':

    # run application
    app.run(debug=True)
