

### IMPORT PACKAGES ###
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go
import pandas as pd
import numpy as np

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

all_data = {}
temp_bundle_ids = []


for i,filename in zip(range(len(file_names)),file_names):

	pickling_off = open(filename,'rb')

	temp_file = pickle.load(pickling_off)

	temp_bundle_ids.append(list(temp_file.keys())) # get ids

	all_data[i] = temp_file # put into a big dictionary


	pickling_off.close()


# test 
#print(len(all_data))
#print(all_data[0][3])


## Get options ##

# bundle_id options
unique_sorted_bundle_ids = np.unique(np.array([item for sublist in temp_bundle_ids for item in sublist]))
bundle_id_options=[]
for b_id in unique_sorted_bundle_ids:
    bundle_id_options.append({'label':'{}'.format(b_id), 'value':b_id})

# gender options
gender_options = []
for g in ['Male','Female','Both']:
    gender_options.append({'label':'{}'.format(g), 'value':g})

# age groups
all_age_groups = ['000','004','009','014','019','024','029','034','039','044','049','054','059','064','069','074','079','084','089','094','095']



## App Layout ##

app.layout = html.Div([
    html.H1('Lulu Lulu Lulu Dashboard',style={'marginLeft':'20px'}),
    html.Div([
        html.H3('Select bundle_id:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_bundle_id_symbol',
            options=bundle_id_options,
            #value='Taiwan',
            placeholder='Select one',
            multi=False
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'80%','marginLeft':'20px'}),
    
    html.Div(),

    html.Div([
        html.H3('Select gender:', style={'paddingRight':'0px'}),
        dcc.Dropdown(
            id='my_gender_symbol',
            options=gender_options,
            #value='Taiwan',
            placeholder='Select one',
            multi=False
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'80%','marginLeft':'20px'}),
    
    html.Div(),
    html.Div(),

    html.Div([
        html.Button(
            id='submit-button_barcharts',
            n_clicks=0,
            children='Plot them out!',
            style={'fontSize':20, 'marginLeft':'20px'}
        ),
    ], style={'display':'inline-block'}),
    
    dcc.Graph(
        id='my_graph',
        figure={
            'data': [],
#                {'x': [], 'y': []}
 #           ],
            'layout':
                {"title": "Select bundle ID(s) and gender and start plotting",
                 "height": 720},  # px
        }
    )
])


###########################
@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button_barcharts', 'n_clicks')],
    [State('my_bundle_id_symbol', 'value'),
    State('my_gender_symbol', 'value')])

def update_graph(n_clicks, id_value, gender_value):

    traces = [] 
	# loop through filenames and store data corresponding to each file into a trace
    for j in range(len(all_data)):

    	try:
	    	##### This section filters given conditions to get filtered_dataframe ######
    		temp_df = all_data[j][id_value] # get the dataframe of the given bundle_id
    		# filter gender (note that in the dataframe the column name for gender is sex)
    		#				(also, both age_ihmec and sex columns are using string, not numbers)
    		if gender_value=='Male':
    			filtered_df = temp_df[temp_df['sex']=='1'] # '1' and '2' are used in original dataframes

    		elif gender_value=='Female':
    			filtered_df = temp_df[temp_df['sex']=='2']

    		else: # the case where gender is 'both' (here I call it '3')
    			  # This case we have to combine values for different genders to get new values.
    			print('Selected both gender!')
    			dummy_list=[]
    			for temp_age in temp_df['age_group'].unique():
    				print(temp_age)
    				t_a_data = temp_df.loc[temp_df['age_group']==temp_age]
    				# the above line gets a dataframe of two rows (male and female of the same id and age group, and now we just need to recalculate the indicator and combine them)
    				t_a_meas_sum = t_a_data['measurement'].sum()
    				t_a_enrol_sum = t_a_data['enrol'].sum()
    				t_a_indicator = t_a_meas_sum/t_a_enrol_sum

    				dummy_list.append([id_value,'3',temp_age,t_a_meas_sum,t_a_enrol_sum,t_a_indicator])

    			filtered_df = pd.DataFrame(
                                        data=dummy_list,
                                        columns=['bundle_id', 'sex', 'age_group', 'measurement', 'enrol','indicator'])
    		print('line 171')
    		print(filtered_df)

    		## ADD Rows with zeros for missing age groups
    		# It is likely that in the filtered_df, there are age groups that do not have data (i.e. the dataframe simply doesnt have data for a specific age group).
    		# To deal with that, here find out which age groups are missing and add the age group in with the corresponding data (indicator) being 0.
    		# Beware that this is just for plotting purposes, not necessarily meaningful scientifically.
    		dummy_list2 = []
    		for a in all_age_groups:

    			if a in filtered_df['age_group'].values:
    				continue# not need to do anything
    			else:
    				if gender_value=='Male':
    					ggg='1'
    				elif gender_value=='Female':
    					ggg='2'
    				else:
    					ggg='3'

    				print('creading zeros row')
    				dummy_list2.append([id_value,ggg,a,0,0,0])

    		df_temp=pd.DataFrame(
    							data=dummy_list2,
    							columns=['bundle_id', 'sex', 'age_group', 'measurement', 'enrol','indicator'])

    		filtered_df = filtered_df.append(df_temp,ignore_index=True).sort_values('age_group')

    		print('dummy zeros dataframe')
    		print(df_temp)

    		#print('Appended filtered_df')
    		#print(filtered_df)







    		##### Now get the data into the form for bar charts
    		# getting a list of tuples (age group,indicator)
    		sorted_filtered_df = [(aaa,vvv) for aaa,vvv in zip(filtered_df['age_group'],filtered_df['indicator']*100)] # unit is now %
    		#print(sorted_filtered_df)
    		# trace for bar chart
    		
    		trace_iter = go.Bar(
    			name=file_names[j],
    			#x=[jj[0] for jj in sorted_filtered_df],
    			x=['<1','1~4','5~9','10~14','15~19','20~24','25~29','30~34','35~39','40~44','45~49','50~54','55~59','60~64','65~69','70~74','75~79','80~84','85~89','90~94','>95'],
    			y=[jj[1] for jj in sorted_filtered_df],
    			width=0.5,
    			orientation = 'v',
    			opacity = 0.6,
    			showlegend = True)

    		traces.append(trace_iter)




    	except:
    		pass


    bar_charts_data = go.Data(traces)

    bar_charts_layout = go.Layout(
    							xaxis = dict(
    										title='Age Groups',
    										domain=[0.1]),
    							yaxis = dict(title='Indicator (%)'),

    							barmode='group',
    							showlegend=True,
    							height=700,
    							width=1450
    							)


    fig = dict(data=bar_charts_data, layout=bar_charts_layout)

    return fig





if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1',port='8000')
	











