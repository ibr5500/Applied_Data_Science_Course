# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                                        {'label': site, 'value': site}
                                        for site in sorted(spacex_df['Launch Site'].dropna().unique())
                                    ],
                                    value='ALL',
                                    searchable=True,
                                    clearable=False
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=max_payload,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(launch_site):
    if launch_site == 'ALL':
        successful_launches = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()
        fig = px.pie(
            values=successful_launches.values,
            names=successful_launches.index,
            title='Successful Launches by Site'
        )
    else:
        site_data = spacex_df[spacex_df['Launch Site'] == launch_site]
        launch_counts = site_data['class'].value_counts().reindex([1, 0], fill_value=0)
        fig = px.pie(
            values=launch_counts.values,
            names=['Successful', 'Failed'],
            title=f'Launch Outcomes for {launch_site}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_payload_scatter(launch_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if launch_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == launch_site]

    return px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Launch Site',
        title='Payload Mass vs. Launch Outcome'
    )


# Run the app
if __name__ == '__main__':
    app.run()
