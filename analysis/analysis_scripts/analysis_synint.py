import numpy as np
import pandas as pd
import pickle
import Code_General_utility_spikes_pickling as util
import Code_General_Nassi_functions as nf
import os
from collections import defaultdict

'''
SYNAPTIC INTERVENTION PROTOCOL ANALYSIS
'''

'''4a'''
#for figure 4a, its original ori tune, and two other ori tunes with either apical or basal stim driven synapes turned off. So just used ori tune code for both of those. 
# ^^^ data_root = './../results/synint-4a-apical or basal', output_path = './data/synint-f4/4a/intv_control_cnd600_delFB_nsA.pickle or intv_control_cnd600_delFB_nsB.pickle
fig4a = 'synint apical or basal stim synapes nullified - used ori tune pickle code'
# For synaptic intervention protocol: process_orientation_tuning_data() for 4a only

'''4 b and c'''
preint_spikes = 'the spike timings of the pre inttervention function is in another doc called spiketime.py'

# need 3 files
# 1. intv_control_cnd600_delFB.pickle: nrn avg, nrn sem, grand avg, grand sem, all control rates
# from orientation disparity (disp=0) data, but need to take out any entries that didnt have a pre intervention spike
# control data ./../results/orientation_disp/bio_oridisp/disp_0/ then stim neuron run
# pre spikes ./data/synint-4a/syn-preint-20.txt

def load_spike_timings(timings_file):
    """Load pre-intervention spike timings from file."""
    spike_data = []
    with open(timings_file, 'r') as f:
        for line in f:
            stim, neuron, run, spike_num, time_ms = line.strip().split()
            spike_data.append({
            	'stim': int(stim),
                'neuron': int(neuron),
                'run': int(run),
                'spike_num': int(spike_num),
                'time': float(time_ms)
            })
    return spike_data

def ctrl_filtered(data_root="./../results/bio-preint-sttx", 
                 output_path="./data/synint-f4/intv_control_cnd600_delFB.pickle", 
                 init_duration=500, stim_duration=2000, dt=10):
    '''Process only control data that matches the spike timings file'''
    init_points = int(init_duration * dt)
    stim_points = int(stim_duration * dt)
    analysis_window = slice(init_points, init_points+stim_points)
    
    # Load spike timings to get valid (stim, neuron, run) combinations
    spike_data = load_spike_timings("./data/synint-f4/syn-preint-20.txt")
    
    # Create a set of all unique (stim, neuron, run) combinations from spike data
    valid_combinations = {(s['stim'], s['neuron'], s['run']) for s in spike_data}
    
    # Initialize arrays with NaN
    n_stimuli = 18  # 0-170 in steps of 10 → 18 stimuli
    n_neurons = 10
    n_runs = 10
    
    all_rates = np.empty((n_neurons, n_runs, n_stimuli))
    
    # Create stimulus value to index mapping
    stim_values = sorted({s['stim'] for s in spike_data})  # [0, 10, 20, ..., 170]
    stim_to_idx = {stim: idx for idx, stim in enumerate(stim_values)}
    
    # Process only the combinations that exist in spike data
    for stim, nrn, run in valid_combinations:
        data_file = f"{data_root}/stim_{stim}/neuron_{nrn}/run_{run}/soma.dat"
        if not os.path.exists(data_file):
        	print(f"missing control file: {data_file}")
        	continue
        
        if os.path.exists(data_file):
            try:
                vtrace = np.loadtxt(data_file)
                stim_vtrace = vtrace[analysis_window]
                n_spikes, _ = util.GetSpikes(stim_vtrace, threshold=0)
                firing_rate = n_spikes / (stim_duration/1000)
                
                # Map stimulus value to array index
                stim_idx = stim_to_idx[stim]
                all_rates[nrn, run, stim_idx] = firing_rate
                
            except Exception as e:
                print(f"Error processing {data_file}: {e}")
                continue
    
    # Calculate statistics while ignoring NaN values
    valid_counts = np.sum(~np.isnan(all_rates), axis=1)
    neuron_avg = np.nanmean(all_rates, axis=1)
    neuron_sem = np.nanstd(all_rates, axis=1) / np.sqrt(valid_counts)
    
    grand_avg = np.nanmean(all_rates)
    #neuron_means_per_stim = np.nanmean(all_rates, axis=1)
    grand_sem = np.nanstd(neuron_avg) / np.sqrt(np.sum(~np.isnan(neuron_avg)))
    
    output_data = (neuron_avg, neuron_sem, grand_avg, grand_sem, all_rates)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the data
    with open(output_path, 'wb+') as f:
        pickle.dump(output_data, f)
    
    return output_data


# 2. pre_intervention_spike_timings_revisions_syn_intv.pickle: key of 600-nrn-run-stim-time (add spike) and then dictionary of just the time again
def timings_pickle(output_path="./data/synint-f4/pre_intervention_spike_timings_revisions_syn_intv.pickle",
                   timings_file="./data/synint-f4/syn-preint-20.txt",
                   dt=0.1):
    """Create the pre-intervention spike timing pickle file in points."""
    
    spike_data = load_spike_timings(timings_file)
    timings_dict = {}
    
    for spike in spike_data:
        time_pts = int(spike['time'] / dt)
        key = f"600-{spike['neuron']}-{spike['run']}-{spike['stim']}-{spike['spike_num']}-{time_pts}"
        timings_dict[key] = [0, time_pts]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(timings_dict, f)
    
    return timings_dict






######################################################################################################################
'''4b - 50% stim driven synapses'''
# 3. spike_survival_verdicts_revisions_syn_intv.pickle: has key 600-nrn-run-stim (will prob have to add spike) and the dictionary anull bnull verdict where its 1 survived 0 not then the verdict from that

def check_synaptic_survival(intervention_type, neuron, run, stim, spike_time, dt=0.1):
    """Check if spike survived intervention by looking near original spike time."""
    base_path = f'./../results/synint-50/identifier_{intervention_type}'
    soma_file = f'{base_path}/stim_{stim}/neuron_{neuron}/run_{run}/spike_*'  # Any spike dir

    # Find the directory with matching spike_num if needed
    candidate_dirs = os.listdir(f'{base_path}/stim_{stim}/neuron_{neuron}/run_{run}/')
    matching_dir = None
    for d in candidate_dirs:
        if d.startswith("spike_"):
            test_path = f'{base_path}/stim_{stim}/neuron_{neuron}/run_{run}/{d}/soma.dat'
            if os.path.exists(test_path):
                matching_dir = d
                break

    if matching_dir is None:
    	print(f"spike returned none (n-{neuron}, r-{run}, st-{stim})")
    	return None
    
    soma_file = f'{base_path}/stim_{stim}/neuron_{neuron}/run_{run}/{matching_dir}/soma.dat'

    try:
        vtrace = np.loadtxt(soma_file)
        if len(vtrace) == 0:
        	print(f"spike returned none (n-{neuron}, r-{run}, st-{stim})")
        	return None

        center_idx = int(spike_time / dt)
        window_half = int(1 / dt)  # ±2.5 ms → 50 points each side
        pre_idx = center_idx - window_half
        post_idx = center_idx + window_half

        if pre_idx < 0 or post_idx > len(vtrace):
        	print(f"spike returned none (n-{neuron}, r-{run}, st-{stim})")
        	return None

        vtrace_window = vtrace[pre_idx:post_idx]
        n_spikes, _ = util.GetSpikes(vtrace_window, threshold=10, detection_type='max')
        survived = n_spikes > 0
        if survived is True:
            print(f"Spike survived ({intervention_type}) (neuron {neuron} run {run})")
        else:
        	print(f"Spike died ({intervention_type}) (neuron {neuron} run {run})")
        return survived
        #return n_spikes > 0

    except Exception as e:
        print(f"Error reading {soma_file}: {e}")
        return None


'''
def check_synaptic_survival(neuron, run, stim, spike_num, spike_time, intervention_type, dt=0.1):
    """Check if spike survived synaptic intervention by reading voltage trace."""
    base_path = f'./../results/synint-50/identifier_{intervention_type}'
    soma_file = f'{base_path}/stim_{stim}/neuron_{neuron}/run_{run}/spike_{spike_num}/soma.dat'
    
    if not os.path.exists(soma_file):
        print(f"Missing file: {soma_file}")
        return None

    try:
        vtrace = np.loadtxt(soma_file)
        if len(vtrace) == 0:
            return None

        pre_ms, post_ms = 5, 5
        pre_idx = int((spike_time - pre_ms) / dt)
        post_idx = int((spike_time + post_ms) / dt)

        if pre_idx < 0 or post_idx > len(vtrace):
            print(f"Spike window [{pre_idx}:{post_idx}] out of bounds in {soma_file}")
            return None

        vtrace_window = vtrace[pre_idx:post_idx]
        n_spikes, _ = util.GetSpikes(vtrace_window, threshold=-20, detection_type='max')
        survived = n_spikes > 0
        if survived is True:
            print(f"Spike {spike_num} ({intervention_type}) survived (neuron {neuron}, run {run}, stim {stim})")
        else:
        	print(f"spike {spike_num} ({intervention_type}) died (neuron {neuron} run {run} stim {stim})")
        return survived

    except Exception as e:
        print(f"Error reading {soma_file}: {e}")
        return None
'''



def process_synaptic_interventions(timings_file, dt=0.1):
    """Process synaptic intervention outcomes and classify spike survivals."""
    verdicts = {}
    spike_counts = defaultdict(int)

    spike_data = load_spike_timings(timings_file)
    print(f"🔍 Processing {len(spike_data)} pre-intervention spikes...")

    for spike in spike_data:
        time_pts = int(spike['time'] / dt)
        key = f"600-{spike['neuron']}-{spike['run']}-{spike['stim']}-{spike['spike_num']}-{time_pts}"

        apical_survived = check_synaptic_survival(-1, spike['neuron'], spike['run'], spike['stim'], spike['time'], dt)
        basal_survived = check_synaptic_survival(1, spike['neuron'], spike['run'], spike['stim'], spike['time'], dt)

        if apical_survived is None or basal_survived is None:
        	print(f"spike returned none (n-{spike['neuron']}, r-{spike['run']}, st-{spike['stim']}, sp-{spike['spike_num']})")
        	continue

        # Classify survival
        if basal_survived is False and apical_survived is False:
            verdict = 'unstable'
        elif apical_survived is True and basal_survived is False:
            verdict = 'basal'
        elif not basal_survived is True and apical_survived is False:
            verdict = 'apical'
        else:
            verdict = 'bistable'
        

        verdicts[key] = {
            'Anull': int(apical_survived),
            'Bnull': int(basal_survived),
            'Verdict': verdict
        }
        spike_counts[verdict] += 1

    print("\n✅ Spike survival counts:")
    for verdict, count in spike_counts.items():
        print(f"{verdict:10}: {count}")

    return verdicts

'''
def process_synaptic_interventions():
    timings_file = './data/synint-f4/syn-preint-20.txt'
    verdicts = {}
    spike_counts = {'total': 0, 'apical': 0, 'basal': 0, 'unstable': 0, 'bistable': 0}

    if not os.path.exists(timings_file):
        print(f"Missing timings file: {timings_file}")
        return verdicts

    spike_data = load_spike_timings(timings_file)
    print(f"Processing {len(spike_data)} pre-intervention spikes...")

    for spike in spike_data:
        neuron = spike['neuron']
        run = spike['run']
        stim = spike['stim']
        spike_num = spike['spike_num']
        spike_time = spike['time']
        cond_code = '600'  # hardcoded for plotting
        key = f'{cond_code}-{neuron}-{run}-{stim}-{spike_num}-{int(spike_time/0.1)}'

        apical_survived = check_synaptic_survival(neuron, run, stim, spike_num, spike_time, -1)
        basal_survived  = check_synaptic_survival(neuron, run, stim, spike_num, spike_time, +1)

        if apical_survived is None or basal_survived is None:
            print(f"Skipping spike {key} (missing data)")
            continue

        if apical_survived is False and basal_survived is False:
            verdict = 'unstable'
        elif apical_survived is True and basal_survived is False:
            verdict = 'basal'
        elif basal_survived is True and apical_survived is False:
            verdict = 'apical'
        else:
            verdict = 'bistable'

        if key not in verdicts:
            verdicts[key] = {'Verdict': [], 'Timings': []}

        verdicts[key]['Verdict'].append(verdict)
        verdicts[key]['Timings'].append(spike_time)
        spike_counts[verdict] += 1
        spike_counts['total'] += 1

    print(f"\nClassification summary:")
    for vtype in ['apical', 'basal', 'unstable', 'bistable']:
        count = spike_counts[vtype]
        frac = (count / spike_counts['total']) * 100 if spike_counts['total'] > 0 else 0
        print(f"  {vtype.capitalize():<9}: {count:>4} spikes ({frac:.1f}%)")

    return verdicts
'''




def create_synaptic_pickles():
    """Wrapper to create verdict pickle file."""
    timings_file = './data/synint-f4/syn-preint-20.txt'
    output_file = './data/synint-f4/spike_survival_verdicts_revisions_syn_intv.pickle'

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    verdicts = process_synaptic_interventions(timings_file)
    with open(output_file, 'wb') as f:
        pickle.dump(verdicts, f)

    print(f"\nVerdicts saved to: {output_file}")
    print(f"Total entries: {len(verdicts)}")









######################################################################################################################
''' 4c - null na'''









######################################################################################################################
if __name__ == "__main__":
	#ctrl_filtered()
	#timings_pickle()
	create_synaptic_pickles()
	
	
	
	

