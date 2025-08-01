import arbor
from arbor import units as u
from arbor import label_dict
from arbor import mechanism, location, event_generator#, schedule, explicit_schedule
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

anf=20 #temporary till sh file can pass
ablated = 0

# PARAMETERS
# description of the parameters that need to be passed in .sh file:
# stimulus_presentation: orientation of presented stimulus, in degrees
# tag_basal: mean preferred orientation of the entire basal tree (disparity)
# disp: controls width of synaptic orientation preference distribution (always 0)
# n_run: simulation ID - allows for different variations in input spike trains
# n_neuron: neuron ID - allows for different variations in starting synaptic preference distribution
# swf: synaptic (excitatory) weight factor, modifies AMPA/NMDA weights
# abltd: controls whether the apical tree has been removed (default 0, ablation 1)
# inhdist: distribution of background inhibition, changes apical/basal ratio
# excdist: distribution of background excitation, changes apical/basal ratio
# excdist_stim: distribution of stim-driven excitation, changes apical/basal ratio
# sttx/bttx/attx: soma/basal/apical TTX (g_na = 0) application (1 for yes, 0 for no) 
# nsB, nsA: no stimulation basal/apical (1 to remove stim driven input, 0 to keep it)
# nbB, nbA: no background basal/apical (1 to remove background excitation, 0 to keep it)
# niB, niA, niS: no inhibition basal/apical/soma (1 to remove inhibition, 0 to keep it)
# anf: apical Na factor, transformed into anf2, default=20, rescaled sodium conductance for apical trees
# valcrit: I3P protocol/model validation. -1 to disable, 0-6 basal, 7-49 apical, 50 all dendrites
# scalefactor: synaptic count rescaling variable - if 1, synapses increase by 1 per step. If 2, they increase by 2 per step etc. (used in I3P, goes 1-200)
# dtext: external simulation time step (/1000 to get real value in ms)
# dtstopext: external simulation total runtime (in ms)
# runtype: Enables (1) or disables (0) sodium conductance intervention experiment logic (ionic intervention)
# identifier: Indirectly switches intervention experiment logic to target apical (-1) or basal (1) dendrites (for ionic and synaptic interventions)
# tpre, tpost: Intervention timing (pre-spike and post-spike) for single-spike interventions
# dend_record: toggles saving voltage traces from each 50 dendritic compartments (record 1, off 0) 
# curr_rec: toggles saving current traces (record 1, off 0)
# tag_rec: toggles saving synaptic orientation preference
# val_na: toggle for the validation of sodium activity - disables NMDA receptor activity by setting their conductance to 0 (for I3P protocol)
# validation_clustered: Switches synaptic distribution from uniform across the section to section center (x=0.5) clustering if set to 1 (default: 0)
# stimintv: Similar to runtype, it enables or disables (1/0) synaptic intervention experiment logic
# ampaA_stim_fct: Percentage of apical stim-driven AMPA receptor weight that remains during synaptic intervention experiments
# ampaB_stim_fct: Percentage of basal stim-driven AMPA receptor weight that remains during synaptic intervention experiments
# nmdaA_stim_fct: Percentage of apical stim-driven NMDA receptor weight that remains during synaptic intervention experiments
# nmdaB_stim_fct: Percentage of basal stim-driven NMDA receptor weight that remains during synaptic intervention experiments
# defFB_stim_exc: Delay (in ms) applied to excitatory feedback (apical stimulus-driven) synapses (default value: 10 ms)

#print(f"stim= {stimulus_presentation}, basal disp= {tag_basal}, ori width= {disp}, run= {n_run}, neuron= {n_neuron}, swf= {swf}, albation= {abltd}, inhdist= {inhdist}, excdist= {excdist}, excdist_stim= {excdist_stim}, anf= {anf}, sttx= {sttx}, attx= {attx}, bttx= {bttx}, nsB= {nsB}, nsA= {nsA}, niB= {niB}, niA= {niA}, niS= {niS}, nbB= {nbB}, nbA= {nbA}, valcrit= {valcrit}, scalefctr= {scalefactor}, runtype= {runtype}, identifier= {identifier}, val_na= {val_na}, stimintv= {stimintv}")

# parse through .sh file for the value of parameters described above
# use argparse???

# unchanging parameters
scf = 30 	# synapse count factor, rescales synaptic density
bnf=20 	    # rescales sodium conductance for basal tree
bnf2=(bnf+80)*0.01 	#bnf=[0:1:40] -> bnf=[0.80:0.01:1.20]  //Basal Na factor, transformed
anf2=(anf+80)*0.01 	#anf=[0:1:40] -> anf=[0.80:0.01:1.20]  //Apical Na factor, transformed
# ^^^seen above, in the "bnf2"/"anf2" variables, which hold the transformed vaues of the "bnf"/"anf" input parameters. Thus, values in the [0,40] range are transformed into values in the [0.8, 1.2] range (in this case).
Astim_ampaf=1	 #Scaling factor for apical stimulus-driven AMPA synapse weights (applied at simulation initialization and lasts throughout the simulation)
Astim_nmdaf=1 	#Scaling factor for apical stimulus-driven NMDA synapse weights (applied at simulation initialization and lasts throughout the simulation)
Bstim_ampaf=1 	#Scaling factor for basal stimulus-driven AMPA synapse weights (applied at simulation initialization and lasts throughout the simulation)
Bstim_nmdaf=1 	#Scaling factor for basal stimulus-driven NMDA synapse weights (applied at simulation initialization and lasts throughout the simulation)
delFB_bg_exc=0    # Delay (in ms) applied to apical background-driven (noise) synapses (default value: 0 ms)
delFB_bg_inh=0    # Delay (in ms) applied to apical inhibitory synapses (default value: 0 ms)
##########################################################################################
# build the cell: morph, labels, decor
# cell_setup.hoc section here
print(f"[INFO] Starting cell setup")

# morphology
try:
	morph = arbor.load_swc_neuron("./morpho.swc").morphology 
	print(f'[INFO] Loaded morpholoy')
except Exception as e:
	print(f'[ERROR] Failed to load morphology: {e}')
	exit(1)

# mod files / mechanisms - compiled in as a catalogue (nrnivmodl equivalent)
# ^compile in terminal with: arbor-build-catalogue <name> <path/to/nmodl>
try: 
	cat = arbor.load_catalogue("./test-catalogue.so") #change name
	arbor.catalogue().extend(cat)
	print(f'[INFO] Loaded in .mod file as arbor mechanism catalogue')
except Exception as e:
	print(f'[ERROR] Failed to load .mod file as mechanism catalogue: {e}')
	exit(1)

labels = label_dict()
labels['soma'] = '(tag 1)'
labels['axon'] = '(tag 2)'
labels['basal'] = '(tag 3)'
labels['apical'] = '(tag 4)'
labels['dend'] = '(join (tag 3) (tag 4))'
labels['all'] = '(join (tag 1) (tag 2) (tag 3) (tag 4))'


# passive properties
celsius = 37 #310.15 K
decor = arbor.decor()
decor.set_property(Vm=-79.0 * u.mV, tempK=310.15 * u.Kelvin)

# convert Rm to g_pas 
Rm = 11000
g_pas = 1/Rm #S/cm2
Ri = 100 #ohm cm
Cm = 1 #mircoF/cm2

# set capacitance
decor.set_property(rL = Ri * u.Ohm*u.cm)
decor.paint('"soma"', cm = Cm * u.uF/u.cm2)
decor.paint('"basal"', cm = Cm*2 * u.uF/u.cm2)
if not ablated:
	decor.paint('"apical"', cm = Cm*2 * u.uF/u.cm2)


#active properties
# ion reversal potentials
Ek = -80
Ena = 60
Eca = 140

# global voltage shifts (unused directly in Arbor unless mod files account for them)
vshift_na = -5
vshift_ca = 0

ca_factor = 0.2

# somatic conductances (in mS/cm²)
gna_soma = 1000 * 1.1 * 0.459
gkv_soma = 100 * 0.5
gkm_soma = 2.2 * 1.27
gka_soma = 0.003 * 1.8
gkca_soma = 3 * 0.1 * 7
gca_soma = 0.5 * 0.5 * ca_factor
git_soma = 0.0003 * 0.5 * ca_factor

# dendritic conductances
gna_dend = 600 * 1.1 * 0.459
gkv_dend = 3 * 0.5
gkm_dend = 1 * 1.27
gka_dend = 0.06 * 1.8
gkca_dend = 3 * 0.1 * 7
gca_dend = 0.5 * 0.5 * ca_factor
git_dend = 0.0003 * 0.5 * ca_factor

# set reversal potentials for ions
decor.set_ion('k', rev_pot=Ek * u.mV)
decor.set_ion('na', rev_pot=Ena * u.mV)
decor.set_ion('ca', rev_pot=Eca * u.mV)

#current_balance.hoc approximation???
decor.paint('"all"', arbor.density('pas', {'g': g_pas, 'e': -79}))

# add somatic active channels
decor.paint('"soma"', arbor.density('na', {'gbar': gna_soma}))
decor.paint('"soma"', arbor.density('kv', {'gbar': gkv_soma}))
decor.paint('"soma"', arbor.density('km', {'gbar': gkm_soma}))
decor.paint('"soma"', arbor.density('kap', {'gbar': gka_soma}))
decor.paint('"soma"', arbor.density('kca', {'gbar': gkca_soma}))
decor.paint('"soma"', arbor.density('ca', {'gbar': gca_soma}))
decor.paint('"soma"', arbor.density('it', {'gbar': git_soma})) #T-type calcium, from CaT.mod
decor.paint('"soma"', arbor.density('cad'))  #ca dynamics, from cad.mod

# basal
decor.paint('"basal"', arbor.density('na', {'gbar': gna_dend * bnf2}))
decor.paint('"basal"', arbor.density('kv', {'gbar': gkv_dend}))
decor.paint('"basal"', arbor.density('km', {'gbar': gkm_dend}))
decor.paint('"basal"', arbor.density('kca', {'gbar': gkca_dend}))
decor.paint('"basal"', arbor.density('kap', {'gbar': gka_dend}))  #add diameter override
decor.paint('"basal"', arbor.density('ca'))  # gbar set via location specific override --- figure out how to do this
decor.paint('"basal"', arbor.density('it')) # gbar varies by distance
decor.paint('"basal"', arbor.density('cad'))

# apical
if not ablated:
	decor.paint('"apical"', arbor.density('na', {'gbar': gna_dend * anf2}))
	decor.paint('"apical"', arbor.density('kv', {'gbar': gkv_dend}))
	decor.paint('"apical"', arbor.density('km', {'gbar': gkm_dend}))
	decor.paint('"apical"', arbor.density('kca', {'gbar': gkca_dend}))
	decor.paint('"apical"', arbor.density('kap', {'gbar': gka_dend})) # diameter override
	decor.paint('"apical"', arbor.density('ca'))  # gbar varies by distance
	decor.paint('"apical"', arbor.density('it'))  # gbar varies by distance
	decor.paint('"apical"', arbor.density('cad'))

# fix the diameter and distance changing mechanisms later
#^can define regions in labels for things like radius > 1.5 on apical so should be able to use that for kap
#^for the location specific ones im not sure



cell = arbor.cable_cell(morph, decor, labels) 
model = arbor.single_cell_model(cell)
print("[INFO] Cell setup complete, mechanisms 'painted'")

##########################################################################################
# background_uniform.hoc translation
print(f"[INFO] Creating uniform background synapes")





#print(f"[INFO] Synapes have been 'placed'")

##########################################################################################
# the recipe
# a.recipe, a.context, a.simulation, run it
'''
class pet_recipe(arbor.recipe):
	def __init__(self, ncells):
		arbor.recipe.__init__(self)
		
		# global properties
		self.props = arbor.cable_global_properties()
		self.props.set_property(Vm = -79 *u.mV, tempK = 310.15 *u.Kelvin, rl = 100 *u.Ohm*u.cm, cm = 1 *u.uF*u.cm2)
		
	def num_cells(self):
		return 1 # or 50?
	
	def cell_kind(self, _):
		return arbor.cell_kind.cable
	
	def cell_description(self, gid):
		return cell #overrides to all the morph, decor, labels done above
	
	def probes(self, _):
		#return cable probe membrance voltage ???
	
	def connections(self, gid):
		#all the expsyn/net_reieve stuff???
	
	def global_properties(self, _):
		return self.props

recipe = pet_recipe()

#put this sim stuff at the end once done
sim = arbor.simulation(recipe)
sim.record(arbor.spike_recording.all)
handle = sim.sample((0, "Um"), arbor.regular_schedule(0.02 * u.ms))
sim.run(tfinal = 2500 * u.ms, dt = 0.1 * u.ms) #get these from arguments passed
spikes = sim.spikes()
print(len(spikes), "spikes recorded:")
for gid, lid), t in spikes:
	print(f" * t={t:.3f}ms gid={gid} lid={lid}")

#add plots
'''







##########################################################################################




























#actual L23V1_model_sim translated contents (experiment related stuff mostly)

# toggle ablation


# import other files needed 
# ^ basic graphics, morphologies, cell setup, delete primary basal, exp protocols, get paths, record save data, background uniform, stimulus uniform basal var


# set time related parameters (unit conversions)


# special control variables 


# synaptic weights


# simulate background synapses


# other stimulus properties


# directory to save data


# run the sim
# ^run ablation
# ^voltage recordings
# ^ion int logic
# ^syn int logic

# The End!



'''
simple layout
morph = arbor.load_swc(config["morphology"])
tree = arbor.segment_tree()
labels = arbor.label_dict()

# Placeholder: insert morphology conversion here

decor = arbor.decor()
decor.set_property(Vm=config["cell"]["v_init"], cm=config["cell"]["cm_soma"], rL=config["cell"]["ri"])

# Placeholder: insert mechanisms here
# decor.paint('"soma"', "pas", {"g": 1/config["cell"]["rm"], "e": config["cell"]["v_init"]})

# Placeholder: insert background and stimulus synapses
# Placeholder: insert recordings

recipe = arbor.recipe()
# Placeholder: implement full recipe class with labels, decor, probes, etc.

# Simulation context and run
sim = arbor.simulation(recipe)
sim.run(tfinal=config["duration"], dt=config["dt"])

# Placeholder: save traces to output/
'''

