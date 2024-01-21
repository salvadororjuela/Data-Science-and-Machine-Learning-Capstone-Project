# Import required libraries
import pandas as pd
import dash
# import dash_html_components as html  # deprecated
from dash import html
# import dash_core_components as dcc  # deprecated
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {"label": "All Sites", "value": "ALL"},
    {"label": "CCAFS LC-40", "value": "CCAFS LC-40"},
    {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"},
    {"label": "KSC LC-39A", "value": "KSC LC-39A"},
    {"label": "VAFB SLC-4E", "value": "VAFB SLC-4E"}
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id="site_dropdown",
                                options=[{"label": i["label"], "value": i["value"]} for i in dropdown_options],
                                value="ALL",
                                placeholder="Select a launch site from the dropdown list",
                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id="payload-slider",
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Create a list where str is added to a new column in the dataset with failure = 0 and success = 1
status = list()
for i in spacex_df["class"]:
    if i == 1:
        status.append("Success")
    else:
        status.append("Failure")
spacex_df["status"] = status
# Add a column with value of 1 for each success or failure and count later as a sum of "failure" or "success"
spacex_df["count"] = 1

@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site_dropdown", component_property="value"))

def get_pie_chart(entered_site): 
    # Calculate the average success rate   
    data = spacex_df.groupby(['Launch Site'], as_index=False).mean()

    if entered_site == 'ALL':
        fig = px.pie(data, values='class', names='Launch Site', title='Launch Success Rate For All Sites')
        return fig
    # return the outcomes in pie chart for a selected site
    else:
        data = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(data, values='count', names='status', title=f'Launch Success Rate For {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [Input(component_id="site_dropdown", component_property="value"), 
     Input(component_id="payload-slider", component_property="value")]
)

def get_scatter_plot(entered_site, entered_payload):
    print(entered_payload)
    data = spacex_df[(spacex_df["Payload Mass (kg)"] >= entered_payload[0]) & (spacex_df['Payload Mass (kg)'] <= entered_payload[1])]
    if entered_site == "ALL":
        fig = px.scatter(
            data, x="Payload Mass (kg)", y="class",
            color="Booster Version", hover_name="Booster Version", size_max=55,
            title="Payload Mass Scatter Chart For All Launch Sites"
        )
        return fig
    
    else:
        data = data[data["Launch Site"] ==  entered_site]
        fig = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version", hover_name="Booster Version", size_max=55,
                         title=f"Payload Mass Scatter Chart For {entered_site}")
        return fig
    
# Run the app
if __name__ == '__main__':
    app.run_server()
