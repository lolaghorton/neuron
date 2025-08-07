import numpy as np
import pandas as pd
import pickle
from scipy.stats import circmean
import Code_General_utility_spikes_pickling as util
import Code_General_Nassi_functions as nf
import os
from glob import glob
import time

'''
ITERATIVE PAIRED PULSE (I3P) ANALYSIS
'''
#pickling raw data so itll be read correctly into petousakis's plotting (and analysis - for this experiment only) 
def process_i3p_data(root_path, num_dends=50, num_syns=200):
	data = np.zeros((num_dends, num_syns, 5001))
	
	for dend_id in range(num_dends):
		if dend_id < 7:
			dend_type = 'basal'
			dend_num = dend_id
		else:
			dend_type = 'apical'
			dend_num = dend_id - 7
   
		for syn_id in range(1, num_syns+1):
			basal_path = f"{root_path}/valcrit_{dend_id}/scalefctr_{syn_id}/basal{dend_num}.dat"
			apical_path = f"{root_path}/valcrit_{dend_id}/scalefctr_{syn_id}/apical{dend_num}.dat"
            
			if dend_type == 'basal' and os.path.exists(basal_path):
				trace = np.loadtxt(basal_path)
			elif dend_type == 'apical' and os.path.exists(apical_path):
				trace = np.loadtxt(apical_path)
			else:
				raise FileNotFoundError(f"No {dend_type} file found for dendrite {dend_id} at {syn_id} synapses")
			
			#truncate my data to 5001 points bc i ran it too long
			if len(trace) > 5001:
				print(f'Truncating dendrite {dend_id} synapse {syn_id} from {len(trace)} to 5001 points')
				trace = trace[:5001]
			elif len(trace) < 5001:
				raise ValueError(f'Trace too short to truncate for dendrite {dend_id} synapse {syn_id} with trace {len(trace)} points')
			else:
				print(f'Trace already 5001 points for dendrite {dend_id} synapse {syn_id}')

			data[dend_id, syn_id-1] = trace  #synapses 1-200 stored as 0-199
	return data



if __name__ == "__main__":
	nmda_data = process_i3p_data(f"./../results/i3p-brokenup/valna_0")
	na_data = process_i3p_data(f"./../results/i3p-brokenup/valna_1")

	with open('./data/i3p-f1/Data_F1_F6_S1_NMDA_noNa_responses.pickle', 'wb+') as f:
		pickle.dump(nmda_data, f)
	
	with open('./data/i3p-f1/Data_F1_F6_S1_Na_responses.pickle', 'wb+') as f:
		pickle.dump(na_data, f)
		
