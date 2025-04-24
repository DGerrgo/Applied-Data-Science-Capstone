# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'Kennedy Space Center', 'value': 'KSC LC-39A'},
                     {'label': 'Vandenberg Space Force Base', 'value': 'VAFB SLC-4E'},
                     {'label': 'Cape Canaveral Space Force Station LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'Cape Canaveral Space Force Station SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    
    html.Br(),

    # Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    # Scatter plot for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_grouped = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_grouped, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        df_counts = filtered_df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        df_counts['class'] = df_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(df_counts, values='count', names='class',
                     title=f'Success vs Failure for site {entered_site}')
    return fig

# Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs. Success for All Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Success for site {selected_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
