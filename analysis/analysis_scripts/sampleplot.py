#just making simple plot of a trace to check things when needed


import numpy as np
import matplotlib.pyplot as plt
import Code_General_utility_spikes_pickling as util

ti3p = np.arange(0, 5001, 1)		#for i3p length
t = np.arange(0, 25001, 1)		#for regular simulation protocol

#for i3p
'''
for id_s in range(1, 201):
	filepath = f'../results/i3p-all/allttxon/valna_1/valcrit_0/scalefctr_{id_s}/basal0.dat'
	trace = np.loadtxt(filepath)
	plt.plot(ti3p, trace)
	#print(len(trace))
plt.show()
# ok looks good

for id_s in range(1, 201):
	fp = f'../results/i3p-all/allttxon/valna_0/valcrit_0/scalefctr_{id_s}/basal0.dat'
	trace = np.loadtxt(fp)
	plt.plot(ti3p, trace)
	#print(len(trace))
plt.show()
'''

for s in range(1, 201):
	fp = f'../results/i3p/valna_1/valcrit_4/scalefctr_{s}/soma.dat'
	trace=np.loadtxt(fp)
	plt.plot(t, trace)
plt.show()


'''
#for testing the pre ionic int raw data confirmung the spike count and timings
sample = f'./../results/even-preint/stim_0/neuron_49/run_8/soma.dat'
trace = np.loadtxt(sample)
plt.plot(t, trace)
plt.show()
#^just confirmed that my spike timing python script worked perfect for creating the txt that i needed
'''

'''
#test neuron 0, run 0 for spont activity
spont = './../results/spontaneous/neuron_49/run_99/soma.dat'
trace = np.loadtxt(spont)
plt.plot(t,trace)
plt.show()
'''

'''
#testing more spont stuff
for nur in range(0, 10):
	for run in range(0, 10):
		files=f'./../results/spontaneous/neuron_{nur}/run_{run}/soma.dat'
		trace = np.loadtxt(files)
		plt.plot(t,trace)
		plt.show()
	'''	
		

