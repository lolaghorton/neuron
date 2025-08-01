
NEURON {
	SUFFIX cad
	USEION ca READ ica, cai WRITE cai
	RANGE ca
	GLOBAL depth,cainf,taur
}

UNITS {
	(molar) = (1/liter)			: moles do not appear in units
	(mM)	= (millimolar)
	(um)	= (micron)
	(mA)	= (milliamp)
	(msM)	= (ms mM)
}

CONSTANT { 
	FARADAY = 96485.3321 (coulomb)
}

PARAMETER {
	depth	= .1	(um)		: depth of shell
	taur	= 50	(ms)		: rate of calcium removal
	cainf	= 100e-6(mM)
	cai		(mM)
}

STATE {
	ca		(mM)
}

INITIAL {
	ca = cainf
	cai = ca
}

ASSIGNED {
:	ica		(mA/cm2)
	drive_channel	(mM/ms)
}
	
BREAKPOINT {
	SOLVE state METHOD cnexp  : derivimplicit
}

DERIVATIVE state { 
	drive_channel =  - (10000) * ica / (2 * FARADAY * depth)
	if (drive_channel <= 0.) { drive_channel = 0. }	: cannot pump inward
	ca' = drive_channel + (cainf-ca)/taur
	cai = ca
}
