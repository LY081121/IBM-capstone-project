# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
launch_sites=spacex_df.groupby(['Launch Site']).first().index.tolist()
launch_sites_dict=[{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
   launch_sites_dict.append({'label': site, 'value': site}) 
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
                                dcc.Dropdown(id='site-dropdown',
                                            options=launch_sites_dict,
                                            value='ALL',
                                            placeholder="place holder here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                        2500: '2500',
                                                        5000: '5000',
                                                        7500: '7500',
                                                        10000:'10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                html.Br(),
                                ])

# TASK 2:
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        filtered_df=spacex_df.groupby('Launch Site', as_index=False).mean()
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Total Successful Launches by site')
        return fig
    else:
        filtered_df=spacex_df.groupby('Launch Site').get_group(entered_site)['class'].value_counts()
        fig = px.pie(values=filtered_df,
        names=['Failure','Success'],
        title='Total Successful Launches for site {}'.format(entered_site) )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value")])

def get_scatter_plot(entered_site,payload_range):
    print(payload_range)
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0],payload_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, y='class', x ='Payload Mass (kg)',
        color="Booster Version Category",
        title='Correlation between payload and success for all sites')
        return fig
    else:
        filtered_df=filtered_df.groupby('Launch Site').get_group(entered_site)
        fig = px.scatter(filtered_df, y='class', x ='Payload Mass (kg)',
        color="Booster Version Category",
        title='Correlation between payload and success for site {}'.format(entered_site) )
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
