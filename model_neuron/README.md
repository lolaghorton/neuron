This folder and its subfolders contain the NEURON model used in the manuscript by Petousakis et al., 2023.
Not all experiment files and data are provided for size reasons. 
The files contained in this folder and subfolders constitute the core of the model, which is necessary
and sufficient to reproduce the results of any experiment described in the manuscript, given the correct
parameter combination is provided.

The model files are adapted from Park et al., 2019 (ModelDB accession number [231185](https://modeldb.science/231185)).

## Model File Description

The files and folders are as follows:

- [Folder] `mod.files`: contains the mechanism files (receptors and channels) required to run the model.
These files should be re-compiled on the host computer in order for the model to run.
See [https://www.neuron.yale.edu/neuron/static/docs/nmodl/unix.html](https://www.neuron.yale.edu/neuron/static/docs/nmodl/unix.html) for instructions using
Linux-based machines, and [https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html](https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html)
for instructions for Windows-based machines. See last part of this file for details.
- [Folder] `morphologies`: contains the cellular morphology used in this manuscript. Also contains ablated
morphologies used in the original model (Park et al., 2019; a/n 231185).
- [Folder] `results`: this folder is created after the model is successfully simulated through NEURON. 

- [File] `background_uniform.hoc`: this file establishes background (noise) synaptic connections.
- [File] `basic-graphics.hoc`: this file contains auxiliary functions related to plots displayed when using NEURON
through the Graphical User Interface (GUI).
- [File] `cell_setup.hoc`: this file establishes the morphology and electrophysiological properties of the neuron.
[File] `current-balance.hoc`: this file balances all neuronal compartments to -79 mV.
[File] `delete-primary-basal.hoc`: this file is part of the original model, and was responsible for performing
dendritic branch/tree ablations. It is not used for this purpose in this work.
- [File] `exp_protocols.hoc`: this file contains various experiment-related protocols (e.g. TTX-like protocol
whereby g_Na is set to 0 for specified compartments/entire dendritic trees).
- [File] `getpaths.hoc`: this file extracts morphological and electrophysiological properties from the compartments
of the model neuron.
- [File] `L23V1_model_sim.hoc`: this file is the main file of the model, and is the one executed to run simulations.
It requires a large amount of externally-provided parameters (using the "-c" argument)
in order to function. The parameters are described within the file itself, in a large
comment block.
- [File] `record_save_data.hoc`: this file contains functions that handle the recording and storage of model output.
- [File] `recsyns.hoc`: this file contains functions that record and store synaptic orientation preferences per
dendritic branch.
- [File] `run_test_sim.sh`: this file is executed (on a linux-based machine) to run a single simulation of the model
using the Graphical User Interface of NEURON. All required parameters are provided. Note
that this file will only execute one run, whereas the results presented in the manuscript
are the product of hundreds of thousands of runs in total.
- [File] `run_test_sim.bat`: this file is executed (on a windows-based machine) to run a single simulation of the model
using the Graphical User Interface of NEURON. All required parameters are provided. Note
that this file will only execute one run, whereas the results presented in the manuscript
are the product of hundreds of thousands of runs in total.
- [File] `stimulus_uniform_basalvar.hoc`: this file distributes synaptic orientation preferences and establishes 
stimulus-driven synaptic connections.


## Running the model

In order to run the model, the user needs to have the NEURON simulator installed, and be familiar with it
([https://nrn.readthedocs.io](https://nrn.readthedocs.io)).

The first step is compiling the mechanisms used by the model. Detailed instructions can be found here: for
[Linux](https://www.neuron.yale.edu/neuron/static/docs/nmodl/unix.html) or for
[Windows](https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html).
Briefly, you need to navigate to `./mod.files/` and open a new terminal window/command line window in that folder,
then run either "`nrnivmodl`" (linux) or "`mknrndll`" (windows).

On Windows, copy the `nrnmech.dll` file from `./mod.files/` to the main directory of the simulation files (same 
path as the file `L23V1_model_sim.hoc`).

On a linux-based machine, execute `run_test_sim.sh` by typing "`sh run_test_sim.sh`" in a terminal window,
and a simulation of the model with the provided parameters should start. 
Results will be saved in the "`results`" folder.

On a windows-based machine, execute "`run_test_sim.bat`" by double-clicking the corresponding icon, or 
running it through the command line. A simulation of the model with the provided parameters should start. 
Results will be saved in the "`results`" folder.

If there are any issues, please contact me at kepetousakis[at]gmail.com.