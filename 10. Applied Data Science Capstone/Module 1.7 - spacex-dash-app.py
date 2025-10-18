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

# Correct the range slider marks to be evenly spaced up to max_payload
payload_marks = {i: f'{i}' for i in range(0, int(max_payload) + 1000, 1000)}


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                        {'label': 'All Sites', 'value': 'ALL'},
                                                        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                                ),                                
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks=payload_marks,
                                                value = [min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total success launches per site
        site_success_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(site_success_counts, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
        return fig
    else:
        ## return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Calculate Success (1) vs. Failure (0) counts
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count'] # Rename columns for clarity
        
        fig = px.pie(outcome_counts, 
                     values='count', 
                     names='class', # Names will be 0 (Failure) and 1 (Success)
                     title=f'Total Success vs. Failed Launches for Site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'), # NO comma after 'figure')
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_plot(entered_site, slider_range):
    low, high = slider_range
    
    # 1. Filter by Payload Range (applies to ALL and single site views)
    payload_df = spacex_df[
                            (spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)
                            ]

    if entered_site == 'ALL':
        fig = px.scatter(
                        data_frame=payload_df,    # Your pandas DataFrame
                        x='Payload Mass (kg)', # Column name for the horizontal axis
                        y='class', # Column name for the vertical axis
                        # Optional parameters for enhanced visualization:
                        color='Booster Version Category', # Use a column to color the points
                        title=f'Correlation between Payload and Success for All Sites (Payload: {low} to {high} kg)'
                        )
        return fig
    else:
        filtered_df = payload_df[payload_df['Launch Site'] == entered_site]
        fig = px.scatter(
                        data_frame=filtered_df,    # Your pandas DataFrame
                        x='Payload Mass (kg)', # Column name for the horizontal axis
                        y='class', # Column name for the vertical axis
                        # Optional parameters for enhanced visualization:
                        color='Booster Version Category', # Use a column to color the points
                        title=f'Correlation between Payload and Success for Site {entered_site} (Payload: {low} to {high} kg)'
                        )
        return fig

# Run the app safely for both IBM Labs and local environments
if __name__ == '__main__':
   app.run()  # IBM Labs or hosted notebook environment

