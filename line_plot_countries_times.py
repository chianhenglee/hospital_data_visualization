
# EXPAND STOCK SYMBOL INPUT TO PERMIT MULTIPLE STOCK SELECTION
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#import pandas_datareader.data as web # requires v0.6.0 or later
import plotly.graph_objs as go
import pandas as pd
import numpy as np


app = dash.Dash()


df = pd.read_csv('IHME_DALY_line_plot_data_try.csv')

year_options = df['Year'].unique()
country_options = df['Location'].unique()
country_options = []
for c in df['Location'].unique():
    country_options.append({'label':'{}'.format(c), 'value':c})

app.layout = html.Div([
    html.H1('DALYs Dashboard',style={'marginLeft':'20px'}),
    html.Div([
        html.H3('Select countries/locations:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_country_symbol',
            options=country_options,
            #value='Taiwan',
            placeholder='Select one or more locations',
            multi=True
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'80%','marginLeft':'20px'}),
    html.Div(),
    html.Div([
        html.H3('Select Time Range (start and end years):'),
        html.P(
        dcc.RangeSlider(
                    id='my_slider_symbol',
                    min=min(year_options),
                    max=max(year_options),
                    step=1,
                    marks={i: i for i in range(min(year_options),max(year_options)+1)},
                    value=[min(year_options),max(year_options)]
                    )
                )

    ], style={'display':'inline-block','width':'80%','marginLeft':'20px'}),

    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Plot them out!',
            style={'fontSize':20, 'marginLeft':'20px'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='my_graph',
        figure={
            'data': [
                {'x': [], 'y': []}
            ],
            'layout':
                {"title": "Select location(s) and time period and start plotting",
                 "height": 720},  # px
        }
    )
])



@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_country_symbol', 'value'),
    State('my_slider_symbol', 'value')])

def update_graph(n_clicks, value, values_y):
    start = values_y[0]
    end = values_y[1]
    traces = []

    for c in value:
        country_data = df[df['Location']==c]
        time_mask = (country_data['Year']>=values_y[0]) & (country_data['Year']<=values_y[1])
        selected_data = country_data[time_mask]
        time = selected_data['Year']
        DALYs = selected_data['Value']
        L_bound = selected_data['Lower bound']
        U_bound = selected_data['Upper bound']

        #trace = {'x':time, 'y':DALYs, 'name':c}
        trace = go.Scatter(
                    x=time,
                    y=DALYs,
                    #text=df[df['continent'] == i]['country'],
                    #text='('+L_bound+', '+DALYs+', '+U_bound+')',
                    hoverinfo='text',
                    text=
                        'Country: '+c+'<br>'+
                        'Year:    '+time.map(str)+'<br>'+
                        'DALYs:   '+round(DALYs/1000,2).map(str)+'k'+'<br>'+
                        'L_Bound: '+round(L_bound/1000,2).map(str)+'k'+'<br>'+
                        'U_Bound: '+round(U_bound/1000,2).map(str)+'k',
                    mode='markers+lines',
                    opacity=1.0,
                    marker={
                        'size': 5,
                        'line': {'width': 0.8}
                            },
                    name=c)
        traces.append(trace)


    fig = {
        'data': traces,
        'layout': go.Layout(
                title='DALYs Time Series',
                xaxis={'type': 'linear', 'title': 'Year'},
                yaxis={'title': 'DALYs'},
                #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                #legend={'x': 0, 'y': 1},
                hovermode='closest')
        }
    return fig




if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1',port='8001')
