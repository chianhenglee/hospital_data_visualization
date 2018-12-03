

### IMPORT PACKAGES ###
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go
import pandas as pd
import numpy as np

from get_bundle_id_name import get_bundle_id_name # my funciton to get cause name from bundle ids

# We're loading pickle files saved from data_aggregation of stata data
import pickle

pd.set_option('display.width', 100)


### MAIN SCRIPT ###

# the following two lines are for deployment through Heroku
app = dash.Dash(__name__)
server = app.server

# the following line is for local setup
#app = dash.Dash()


## load data ##

file_names = ['data/ip105_i_processed.pickle',
			  'data/ip105_p_processed.pickle',
			  'data/oip105_i_processed.pickle',
			  'data/oip105_p_processed.pickle']

# give legend names for the corresponding files that we specified above.
legend_names = ['住院105_i',
                '住院105_p',
                '門診+住院_105_i',
                '門診+住院_105_p']


all_data = {}
temp_bundle_ids = []


for i,filename in zip(range(len(file_names)),file_names):

	pickling_off = open(filename,'rb')

	temp_file = pickle.load(pickling_off)

	temp_bundle_ids.append(list(temp_file.keys())) # get ids

	all_data[i] = temp_file # put into a big dictionary


	pickling_off.close()


# get cause/disease name from bundle_id
id_name_dict = get_bundle_id_name('bundle_to_cause_clinical.csv','bundle_id','cause_name')



# test 
#print(len(all_data))
#print(all_data[0][3])
#print(id_name_dict.keys())

## Get options ##

# bundle_id options
unique_sorted_bundle_ids = np.unique(np.array([item for sublist in temp_bundle_ids for item in sublist]))
bundle_id_options=[]
for b_id in unique_sorted_bundle_ids:
    
    #there may be missing id names in the csv file so I use try except for now:
    # use actual cause name when available and use the bundle id when otherwise.
    # Ideally we should go back and make sure the files corresponds to each other.
    try:
        
        ididid = str(b_id)+': '+id_name_dict[b_id]
    except:
        ididid = b_id
    
    
    bundle_id_options.append({'label':'{}'.format(ididid), 'value':b_id})

    #bundle_id_options.append({'label':'{}'.format(id_name_dict[b_id]), 'value':b_id})

# gender options
gender_options = []
for g in ['Male','Female','Both']:
    gender_options.append({'label':'{}'.format(g), 'value':g})

# age groups
all_age_groups = ['000','004','009','014','019','024','029','034','039','044','049','054','059','064','069','074','079','084','089','094','095']



## App Layout ##
app.title='NTU NBD Visualization'

app.layout = html.Div([

    ### Header ###
    html.Div([
        html.Header([
            html.Img(className='header_image',src='assets/short_logo.png'),
            html.H1(className='header_text',
                    children='國立台灣大學公共衛生學系 流行病學研究所'),

            ]),
        ],className='header_div'),

    ### Body ###
    html.Div([

        ## Title and paragraphs ##
        html.H1('National Burden of Disease Dashboard'),
        html.Div([
            html.P('This dashboard is a simple tool to visualize disease prevalence across different age groups in Taiwan.'),
            html.P('An evidence-based comparative risk assessment revealed that substantial mortality burden and premature deaths could be attributable to cardiometabolic risk factors, tobacco smoking, alcohol use, viral hepatitis, and ambient air pollution among Taiwanese adults. The study was led by Wei-Cheng Lo, a doctoral student from the College of Public Health at National Taiwan University. The investigators estimated the number of deaths and years of life lost that were attributable to 13 metabolic, lifestyle, infectious, and environmental risk factors in Taiwan. These findings were published in Population Health Metrics in May.'),
            ],className='paragraph'),

        ## Entire interactive graph section ##
        html.Div([

            # Select bundle ID #
            html.Div([
                html.H3('Select bundle_id (cause name):'),
                dcc.Dropdown(
                    className = 'dropdown',
                    id='my_bundle_id_symbol',
                    options=bundle_id_options,
                    #value='28: Meningitis',
                    placeholder='Select one',
                    multi=False
                )
            ],className='dropdown_section'),

            # Button #
            html.Button(
                id='submit-button_barcharts',
                n_clicks=0,
                children='Plot',
                className = 'the_button'
                ),

            # Graph 1 #
            dcc.Graph(
                id='my_graph',
                className='graph',
                config={'displayModeBar': False},
                figure={
                    'data': [],
                    'layout':
                        {"title": "Select bundle ID(s) and gender and start plotting",
                        "height": 720},  # px
                        },
                ),

            # Graph 2 #
            dcc.Graph(
                id='my_graph2',
                className='graph',
                config={'displayModeBar': False},
                figure={
                    'data': [],
                    'layout':
                        {"title": "Select bundle ID(s) and gender and start plotting",
                        "height": 720},  # px
                        },
                )

        ],className='entire-interactive-graph'),


    ],className='page-content'),

    ### Footer
    html.Div(
        html.Footer([
            #html.Br(),
            html.H5('2016 Taiwan National Burden of Disease'),
            html.H5('School of Public Health, National Taiwan University'),
            html.H5('2018 All rights reserved.'),
            ]
        ),
    )

])



###########################

##### callback 1: Male #####
@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button_barcharts', 'n_clicks')],
    [State('my_bundle_id_symbol', 'value')])

def update_graph_male(n_clicks, id_value):

    traces_male = [] 
	# loop through filenames and store data corresponding to each file into a trace
    for j in range(len(all_data)):
        try:
            ##### This section filters given conditions to get filtered_dataframe ######
            temp_df = all_data[j][id_value]
            # get the dataframe of the given bundle_id

            filtered_df_male = temp_df[temp_df['sex']=='1']

            # separate male and female data

    		## ADD Rows with zeros for missing age groups
    		# It is likely that in the filtered_df, there are age groups that do not have data (i.e. the dataframe simply doesnt have data for a specific age group).
    		# To deal with that, here find out which age groups are missing and add the age group in with the corresponding data (indicator) being 0.
    		# Beware that this is just for plotting purposes, not necessarily meaningful scientifically.

            dummy_list2_male = []

            for a in all_age_groups:
                if a in filtered_df_male['age_group'].values:
                    continue
                else:
                    dummy_list2_male.append([id_value,'1',a,0,0,0])


            df_temp_male=pd.DataFrame(
    							data=dummy_list2_male,
    							columns=['bundle_id', 'sex', 'age_group', 'measurement', 'enrol','indicator'])

            filtered_df_male =   filtered_df_male.append(df_temp_male,    ignore_index=True).sort_values('age_group')

    		##### Now get the data into the form for bar charts
    		# getting a list of tuples (age group,indicator)

            sorted_filtered_df_male = [(aaa,vvv) for aaa,vvv in zip(filtered_df_male['age_group'],filtered_df_male['indicator']*100)] # unit is now %

    		#print(sorted_filtered_df)
    		# trace for bar chart
    		
            trace_iter_male = go.Bar(
    			#name=file_names[j],
                name=legend_names[j],
    			#x=[jj[0] for jj in sorted_filtered_df],
    			x=['<1','1~4','5~9','10~14','15~19','20~24','25~29','30~34','35~39','40~44','45~49','50~54','55~59','60~64','65~69','70~74','75~79','80~84','85~89','90~94','>95'],
    			y=[jj[1] for jj in sorted_filtered_df_male],
    			width=0.5,
    			orientation = 'v',
    			opacity = 0.6,
    			showlegend = True)

            traces_male.append(trace_iter_male)

        except:
            pass


    bar_charts_data_male = go.Data(traces_male)

    bar_charts_layout = go.Layout(
                                #title = str(id_name_dict[id_value])+' ('+str(gender_value)+')',
    							xaxis = dict(
    										title='Age Groups (yrs old)',
    										domain=[0,1]),
    							yaxis = dict(title='Prevalence (%)'),

    							barmode='group',
    							showlegend=True,
    							height=500,
    							width=1000
    							)


    fig_male = dict(data=bar_charts_data_male, layout=bar_charts_layout)

    return fig_male


##### callback 1: Male #####
@app.callback(
    Output('my_graph2', 'figure'),
    [Input('submit-button_barcharts', 'n_clicks')],
    [State('my_bundle_id_symbol', 'value')])

def update_graph_female(n_clicks, isd_value):

    traces_female = [] 
    # loop through filenames and store data corresponding to each file into a trace
    for j in range(len(all_data)):
        try:
            ##### This section filters given conditions to get filtered_dataframe ######
            temp_df = all_data[j][id_value]
            # get the dataframe of the given bundle_id

            filtered_df_female = temp_df[temp_df['sex']=='2']

            # separate male and female data

            ## ADD Rows with zeros for missing age groups
            # It is likely that in the filtered_df, there are age groups that do not have data (i.e. the dataframe simply doesnt have data for a specific age group).
            # To deal with that, here find out which age groups are missing and add the age group in with the corresponding data (indicator) being 0.
            # Beware that this is just for plotting purposes, not necessarily meaningful scientifically.

            dummy_list2_female = []

            for a in all_age_groups:
                if a in filtered_df_female['age_group'].values:
                    continue
                else:
                    dummy_list2_female.append([id_value,'2',a,0,0,0])


            df_temp_female=pd.DataFrame(
                                data=dummy_list2_female,
                                columns=['bundle_id', 'sex', 'age_group', 'measurement', 'enrol','indicator'])

            filtered_df_female =   filtered_df_female.append(df_temp_female,    ignore_index=True).sort_values('age_group')

            ##### Now get the data into the form for bar charts
            # getting a list of tuples (age group,indicator)

            sorted_filtered_df_female = [(aaa,vvv) for aaa,vvv in zip(filtered_df_female['age_group'],filtered_df_female['indicator']*100)] # unit is now %

            #print(sorted_filtered_df)
            # trace for bar chart
            
            trace_iter_female = go.Bar(
                #name=file_names[j],
                name=legend_names[j],
                #x=[jj[0] for jj in sorted_filtered_df],
                x=['<1','1~4','5~9','10~14','15~19','20~24','25~29','30~34','35~39','40~44','45~49','50~54','55~59','60~64','65~69','70~74','75~79','80~84','85~89','90~94','>95'],
                y=[jj[1] for jj in sorted_filtered_df_female],
                width=0.5,
                orientation = 'v',
                opacity = 0.6,
                showlegend = True)

            traces_female.append(trace_iter_female)

        except:
            pass


    bar_charts_data_female = go.Data(traces_female)

    bar_charts_layout = go.Layout(
                                title = 'Female',
                                xaxis = dict(
                                            title='Age Groups (yrs old)',
                                            domain=[0,1]),
                                yaxis = dict(title='Prevalence (%)'),

                                barmode='group',
                                showlegend=True,
                                height=500,
                                width=1000
                                )


    fig2 = dict(data=bar_charts_data_female, layout=bar_charts_layout)

    return fig2






if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1',port='8000')
	











