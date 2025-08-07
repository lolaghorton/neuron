The shell files to run the protocols were not given with the model, so everything here has been adapted from run_test_sim.sh and modified per protocol by gathering information from the manuscript. These will be describes as changing the parameters from the test example of run_test_sim.sh as a control .sh file. Since these are all shell files they are meant for a Linux machine, however explicit parameters are mentioned and can easily be adapted for Windows. For each experiment the path of saving the raw data needs to be changed within L23V1_model_sim.hoc to avoid overwriting. For each experiment the simulation is run for 2500 ms total (dtstopext=2500), with a dt of 0.1 ms (dtext=100) unless stated otherwise. In order of the manuscript:


Iterative paired pulse protocol (model validation)
these shell files were written for the use of a cluster with scripts submitted through SLURM. For all 3 files used here valcrit loops through 0-49 corresponding to the 50 dendrite segments (0-6 basal, 7-49 apical), then for each segment a loop of 1-200 synapses (scalefactor) are applied in 2 pulses. There must also be no synapses during this protocol as valcrit and scalefactor will do that work for us, thus nsB, nsA, nbB, nbA, niS, niB, and niA are all set to 1. To see more on this protocol look in stimulus_uniform_basalvar.hoc. For this protocol we aslo want to be recording the actual dendrites (turn dend_record on). Also consider that dend_record will record all dendrites per simulation and will take up a lot of space, a secondary record_save_data.hoc I have modified to only record the dendrite being given pulses by valcrit in record_save_data-i3p.hoc. These can all be run for 500 ms total (dtstopext=500) but if forgotten the analysis code will truncate it.
i3p-nmda.sh: to test nmda spiking we turn on ttx for apical, basal, and soma (attx, bttx, sttx) to set g_na to 0 in all sections. 
i3p-naapical.sh: to test Na spiking we need to turn on val_na in order to disable NMDA receptors. To also recieve apical activity attx will be turned off. I had ran this for all 50 segments but we only need to keep valcrits 7-49 from this.
i3p-nabasal.sh: to test Na spiking we still have val_na on, and to get basal activity we turn attx back on but tur bttx off. From this experiment we only need to keep valcrit's 0-6. 


Orientation tuning/orientation disparity protocol
The biological plausible and even scenario was not run on the cluser so that is a bare bones shell file, inverse however was made for the cluster. To test how apical and basal contribute to orientation selctivity we leave apical orientation preference at 0 deg, but set the basal preference from 0-90 deg in steps of 10 (tag_basal, the disparity), then for each disparity we test 18 different stimulus orientations 0-170 deg (stimulus_presentation), with 10 neurons and 10 runs each (n_neuron, n_run). We only need somatic voltage traces back so turn off dend_record (soma traces are always recorded no matter what). For the orientation tuning protocol its the exact same as the orientation disparity protocol with disparity = 0 deg. 
oridisp-bio.sh: to test the biologically plausible condition the background inhibition is set to 60% basal, 33% apical, 7% soma (soma automatic), this param is in terms of apical so it will be set to 33% (inhdist=330). Then thebackground exciation and stim-driven excitation are also 60% basal and 40% apical, these params are in terms of basal so will be set to 60% (excdist anf excdist_stim = 600). 
oridisp-even.sh: For the even scenario everything is split 50/50, so excdist and excdist_stim = 500, but for inhdist since 7% automatically goes to the soma the value is 46.5% (inhdist=465).
oridisp-inverse.sh: For the inverse scenario, the excdist and excdist_stim are to be 60% apical thus = 400. For the inhibition through it is split 55.8% apical, 37.2% basal, 7% soma. And so inhdist=558.


Spontaneous activity protocol 
spont.sh: For this protocol we run 50 neurons with 100 runs (n_neuron, n_run), and we want no stimulus driven synapses so we turn on nsA and nsB. For this we want the dendrites voltage traces so we keep dend_record on. 
fig2s1btrace.sh: this is for a specific use of one of the plotting scripts that was provided. It is neuron 1, run 2 with nsB and nsA still turned off. This however we run for 5000 ms instead of 2500 (dtstopext=5000). 


Ionic intervention
For this intervention we need to run a pre intervention to grab spike timings to actually preform the intervention at. For both pre and intervention sttx is set to 1 to prevent backpropogation. Spiketime.py is used to get a txt file of spike timings to be used in the actual interventions. 
bio-preint-sttx.sh: Run through stimulus_presentation 0-170 in steps of 10 deg. 10 neurons and 10 runs used (n_neuron, n_run). Only need soma readings, turn dend_record off. 
even-preint-sttx.sh: Only need stimulus_presentation 0 and 90 deg, still n_neuron=10 and n_run=10, dend_record off. 
bio-0-ionint.sh: For stimulus_presentation=0. Read in line by line the spike timings txt file (organized as: neuron run spike time), assign for each run of the simulation a line of the txt file (n_neuron=neuron, n_run=run, tpre=time-3, tpost=time+1, spikenum=spike). Spike is added into the ends of these shell files, they arent needed nessicarily but I found it easier to organize to not overwrite other files (for example if other neuron 1, run 1 has 2 spikes in that trace both spikes need to be recorded for intervention to happen on both, but not having a spike number would mean the second spike with be saved over the first one). Identifier toggles if the intervention is on the apical (-1) or basal (1) tree. Runtype turns on the intervention experiment (found in L23V1_model_sim.hoc).
bio-90-ionint.sh: Same as above but for stimulus_presentation=90
even-0-ionint.sh: Same as above but stimulus_presentation=0, and background synapses are even distribution (inhdist=465, excdist=500).
even-90-ionint.sh: Same as above but stimulus_presentation=90, and background synapses are even distribution (inhdist=465, excdist=500).


Synaptic intervention
synint-4a-apical.sh: For this we run through stimulus_presentations 0 to 170 deg in steps of 10 deg, 10 neurons and 10 runs (n_neuron, n_run), turning on nsA to null stim-driven synapses on the apical branch completely. 
synint-4a-basal.sh: Same as above except we turn off nsB.
synint-50.sh: This uses the same pre intervention as the ionic intervention (only biological condition bio-preint-sttx.sh). Read in line by line from spike timings file (organized as stim neuron run spike time), assign each run of the simulation a line of the txt file (n_neuron=neuron, n_run=run, tpre=time-30, tpost=time+10, spikenum=spike). Identifier again toggles if the intervention is on the apical or basal tree. Stmintv turns on the synaptic intervention experiment (found in L23V1_model_sim.hoc). 
synint-nullna.sh: This is really ionic intervention but used all synint related analysis so I had put it here. For this we have identifier either -1 or 1 for apical or basal intervention, turn runtype on for ionic intervention, and read in the spike timings txt as before with tpre being time-3 and tpost is time+1. For the sensitivity analysis versions (synint-sensi-5 and synint-sensi-10.sh) it is the same as this null na file except anf is reduced to 15 and 10 respectively to lower the apical sodium conductance by 5 and 10%. A new control must be ran as well for the sensitivity analysis, rerun bio-preint-sttx.sh with the same anf changes. 

Apical ablation
This is ran exactly like orientation tuning except with abltd=1. From the oridisp-bio.sh script the disparity was removed (set tag_basal to 0 deg) and then just ran the orientation tuning protocol but with the apical tree ablated. 




