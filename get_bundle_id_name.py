
def get_bundle_id_name(filename,bundle_id_column_name,disease_column_name):
	'''this funciton reads the file of a csv table of bundle_id and cause_name
	and returns a dictionary with the keys being bundle ids and values being the cause names

	filename is the name of the file
	usecols is a list of column names (str) 
	'''

	import pandas as pd

	#raw_df = pd.read_csv('bundle_to_cause_clinical.csv',usecols=['bundle_id','cause_name'])
	raw_df = pd.read_csv(filename,usecols=[bundle_id_column_name,disease_column_name])
	raw_df.drop_duplicates(keep='first',inplace=True)


	id_names = {}
	for i in range(len(raw_df)):

		bundle_id=raw_df.iloc[i][bundle_id_column_name]
		name=raw_df.iloc[i][disease_column_name]
		id_names[bundle_id]=name


	return id_names





