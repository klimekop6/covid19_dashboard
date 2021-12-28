import pandas as pd
import plotly.express as px 
from dash import Dash, dcc, html, Input, Output  

# dcc -> dash core components https://dash.plotly.com/dash-core-components
# pltotly.express -> https://plotly.com/python/


app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
df = pd.read_csv('intro_bees.csv')

df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1('Web Application Dashboards with Dash', style={'text-align': 'center'}),

    html.Div([
        
            dcc.Dropdown(id='slct_year',    
                        options=[
                            {'label': '2015', 'value': 2015},
                            {'label': '2016', 'value': 2016},
                            {'label': '2017', 'value': 2017},
                            {'label': '2018', 'value': 2018}],
                        multi=False,
                        value=2015,
                        clearable=False,
                        style={'width': '90px'}
            )
    ],
        style = {'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%'}
    ),

    html.Div(id='output_container', style={'text-align': 'center'}),
    html.Br(),

    dcc.Graph(id='my_bee_map'),
    html.Br(),

    html.Div('Colored text', id='colored_text', style={'text-align': 'center'}),

    html.Div([
        
            dcc.RadioItems(id='slct_color',
                options=[
                    {'label': 'Black', 'value': 'black'},
                    {'label': 'Blue', 'value': 'blue'},
                    {'label': 'Red', 'value': 'red'},
                    {'label': 'Green', 'value': 'green'}
                ],
                value='MTL',
                labelStyle={'display': 'inline-block'}
            )    
    ],
        style = {'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%'}
    )

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),]
)
def update_graph(option_slctd):

    container = f'The year chosen by user was: {option_slctd}'

    dff = df.copy()
    dff = dff[dff['Year'] == option_slctd]
    dff = dff[dff['Affected by'] == 'Varroa_mites']

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope='usa',
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    return container, fig

@app.callback(
    Output(component_id='colored_text', component_property='style'),
    [Input(component_id='slct_color', component_property='value')]
)
def update_text_color(color_slctd):    
    
    return {'color': color_slctd, 'text-align': 'center'}

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server('192.168.0.116', 55554, debug=True, use_reloader=False)