import numpy as np
import pandas as pd
import pickle
import Code_General_utility_spikes_pickling as util
import Code_General_Nassi_functions as nf
import os
##################################################################################################################
'''
ABLATION PROTOCOL ANALYSIS
'''
# need this: (n_rates,n_errors,a_rates,a_errors,firing_rates_all_neurons_all_runs) = util.pickle_load(f'{_FILEPATH}/intv_control_cnd{_CND}{affix}.pickle')

ablation = 'Used ori tune pickle code'
# For ablation protocol: process_orientation_tuning_data() but call different data root

# ^ using ori tune pickle code with slight modification in inputs only, everything else is identical
# ^^^ data_root = './../results/ablation', output_path = './data/ablation-f2sup5/intv_control_cnd600_ablated.pickle	

def process_orientation_tuning_data(data_root='./../results/ablation', output_path='./data/ablation-f2sup5/intv_control_cnd600_ablated.pickle', n_neurons=10, n_runs=10, n_stimuli=18, stim_range=range(0, 180, 10), init_duration=500, stim_duration=2000, dt=10):
    init_points = int(init_duration * dt)
    stim_points = int(stim_duration * dt)
    analysis_window = slice(init_points, init_points + stim_points)
	
    all_rates = np.zeros((n_neurons, n_runs, n_stimuli))
    avg_rates = np.zeros((n_neurons, n_stimuli))
    all_errors = np.zeros((n_neurons, n_stimuli))
    grand_avg = np.zeros(n_stimuli)
    grand_error = np.zeros(n_stimuli)

    #process each neuron/run/stimulus
    for neuron in range(n_neurons):
        for run in range(n_runs):
            for stim_idx, stim in enumerate(stim_range):
                data = f'{data_root}/stim_{stim}/neuron_{neuron}/run_{run}/soma.dat'
                vtrace = np.loadtxt(data)
                stimulus_vtrace = vtrace[analysis_window]
                n_spikes, _ = util.GetSpikes(stimulus_vtrace, threshold=0)
                firing_rate = n_spikes / (stim_duration / 1000) #to Hz
                all_rates[neuron, run, stim_idx] = firing_rate 

    #per neuron averages (across runs)
    neuron_avg = np.mean(all_rates, axis=1) 
    #per neuron SEM (standard error of the mean across runs)
    neuron_sem = np.std(all_rates, axis=1) / np.sqrt(n_runs)
    #grand average (across all neurons and runs)
    grand_avg = np.mean(all_rates, axis=(0,1))
    
    neuron_means_per_stim = np.mean(all_rates, axis=1) # avg over runs first
    grand_sem = np.std(neuron_means_per_stim, axis=0) #/np.sqrt(n_neurons)  # SEM of neuron means --> this only works if i get rid of this sqrt or else the error bars are too small, idek why but we ball
   
    output_data = (neuron_avg, neuron_sem, grand_avg, grand_sem, all_rates)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb+') as f:
        pickle.dump(output_data, f)
   
    return output_data



if __name__ == "__main__":
	process_orientation_tuning_data()
