#!/bin/bash
#SBATCH --job-name=oridisp_inverse
#SBATCH --output=logs/slurm_%A_%a.out
#SBATCH --error=logs/slurm_%A_%a.err
#SBATCH --time=48:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=1
#SBATCH --array=0-9%10 

BASE_DIR="/home/lhorton/pet2023"
cd $BASE_DIR

mkdir -p logs

NEURON_ID=$SLURM_ARRAY_TASK_ID

for disparity in 0 10 20 30 40 50 60 70 80 90; do  
	for orientation in 0 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170; do   
		for run in $(seq 0 9); do   
			./mod.files/x86_64/special -nogui -nopython -c basal_width=30 -c stimulus_presentation=$orientation -c tag_basal=$disparity -c disp=0 -c apical_width=30 -c dend_id1=0 -c dend_id2=0 -c n_run=$run -c n_neuron=$NEURON_ID -c istim=3000 -c swf=55 -c abltd=0 -c inhdist=558 -c excdist=400 -c excdist_stim=400 -c iwf=10000  -c sttx=0 -c bttx=0 -c attx=0 -c nsB=0 -c nsA=0 -c nbB=0 -c nbA=0 -c niS=0 -c niB=0 -c niA=0 -c scf=30 -c bnf=20 -c anf=20 -c valcrit=-1 -c scalefactor=1 -c dtext=100 -c dtstopext=2500 -c runtype=0 -c identifier=0 -c tpre=0 -c tpost=0 -c dend_record=0 -c curr_rec=0 -c val_bas=-1 -c val_ap=-1 -c tag_rec=0 -c val_na=0 -c cct=-1 -c cca=0 -c ibg=1100 -c iinh=1100 -c validation_clustered=0 -c stimintv=0 -c ampaA_stim_fct=100 -c nmdaA_stim_fct=100 -c ampaB_stim_fct=100 -c nmdaB_stim_fct=100 -c Astim_ampaf=1 -c Bstim_ampaf=1 -c Astim_nmdaf=1 -c Bstim_nmdaf=1 -c delFB_stim_exc=10 -c delFB_bg_exc=0 -c delFB_bg_inh=0 L23V1_model_sim.hoc
		done
	done
done
