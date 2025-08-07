import numpy as np
import pandas as pd
import pickle
import Code_General_utility_spikes_pickling as util
import os
'''
'''
#IONIC INTERVENTION PROTOCOL ANALYSIS

preint_spikes = 'the spike timings of the pre inttervention function is in another doc called spiketime.py'

def load_spike_timings(timings_file):
    """Load pre-intervention spike timings from file."""
    spike_data = []
    with open(timings_file, 'r') as f:
        for line in f:
            neuron, run, spike_num, time_ms = line.strip().split()
            spike_data.append({
                'neuron': int(neuron),
                'run': int(run),
                'spike_num': int(spike_num),
                'time': float(time_ms)
            })
    return spike_data


def check_intervention_survival(cond, angle, neuron, run, spike_num, intervention_type):
    """Check if spike survived apical (-1) or basal (+1) intervention."""
    intv_dir = 'apical' if intervention_type == -1 else 'basal'
    base_path = f'./../results/{cond}-{angle}-ionint/identifier_{intervention_type}'
    soma_file = f'{base_path}/neuron_{neuron}/run_{run}/spike_{spike_num}/soma.dat'
    timings_file = f'./data/ionint-f3/preint-times/{cond}-{angle}-timings-sttx.txt'
    
    if not os.path.exists(soma_file):
        print(f"Missing intervention file: {soma_file}")
        return None
    
    try:
        spike_data = load_spike_timings(timings_file)
        current_spike = next((s for s in spike_data if 
                              s['neuron'] == neuron and 
                              s['run'] == run and 
                              s['spike_num'] == spike_num), None)
        if not current_spike:
            print(f"Spike {spike_num} not found in timings for neuron {neuron}, run {run}")
            return None

        expected_time = current_spike['time']
        dt = 0.1
        pre_ms = 0.25
        post_ms = 0.25
        pre_idx = int((expected_time - pre_ms) / dt)
        post_idx = int((expected_time + post_ms) / dt)

        full_vtrace = np.loadtxt(soma_file)
        if pre_idx < 0 or post_idx > len(full_vtrace):
            print(f"Spike window [{pre_idx}:{post_idx}] out of bounds in {soma_file}")
            return None
        
        vtrace_window = full_vtrace[pre_idx:post_idx]
        if len(vtrace_window) == 0:
            print(f"Empty voltage slice for {soma_file}")
            return None

        n_spikes, _ = util.GetSpikes(vtrace_window, threshold=-20, detection_type='max')
        survived = n_spikes > 0
        if survived:
            print(f"Spike survived {intv_dir} (neuron {neuron} run {run} spike {spike_num})")
        return survived

    except Exception as e:
        print(f"Error reading {soma_file}: {e}")
        return None


def process_interventions(cond, angle):
    """Run intervention classification for a condition + angle combo."""
    verdicts = {}
    spike_counts = {'total': 0, 'apical': 0, 'basal': 0, 'unstable': 0, 'bistable': 0}
    timings_file = f'./data/ionint-f3/preint-times/{cond}-{angle}-timings-sttx.txt'

    if not os.path.exists(timings_file):
        print(f"Missing timings file: {timings_file}")
        return verdicts
    
    spike_data = load_spike_timings(timings_file)
    print(f"Processing {len(spike_data)} spikes for {cond} {angle}°")

    for spike in spike_data:
        neuron = spike['neuron']
        run = spike['run']
        spike_num = spike['spike_num']
        spike_time = spike['time']
        cond_code = '600'  # hardcoded in plot code
        key = f'{cond_code}-{neuron}-{run}-{angle}-{spike_num}-'

        # Check if spike survives interventions
        apical_survived = check_intervention_survival(cond, angle, neuron, run, spike_num, -1)
        basal_survived  = check_intervention_survival(cond, angle, neuron, run, spike_num, +1)

        if apical_survived is None or basal_survived is None:
            print(f"Skipping spike {spike_num} (missing or bad trace)")
            continue

        if not basal_survived and not apical_survived:
            verdict = 'unstable'
        elif apical_survived:
            verdict = 'basal'
        elif basal_survived:
            verdict = 'apical'
        else:
            verdict = 'bistable'

        if key not in verdicts:
            verdicts[key] = {'Verdict': [], 'Timings': []}

        verdicts[key]['Verdict'].append(verdict)
        verdicts[key]['Timings'].append(spike_time)
        spike_counts[verdict] += 1
        spike_counts['total'] += 1

    print(f"\nClassification summary for {cond} {angle}°:")
    for vtype in ['apical', 'basal', 'unstable', 'bistable']:
        count = spike_counts[vtype]
        frac = (count / spike_counts['total']) * 100 if spike_counts['total'] > 0 else 0
        print(f"  {vtype.capitalize():<9}: {count:>4} spikes ({frac:.1f}%)")
    
    return verdicts


def create_verdict_pickle():
    """Main wrapper to run all conditions + save the pickle."""
    all_verdicts = {}
    conditions = ['even']  # use ['even'] if running for fixed background
    angles = ['0', '90']

    for cond in conditions:
        for angle in angles:
            verdicts = process_interventions(cond, angle)
            all_verdicts.update(verdicts)

    # Final save
    output_dir = './data/ionint-f3'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/fn_spike_survival_verdicts_revisions_na_intv.pickle'
    util.pickle_dump(all_verdicts, output_file)
    print(f"\nSaved verdicts to: {output_file}")

    total_spikes = sum(len(v['Verdict']) for v in all_verdicts.values())
    print(f"\nTotal spikes processed: {total_spikes}")
    print("Done!")


if __name__ == "__main__":
    create_verdict_pickle()

