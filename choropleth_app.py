
import plotly.offline as pyo
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
import colorlover as cl
import plotly.colors as plc

#app = dash.Dash() # this line is for local test

# the following two lines are for deployment through Heroku
app = dash.Dash(__name__)
server = app.server


mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"
#mapbox_access_token = 'pk.eyJ1IjoiY2hpYW5oZW5nbGVlIiwiYSI6ImNqajN6OTc3djFqcDUzdm82MnM4eDNibnAifQ.v_27stJt5we4xMKrk8nenQ'
#mapbox_access_token = 'pk.eyJ1IjoiY2hpYW5oZW5nbGVlIiwiYSI6ImNqamk1bDJ2ODNxcmszd256MDZ0N25laGYifQ.L5T6cvt07wm_LkcMjnOewg'
## Load the whole raw dataset
df = pd.read_csv('Test_data.csv')


######## Loading Essential Data for plotting polygons of counties and cities #######
# Get counties name list
with open('counties/counties_list.txt') as f:
    Clist=f.read().splitlines()

# Get centroid of polygons correspond to Clist order
with open('counties/counties_centroid.txt') as f2:
    temp_coords = f2.read().splitlines()
temp2=[i.split(',') for i in temp_coords]
center_lonlat=[[float(k) for k in j] for j in temp2]

# Construct two dictionaries one for storing the lon,lat of the center of each county/city,
# another for storing geojson files (both as key,value pairs)
Dict_counties={}
Dict_counties_center={}
i=0
for c in Clist:
    with open('counties/'+c+'.json') as f:
        geojsonfile = json.load(f)
    Dict_counties[c]=geojsonfile
    Dict_counties_center[c]=center_lonlat[i]
    i=i+1



###### Get options for selection ###########

# from the loaded data set df

#year_options = df['Year'].unique()
year_options = []
for y in df['Year'].unique():
    year_options.append({'label':'{}'.format(y), 'value':y})

#age_options = df['Age'].unique()
age_options = []
for ag in df['Age'].unique():
    age_options.append({'label':'{}'.format(ag), 'value':ag})

#gender_options = df['Sex'].unique()
gender_options = []
for g in df['Sex'].unique():
    gender_options.append({'label':'{}'.format(g), 'value':g})


####### Layout of the dashboard ######

app.layout = html.Div([
    html.H1('Counties Map Choropleth Dashboard',style={'marginLeft':'20px'}),

    html.Div([
        html.H3('Select Year:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_year_symbol',
            options=year_options,
            #value='Taiwan',
            placeholder='Select a year...',
            multi=False
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%','marginLeft':'20px'}),

    html.Div(),

    html.Div([
        html.H3('Select Age:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_age_symbol',
            options=age_options,
            #value='Taiwan',
            placeholder='Select an age group...',
            multi=False
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%','marginLeft':'20px'}),

    html.Div(),

    html.Div([
        html.H3('Select Gender:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_gender_symbol',
            options=gender_options,
            #value='Taiwan',
            placeholder='Select a gender...',
            multi=False
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%','marginLeft':'20px'}),

    html.Div(),

    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit and plot!',
            style={'fontSize':20, 'marginLeft':'20px'}
        ),
    ], style={'display':'inline-block','width':'30%','marginTop':'20px'}),

    html.Div(),

    html.Div([
        dcc.Graph(
            id='my_graph',
            figure={
                'data': [
                    {'x': [], 'y': []}
                    ],
                    'layout':
                    {"title": "Select location(s) and time period and start plotting",
                    "height": 720,
                    "width": 200},  # px
                    }
                    ),
    ], style = {'display':'inline-block','marginLeft':'0px','width':'50%'}
    ),

    #html.Div(),

    html.Div([
        dcc.Graph(
            id='my_graph2',
            figure={
                'data': [
                    {'x': [], 'y': []}
                    ],
                    'layout':
                    {"title": "This is a bar chart",
                    "height": 720,
                    "width": 200},  # px

                    }
                    ),
    ], style = {'display':'inline-block','marginLeft':'0px','width':'50%'}
    ),
])

##### Callback section ##########

@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_year_symbol', 'value'),
    State('my_age_symbol','value'),
    State('my_gender_symbol', 'value'),
    State('my_graph','figure')])

def update_graph(n_clicks, year, age, gender, figure):

    ################# Get data from user specified conditions/criteria

    '''
    This should just be a function call to get the information needed for this plot
    '''

    selected_data = df[(df['Year']==year) & (df['Age']==age) & (df['Sex']==gender)]
    selected_data.set_index('Location',inplace=True)

    Year = selected_data['Year'].unique()
    Gender = selected_data['Sex'].unique()
    Age = selected_data['Age'].unique()

    Dict_data = {}
    for location in selected_data.index:
        Dict_data[location] = selected_data.loc[location]

    ####### This section generate proper color scale for plotting ##########

    ### get color scale
    colors = cl.scales['8']['seq']['OrRd']
    #['rgb(255,247,236)', 'rgb(254,232,200)', 'rgb(253,212,158)',
    # 'rgb(253,187,132)', 'rgb(252,141,89)', 'rgb(239,101,72)',
    # 'rgb(215,48,31)', 'rgb(153,0,0)']
    # interpolate to get 100 different colors in the color scale gradient
    interp_colors=cl.to_rgb(cl.interp( colors, 100 ))
    my_colorscale = plc.make_colorscale(interp_colors) # create colorscale e.g. [0.23,'rgb(103, 29, 45)'']
    my_colorscale_nums = [i[0] for i in my_colorscale] # get the 0-1 values in each element from above

    data_values = [float(list(Dict_data.values())[i].Value) for i in range(len(Dict_data))]
    data_values_n = data_values/np.max(data_values)
    index_data_color = [np.argmin(np.abs(np.array(my_colorscale_nums)-k)) for k in data_values_n]


    # put it in a dictionary
    Dict_colorscale={}
    i=0
    for c in list(selected_data.index):
        Dict_colorscale[c] = my_colorscale[index_data_color[i]][1]
        i=i+1

    ### Now we generate colorbar manually as annotations in the layout
    annotations = [
        dict(
            showarrow = False,
            align = 'right',
            text = '<b>Age-adjusted death rate<br>per county per year</b>',
            x = 0.95,
            y = 0.95,
        ),
        dict(
            showarrow = False,
            align = 'right',
            text = str(round(np.max(data_values),0)),
            x = 0.90,
            y = 0.85,
        ),
        dict(
            showarrow = False,
            align = 'right',
            text = str(round(np.min(data_values),0)),
            x = 0.90,
            y = 0.10,
        )]

    for i, bin in enumerate(reversed(my_colorscale)):
    	color = bin[1]
    	annotations.append(
    		dict(
    			arrowcolor = color,
    			#text = bin[0]*np.max(data_values),
    			x = 0.95,
    			y = 0.85-((i)*((0.85-0.1)/len(my_colorscale))), #0.90-(i/len(my_colorscale)),
    			ax = -30,
    			ay = 0,
    			arrowwidth = 7,
    			arrowhead = 0,
                hovertext = str(bin[0]*np.max(data_values))
    		)
    	)


    ######### plotting #########
    ### Plot data points (center of each polygon) on the map so that we can display hover information


    data_polygon_center = go.Data(
        [go.Scattermapbox(
            name=i,
            showlegend=False,
            lat=[Dict_counties_center[i][1]],
            lon=[Dict_counties_center[i][0]],
            mode='markers',
            marker=dict(size=5,color='white',opacity=0),
            hoverinfo='text',
            text=
                'Country: '+i+'<br>'+
                #'Year:    '+time.map(str)+'<br>'+
                #'DALYs:   '+round(DALYs/1000,2).map(str)+'k'+'<br>'+
                #'L_Bound: '+round(L_bound/1000,2).map(str)+'k'+'<br>'+
                #'U_Bound: '+round(U_bound/1000,2).map(str)+'k',
                'Value: '+str(data_values[ind])+'<br>'+
                'Here is the text shown when hover on a county/city'
        ) for ind,i in enumerate(selected_data.index)]
    )




    ###### Layout of the map #######

    map_layout = dict(
            height=800,
            width=700,
            autosize=True,
            hovermode='closest',
            annotations = annotations,
            mapbox=dict(
                layers=[],
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=23.67,
                    lon=121.05
                    ),

                zoom=6.8
                ),
            )

    # Add counties one by one with different fill color based on data values
    for cc in selected_data.index:
        geo_layer = dict(
                    sourcetype = 'geojson',
                    source = Dict_counties[cc],
                    type = 'fill',
                    color = Dict_colorscale[cc],
                    opacity = 0.8
        )
        map_layout['mapbox']['layers'].append(geo_layer)



    # putting all together in to a plot
    fig = dict(data=data_polygon_center, layout=map_layout)

    return fig

'''
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
'''

###### Second plot: Bar chart ############
@app.callback(
    Output('my_graph2', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_year_symbol', 'value'),
    State('my_age_symbol','value'),
    State('my_gender_symbol', 'value'),
    State('my_graph2','figure')])
def update_graph2(n_clicks, year, age, gender, figure):

    ################# Get data from user specified conditions/criteria

    '''
    This should just be a function call to get the information needed for this plot
    '''

    selected_data = df[(df['Year']==year) & (df['Age']==age) & (df['Sex']==gender)]
    selected_data.set_index('Location',inplace=True)

    Year = selected_data['Year'].unique()
    Gender = selected_data['Sex'].unique()
    Age = selected_data['Age'].unique()

    sorted_selected_data=[(ccc,vvv) for vvv,ccc in sorted(zip(list(selected_data['Value']),list(selected_data.index)), reverse=True)]

    # plotly data
    bar_chart_data = go.Data([
        go.Bar(
            y=[i[0] for i in sorted_selected_data],
            x=[i[1] for i in sorted_selected_data],
            orientation = 'h',
            #text = ,
            marker=dict(
                    color='rgb(250,70,70)',

                    line=dict(
                            color='gray',
                            width=1.5,
                            )

                        ),
            opacity=0.6
            )
    ])

    # plotly layout
    bar_chart_layout = go.Layout(
                #yaxis = dict(
                #            title='Political Regions'
                #            ),
                xaxis = dict(
                            title='Values',
                            domain=[0.1]

                            ),
                #barmode='group',
                height=800,
                width=700
    )


    # putting all together in to a plot
    fig2 = dict(data=bar_chart_data, layout=bar_chart_layout)

    return fig2









if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1',port='8002')


########################### END #########
