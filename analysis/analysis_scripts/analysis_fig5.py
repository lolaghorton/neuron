import numpy as np
import os
import pickle
import Code_General_utility_spikes_pickling as util
'''
THIS FILE FOR FIGURE 5 DATA ANALYSIS AND PICKLING
'''

##################################################################################################################
'''
PET 09 - FIGURE 5 C AND D
'''
# reused/modified from i3p analysis
def process_i3pfig5(root_path, num_dends=50, num_syns=200):
	'originial processing/pickling code for i3p experiments'
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


def amp_data_thresholds(na_data, dt=0.1):
    """
    For each dendrite, find threshold (# synapses) where a Na+ dendritic spike occurs.
    Input: na_data: shape (50, 200, 5001)
    Output: ndarray of shape (50, 3): spike threshold (# synapses)
    """
    num_dends, num_syns, _ = na_data.shape
    spike_thresholds = np.zeros((num_dends, 3))

    for dend_id in range(num_dends):
        for syn_id in range(num_syns):
            trace = na_data[dend_id, syn_id]
            spikes, _ = util.GetSpikes(trace[:int(220/dt)], threshold=-20, detection_type='max')
            if spikes > 0:
                spike_thresholds[dend_id, 2] = syn_id + 1  # off-by-one correction
                print(f"Dendrite {dend_id} threshold: {syn_id + 1} synapses")
                break

        if np.isnan(spike_thresholds[dend_id, 2]):
            print(f"Dendrite {dend_id} no spike detected at up to 200 synapses")
	
    out_path = './data/figure5/amp_data_thresholds.pickle'
    with open(out_path, 'wb+') as f:
        pickle.dump(spike_thresholds, f)

    print(f"\nSaved thresholds for Figure 5C/D to: {out_path}")
    return spike_thresholds

##################################################################################################################
'''
PET 18 - FIGURE 5 SUP ABEF
'''
#instead of na thresholds its spike attenuation at the soma in mV

# reused/modified from i3p analysis
def process_i3pfig5_soma(root_path, num_dends=50, num_syns=200):
	'originial processing/pickling code for i3p experiments'
	data = np.zeros((num_dends, num_syns, 5001))
	
	for dend_id in range(num_dends):
		for syn_id in range(1, num_syns+1):
			soma_path = f"{root_path}/valcrit_{dend_id}/scalefctr_{syn_id}/soma.dat"
            
			if os.path.exists(soma_path):
				trace = np.loadtxt(soma_path)
			else:
				raise FileNotFoundError(f"No soma.dat file found for dendrite {dend_id} at {syn_id} synapses")
			
			#truncate my data to 5001 points bc i ran it too long
			if len(trace) > 5001:
				print(f'Truncating soma trace from valcrit {dend_id} synapse {syn_id} from {len(trace)} to 5001 points')
				trace = trace[:5001]
			else:
				print(f'Trace already 5001 points for dendrite {dend_id} synapse {syn_id}')

			data[dend_id, syn_id-1] = trace  #synapses 1-200 stored as 0-199
	return data



def dspikes(soma_data, save_path='./data/figure5/amp_data_dspikes.pickle', dt=0.1):
    """
For each dendrite, determine the synapse count needed to trigger a Na+ spike and calculate the somatic spike amplitude (attenuation) at that threshold.
    amp_data: ndarray (50, 3) — column 2 holds attenuation in mV at threshold
    """
    num_dends, num_syns, _ = soma_data.shape
    amp_data = np.zeros((num_dends, 3))  #only column 2 is used

    for dend_id in range(num_dends):
        for syn_id in range(num_syns):
            strace = soma_data[dend_id, syn_id]
            dtrace = na_data[dend_id, syn_id]
			
            # Detect Na+ spike before 220 ms
            spikes, _ = util.GetSpikes(dtrace[0:int(220/dt)], threshold=-20, detection_type='max')

            if spikes > 0:
                # Spike threshold = synapse count that triggered spike
                threshold = syn_id + 1
                strace = soma_data[dend_id, syn_id]
                amp_data[dend_id, 2] = np.max(dtrace[0:int(220/dt)]) - np.max(strace[0:int(220/dt)])
                #amp_data[dend_id, 2] = np.abs(np.max(strace)) 
                print(f"Dendrite {dend_id}: Spike threshold = {threshold}, Attenuation = {amp_data[dend_id, 2]:.2f} mV")
                break

        if amp_data[dend_id, 2] <= 0:
            print(f"Dendrite {dend_id}: No somatic spike detected up to 200 synapses.")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb+') as f:
        pickle.dump(amp_data, f)

    print(f"\nSaved spike attenuation data to: {save_path}")
    return amp_data


##################################################################################################################
'''
PET 08 - FIGURE 5 AB AND 5 SUP CD
'''
#for EPSP_validation_results.pickle
#only ever actually need the amplitudes from this
def process_epsp_validation_data(dend_data, soma_data, dt=0.1, save_path='./data/figure5/EPSP_validation_results.pickle'):
    """
    Extract EPSP amplitudes, widths, and delays from dendritic and somatic voltage traces.
    Pickle file containing (amplitudes, widths, delays, delays_dV)
        - amplitudes: shape (50, 200, 2): dend/soma peak relative to baseline
        - widths:     shape (50, 200, 2): full-width at half-max (ms)
        - delays:     shape (50, 200): dendrite peak latency - soma peak latency (ms)
        - delays_dV:  shape (50, 200): latency to cross 10 mV for dend/soma
    """
    num_dends, num_syns, num_t = dend_data.shape
    amplitudes = np.zeros((num_dends, num_syns, 2))   #dend/soma
    widths     = np.zeros((num_dends, num_syns, 2))   #dend/soma
    delays     = np.zeros((num_dends, num_syns))      #peak delay (dend - soma)
    delays_dV  = np.zeros((num_dends, num_syns))      #10 mV crossing delay (dend - soma)

    stim_window = slice(0, int(220/dt))  #stimulation occurs here

    for dend_id in range(num_dends):
        for syn_id in range(num_syns):
            dtrace = dend_data[dend_id, syn_id]
            strace = soma_data[dend_id, syn_id]

            # baseline estimate --> its really just -79
            v0_mean = np.mean(dtrace[:int(100/dt)])
            v0 = -79

            # peak amplitude
            d_fix = dtrace -v0
            s_fix = strace -v0
            d_peak = np.max(d_fix)
            s_peak = np.max(s_fix) 
            #adding np.abs didnt changing the flipping issue, idk if it changed anything actually
            amplitudes[dend_id, syn_id, 0] = d_peak
            amplitudes[dend_id, syn_id, 1] = s_peak
            
            ################# only really need the amplitudes, can ignore rest even if wrong ##################
            
            # full width at half max (FWHM) 
            def width_halfmax(trace, baseline):
                peak = np.max(trace[stim_window])
                half = (peak + baseline) / 2
                above = np.where(trace[stim_window] > half)[0]
                if len(above) >= 2:
                    return (above[-1] - above[0]) * dt
                return 0.0
            widths[dend_id, syn_id, 0] = width_halfmax(dtrace, v0)
            widths[dend_id, syn_id, 1] = width_halfmax(strace, v0)

            # peak latency difference
            d_peak_t = np.argmax(dtrace[stim_window]) + stim_window.start
            s_peak_t = np.argmax(strace[stim_window]) + stim_window.start
            delays[dend_id, syn_id] = (d_peak_t - s_peak_t) * dt
            # latency to 10 mV crossing above baseline
            def crossing_delay(trace, baseline, target=10):
                above = np.where(trace[stim_window] > baseline + target)[0]
                if len(above) > 0:
                    return (above[0] + stim_window.start) * dt
                return np.nan
            d10 = crossing_delay(dtrace, v0)
            s10 = crossing_delay(strace, v0)
            if not np.isnan(d10) and not np.isnan(s10):
                delays_dV[dend_id, syn_id] = d10 - s10
            else:
                delays_dV[dend_id, syn_id] = np.nan

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb+') as f:
        pickle.dump((amplitudes, widths, delays, delays_dV), f)
    print(f"Saved EPSP validation data to: {save_path}")
    return amplitudes, widths, delays, delays_dV

'''
#for amp_data_EPSPs.pickle
def extract_epsp_attenuation(amplitudes, dend_data, soma_data, target_dv=20, save_path='./data/figure5/amp_data_EPSPs.pickle'):
    """
	For each dendrite, find the synapse count producing ~20 mV EPSP at the dendrite, and extract the 
	corresponding attenuation at the soma. Returns array of shape (50, 3) — only column 2 is used (attenuation).
    """
    dend_amps = amplitudes[:, :, 0]
    soma_amps = amplitudes[:, :, 1]
    num_dends = dend_amps.shape[0]
    dt=0.1

    amp_data = np.zeros((num_dends, 3))

    for dend_id in range(num_dends):
        diffs = np.abs(dend_amps[dend_id] - target_dv)
        syn_id = np.argmin(diffs)
        attenuation = dend_amps[dend_id, syn_id] - soma_amps[dend_id, syn_id] #added dend_amps[] - , flipped good now but still slightly off
        #dtrace=dend_data[dend_id, syn_id]
        #strace=soma_data[dend_id, syn_id]
        #attenuation = np.max(dtrace[0:int(220/dt)]) - np.max(strace[0:int(220/dt)])

        amp_data[dend_id, 2] = attenuation
        print(f"Dendrite {dend_id}: EPSP @ dend ≈ {dend_amps[dend_id, syn_id]:.2f} mV -> Attenuation = {attenuation:.2f} mV (syn {syn_id+1})")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb+') as f:
        pickle.dump(amp_data, f)

    print(f"\nSaved EPSP attenuation data to: {save_path}")
    return amp_data
'''
def extract_epsp_attenuation(amplitudes, target_dv=20, save_path='./data/figure5/amp_data_EPSPs.pickle'):
    """
    Vectorized extraction of EPSP attenuation at the soma from ~20 mV dendritic EPSPs.
    Returns amp_data: shape (50, 3), with column 2 containing attenuation values.
    """
    dend_amps = amplitudes[:, :, 0]
    soma_amps = amplitudes[:, :, 1]
    
    dend_amps = np.array(dend_amps)
    soma_amps = np.array(soma_amps)

    # Find the index of the synapse closest to 20 mV EPSP at each dendrite
    dend_diff = np.abs(dend_amps - target_dv)
    idx_dV = np.argmin(dend_diff, axis=1)
    thresholds = idx_dV+1

    # Gather the matching dendritic and somatic EPSP amplitudes
    #actual_dend_amps = dend_amps[np.arange(dend_amps.shape[0]), idx_dV]
    #actual_soma_amps = soma_amps[np.arange(soma_amps.shape[0]), idx_dV]
    actual_dend_amps = np.array([dend_amps[i,x] for i,x in enumerate(thresholds-1)])
    actual_soma_amps = np.array([soma_amps[i,x] for i,x in enumerate(thresholds-1)])
    attenuation = actual_dend_amps - actual_soma_amps

    # Store in amp_data (only column 2 is used)
    amp_data = np.zeros((dend_amps.shape[0], 3))
    amp_data[:, 2] = attenuation

    # Stats
    print(f'Proximity to selected voltage ({target_dv} mV):')
    print(f'\tMean and st.dev. of dendritic EPSP amplitude: {np.mean(actual_dend_amps):.4f} ± {np.std(actual_dend_amps):.4f}')

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb+') as f:
        pickle.dump(amp_data, f)
    print(f"\nSaved EPSP attenuation data to: {save_path}")

    return amp_data
##################################################################################################################
if __name__ == "__main__":
	#for figure 5 c and d --- will be fig 4 and 5 in pet 09 output 
	#na_data = process_i3pfig5(f"./../results/i3p/valna_1")     #sodium spiking only
	#amp_data_thresholds(na_data)
	
	#for figure 5 sup abef --- will be 5se-fig1 5sf-fig2 5sb-fig3 5sa-fig4 in pet 18 output
	#na_data = process_i3pfig5(f"./../results/i3p/valna_1")
	#soma_data = process_i3pfig5_soma(f"./../results/i3p/valna_1") 
	#dspikes(soma_data)
	
	#for figure 5 ab and 5 sup cd --- will be 5a-fig3 5b-fig4 5sc-fig1 5sd-fig2 in pet 08 output
    dend_data = process_i3pfig5(root_path="./../results/i3p/valna_1")
    soma_data = process_i3pfig5_soma(root_path="./../results/i3p/valna_1")
    amplitudes, widths, delays, delays_dV = process_epsp_validation_data(dend_data, soma_data)
    amp_data = extract_epsp_attenuation(amplitudes)
    
    

