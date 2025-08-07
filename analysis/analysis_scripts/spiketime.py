import os
import numpy as np
import Code_General_utility_spikes_pickling as util
import Code_General_Nassi_functions as nf
"""
Spike timing extraction for ionic intervention protocol
Output format in txt: neuron run spike_number time_ms
"""
cond = 'even'
stim = '90'

def extract_spikes(BASE_PATH = f"./../results/{cond}-preint-sttx/stim_{stim}", OUTPUT_FILE = f"./data/ionint-f3/preint-times/{cond}-{stim}-timings-sttx.txt", DT = 0.1, DURATION = 2500, THRESHOLD = -20):	
	
    with open(OUTPUT_FILE, 'w') as out_f:
        #out_f.write("neuron run spike_number time_ms\n")
       
        for neuron in range(10):
            for run in range(10):
                dat_file = f"{BASE_PATH}/neuron_{neuron}/run_{run}/soma.dat"
               
                if not os.path.exists(dat_file):
                    print(f"Missing file/no spikes within: {dat_file}")
                    continue
               
                #load trace (single column)
                try:
                    voltage = np.loadtxt(dat_file)
                except Exception as e:
                    print(f"Error loading {dat_file}: {str(e)}")
                    continue
               
                #get the spikes
                n_spikes, spike_indices = util.GetSpikes(voltage, threshold=THRESHOLD, detection_type='max')
               
                #convert to times
                for i, idx in enumerate(spike_indices, 1):
                    spike_time = idx * DT  #sample index into ms
                    if spike_time > DURATION:
                        continue  #skips if beyond sim duration
                   
                    out_f.write(f"{neuron} {run} {i} {spike_time:.3f}\n")
               
                print(f"Neuron {neuron} Run {run}: {n_spikes} spikes found")


def extract_spikes_500ms(BASE_PATH = f"./../results/{cond}-preint-sttx/stim_{stim}", OUTPUT_FILE = f"./data/preint-times/{cond}-{stim}-timings-500ms-sttx.txt", DT = 0.1, INIT_DUR = 500, DURATION = 2500, THRESHOLD = 0):	
	
    with open(OUTPUT_FILE, 'w') as out_f:
        #out_f.write("neuron run spike_number time_ms\n")
       
        for neuron in range(50):
            for run in range(10):
                dat_file = f"{BASE_PATH}/neuron_{neuron}/run_{run}/soma.dat"
                
                if not os.path.exists(dat_file):
                    print(f"Missing file: {dat_file}")
                    continue
               
                # Load voltage trace (assumes single-column format)
                try:
                    voltage = np.loadtxt(dat_file)
                except Exception as e:
                    print(f"Error loading {dat_file}: {str(e)}")
                    continue
               
                # Detect spikes
                n_spikes, spike_indices = util.GetSpikes(voltage, threshold=THRESHOLD, detection_type='max')
               
                # Filter and record spikes after INIT_DUR
                spike_count = 0
                for idx in spike_indices:
                    spike_time = idx * DT  # convert index to ms
                    if INIT_DUR < spike_time <= DURATION:
                        spike_count += 1
                        out_f.write(f"{neuron} {run} {spike_count} {spike_time:.3f}\n")
               
                print(f"Neuron {neuron} Run {run}: {spike_count} spikes after {INIT_DUR} ms")

##################################################################################################################
'''
this one is for the syn int pre int spikes, which since ttx isnt turned on, its just bio disp 0 like ori tune
basically same but added a stim column. new output: stim neuron run spike_num spike_time
'''

def extractspikes_stims(BASE_PATH = f"./../results/bio-preint-sttx", OUTPUT_FILE = f"./data/synint-f4/syn-preint-20.txt", DT = 0.1, DURATION = 2500, THRESHOLD = -20):	
	
    with open(OUTPUT_FILE, 'w') as out_f:
        #out_f.write("neuron run spike_number time_ms\n")
        
        stim_range = range(0, 180, 10)
        
        for stim in stim_range:
        	for neuron in range(10):
        		for run in range(10):
        			dat_file = f"{BASE_PATH}/stim_{stim}/neuron_{neuron}/run_{run}/soma.dat"
        			
        			if not os.path.exists(dat_file):
        				print(f"Missing file/no spikes within: {dat_file}")
        				continue
        				
        			#load trace (single column)
        			try:
        				voltage = np.loadtxt(dat_file)
        			except Exception as e:
        				print(f"Error loading {dat_file}: {str(e)}")
        				continue
        				
        			#get the spikes
        			n_spikes, spike_indices = util.GetSpikes(voltage, threshold=THRESHOLD, detection_type='max')
        			
        			#convert to times
        			for i, idx in enumerate(spike_indices, 1):
        				spike_time = idx * DT  #sample index into ms
        				if spike_time > DURATION:
        					continue  #skips if beyond sim duration
        				
        				out_f.write(f"{stim} {neuron} {run} {i} {spike_time:.3f}\n")
        				
        			print(f"Stim {stim} Neuron {neuron} Run {run}: {n_spikes} spikes found")

         
if __name__ == "__main__":
#for ionic intervention    
    #extract_spikes()
    #extract_spikes_500ms()      #didnt end up being the correct one i needed, but function works if needed
    
#for synaptic intervention
	extractspikes_stims()        #did for syn int, then also used this again for pre ion int with all stims just in case
	
