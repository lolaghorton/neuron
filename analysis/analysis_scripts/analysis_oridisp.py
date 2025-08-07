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
ORIENTATION DISPARITY PROTOCOL ANALYSIS
'''
def calc_expected_preferences(output_path='./Data_F3_expectation_lines.pickle'):
    #shape (1, 3, 10) for 3 conditions and 10 disparities
    expected_prefs = np.zeros((1, 3, 10))

    condition_weights = {600: (0.4, 0.6), 500: (0.5, 0.5), 400: (0.6, 0.4)}
   
    for cond_idx, (cnd, (basal_w, apical_w)) in enumerate(condition_weights.items()):
        for disp in range(10):
            basal_pref = disp * 10
            apical_pref = 0
           
            basal_vec = np.array([np.cos(np.radians(basal_pref)),
                                np.sin(np.radians(basal_pref))])
            apical_vec = np.array([np.cos(np.radians(apical_pref)),
                                 np.sin(np.radians(apical_pref))])
           
            weighted_vec = basal_w*basal_vec + apical_w*apical_vec
            expected_pref = np.degrees(np.arctan2(weighted_vec[1], weighted_vec[0]))
           
            #map to -90 to 90
            if expected_pref > 90:
                expected_pref -= 180
            elif expected_pref < -90:
                expected_pref += 180
               
            expected_prefs[0, cond_idx, disp] = expected_pref

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(expected_prefs, f)
       
    return expected_prefs
#^ only realized after getting correct prefs that the exp line is slightly off, leaving it tbh

# this one has to be run 3 seperate times while changing the data_root (bio/even/inverse locations), and output path cnd number (400/500/600). Give the correct disparity rates, but doesnt do osi/wdith calculations to see which neurons are accepted or rejected 
def process_disp_unfilter(data_root='./../results/inverse_oridisp', output_path='./data/oridisp-f2def/cnd400_neuron_disparity_rates_unfiltered.pickle', n_neurons=10, n_runs=10, n_disparities=10, n_stimuli=18, init_duration=500, stim_duration=2000, dt=10):
	
    init_points = int(init_duration * dt)  
    stim_points = int(stim_duration * dt)
    analysis_window = slice(init_points, init_points + stim_points)

    #[disparity][neuron][stimulus]
    all_rates = [[[] for _ in range(n_neurons)] for _ in range(n_disparities)]

    for disp in range(n_disparities):
        disp_dir = f'{data_root}/disp_{disp*10}'
        
        for neuron in range(n_neurons):
            neuron_rates = np.zeros((n_runs, n_stimuli))
            
            for run in range(n_runs):
            
                for stim_idx in range(n_stimuli):
                    data_file = f'{disp_dir}/stim_{stim_idx*10}/neuron_{neuron}/run_{run}/soma.dat'
                    
                    if os.path.exists(data_file):
                        vtrace = np.loadtxt(data_file)
                        stimulus_vtrace = vtrace[analysis_window]
                        n_spikes, _ = util.GetSpikes(stimulus_vtrace, threshold=0)
                        firing_rates = (n_spikes / (stim_duration / 1000))
                        neuron_rates[run, stim_idx] = firing_rates
           
            all_rates[disp][neuron] = np.mean(neuron_rates, axis=0) #avg across runs

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb+') as f:
        pickle.dump(all_rates, f)
   
    return all_rates

#from the above data, need to filter out neurons that dont fit criteria (OSI<0.2 & width>80 are rejected)
#ok this isnt perfect but does get 0-40 good, 50 removed correct 2, 60+ removed 3+ nrns which fails test
def process_disp_filter(data_root='./../results/even_oridisp', output_path='./data/oridisp-f2def/cnd500_neuron_disparity_rates_filtered.pickle', n_neurons=10, n_runs=10, n_disparities=10, n_stimuli=18, init_duration=500, stim_duration=2000, dt=10):
	
    init_points = int(init_duration * dt)  
    stim_points = int(stim_duration * dt)
    analysis_window = slice(init_points, init_points + stim_points)

    #[disparity][neuron][stimulus]
    all_rates = [[[] for _ in range(n_neurons)] for _ in range(n_disparities)]
    accepted_neurons = []

    for disp in range(n_disparities):
        disp_dir = f'{data_root}/disp_{disp*10}'
        
        for neuron in range(n_neurons):
            neuron_rates = np.zeros((n_runs, n_stimuli))
            
            for run in range(n_runs):
                for stim_idx in range(n_stimuli):
                    data_file = f'{disp_dir}/stim_{stim_idx*10}/neuron_{neuron}/run_{run}/soma.dat'
                    
                    if os.path.exists(data_file):
                        vtrace = np.loadtxt(data_file)
                        stimulus_vtrace = vtrace[analysis_window]
                        n_spikes, _ = util.GetSpikes(stimulus_vtrace, threshold=0)
                        firing_rates = (n_spikes / (stim_duration / 1000))
                        neuron_rates[run, stim_idx] = firing_rates
            
            avg_rates = np.mean(neuron_rates, axis=0)  #avg across runs
            nrn_pref, nrn_OSI, nrn_width, _, _ = nf.tuning_properties(avg_rates, [x*10 for x in range(0, n_stimuli)])
            if nrn_OSI < 0.2 or nrn_width > 80 or np.isnan(nrn_OSI):
                verdict = 'REJECT'
            else:
                verdict = 'ACCEPT'
                accepted_neurons.append(neuron)

            print(f'Disparity {disp*10} | Neuron {neuron} - Pref: {nrn_pref}, OSI: {nrn_OSI:.3f}, Width: {nrn_width} | {verdict}')
            
            #save firing rates for accepted neurons
            if verdict == 'ACCEPT':
                all_rates[disp][neuron] = avg_rates
	
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb+') as f:
        pickle.dump(all_rates, f)

    print(f'Accepted {len(accepted_neurons)} neurons out of {n_neurons*n_disparities}.')
    return all_rates, accepted_neurons




if __name__ == "__main__":
	#calc_expected_preferences() 
	#process_disp_unfilter()
	#process_disp_filter()

