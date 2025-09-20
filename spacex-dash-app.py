# spacex-dash-app.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Determine min and max payload for the slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "SpaceX Launch Dashboard"

# ------------------------
# Layout
# ------------------------
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center'}),

    # Dropdown for launch site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # Pie chart for success counts
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={i: str(i) for i in range(0, 10001, 2500)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.Br(),

    # Scatter chart for payload vs success
    dcc.Graph(id='success-payload-scatter-chart')
])

# ------------------------
# Callbacks
# ------------------------

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Pie chart for total successes by site
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs Failure Launches for site {selected_site}'
        )
    return fig


# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filter data within payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Correlation between Payload and Success for All Sites"
        )
    else:
        # Filter for the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for site {selected_site}"
        )
    return fig


# ------------------------
# Run the app
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)