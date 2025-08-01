#!/bin/bash
#SBATCH --job-name=i3p-nabasal
#SBATCH --output=logs/slurm_%A_%a.out
#SBATCH --error=logs/slurm_%A_%a.err
#SBATCH --time=48:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=1
#SBATCH --array=0-49%20

BASE_DIR="/home/horton/venv/nrnvenv/pet2023"
cd $BASE_DIR
mkdir -p logs

dendseg=$SLURM_ARRAY_TASK_ID

for synnum in $(seq 1 200); do
		./mod.files/x86_64/special -nogui -nopython -c basal_width=30 -c stimulus_presentation=0 -c tag_basal=0 -c disp=0 -c apical_width=30 -c dend_id1=0 -c dend_id2=0 -c n_run=0 -c n_neuron=0 -c istim=3000 -c swf=55 -c abltd=0 -c inhdist=330 -c excdist=600 -c excdist_stim=600 -c iwf=10000  -c sttx=1 -c bttx=0 -c attx=1 -c nsB=1 -c nsA=1 -c nbB=1 -c nbA=1 -c niS=1 -c niB=1 -c niA=1 -c scf=30 -c bnf=20 -c anf=20 -c valcrit=$dendseg -c scalefactor=$synnum -c dtext=100 -c dtstopext=2500 -c runtype=0 -c identifier=0 -c tpre=0 -c tpost=0 -c dend_record=1 -c curr_rec=0 -c val_bas=-1 -c val_ap=-1 -c tag_rec=0 -c val_na=1 -c cct=-1 -c cca=0 -c ibg=1100 -c iinh=1100 -c validation_clustered=0 -c stimintv=0 -c ampaA_stim_fct=100 -c nmdaA_stim_fct=100 -c ampaB_stim_fct=100 -c nmdaB_stim_fct=100 -c Astim_ampaf=1 -c Bstim_ampaf=1 -c Astim_nmdaf=1 -c Bstim_nmdaf=1 -c delFB_stim_exc=10 -c delFB_bg_exc=0 -c delFB_bg_inh=0 L23V1_model_sim.hoc
done
