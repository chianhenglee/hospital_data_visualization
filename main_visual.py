

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
                    children='國立台灣大學公共衛生學院'),

            ]),
        ],className='header_div'),

    ### Body ###
    html.Div([

        ## Title and paragraphs ##
        html.H1('National Burden of Disease Dashboard'),
        html.Div([
            html.P('This dashboard is a simple tool to visualize disease prevalence across different age groups in Taiwan.'),
            html.P('本研究計畫擬採用全球疾病負擔(Global Burden of Disease, GBD)的研究架構，利用台灣本土健康資料庫，推估台灣族群因罹病造成的失能、死亡、以及醫療花費負擔，並利用系統性的方法量化並比較可歸因於危險因子的疾病負擔。所有的分析都會以年齡與性別分層，並且依年度別與縣市地區別來進行，探討健康議題上社會不平等的情況。'),
            html.P('本計畫預計將建立台灣疾病負擔之健康指標資料庫，是首次將現有台灣健康資料完整盤點並加值應用的嘗試，縱向觀察不同年代國人疾病負擔發展趨勢，橫向評比地區別、族群別的危險暴露與疾病負擔分布，除了作為整體衛生政策擬定之參考之外，亦剖析台灣健康議題上社會不平等的根本原因。疾病負擔指標資料庫的建置亦成為相關延伸研究的基礎輸入(basic inputs)，除了協助評比台灣地區別重要族群健康指標(SDG, HAQ Index)之外，亦將作為評估台灣族群健康資本的重要依據，可應用於產業經濟轉型評估參考。此外，疾病負擔相關結果亦反饋全球疾病負擔計畫，補足全球疾病負擔報告中對單一國家層面報告之不足。另一方面，透過台灣族群疾病負擔的評估，將作為未來衛生政策的策略擬定更多元的參考價值，提供以證據導向(evidence-based)為基礎的衛生政策規劃，補充目前政策擬定架構之不足。'),
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
            #html.H5('2018 All rights reserved.'),
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
                                title = str(id_name_dict[id_value])+' (Male)',
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


##### callback 2: Female #####
@app.callback(
    Output('my_graph2', 'figure'),
    [Input('submit-button_barcharts', 'n_clicks')],
    [State('my_bundle_id_symbol', 'value')])

def update_graph_female(n_clicks, id_value):

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
                                #title = str(id_name_dict[id_value])+' ('+str(gender_value)+')',
                                title = str(id_name_dict[id_value])+' (Female)',
                                xaxis = dict(
                                            title='Age Groups (yrs old)',
                                            domain=[0,1]),
                                yaxis = dict(title='Prevalence (%)'),

                                barmode='group',
                                showlegend=True,
                                height=500,
                                width=1000
                                )


    fig_female = dict(data=bar_charts_data_female, layout=bar_charts_layout)

    return fig_female






if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1',port='8000')
	











