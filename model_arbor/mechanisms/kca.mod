
NEURON {
	SUFFIX kca
	USEION k READ ek WRITE ik
	USEION ca READ cai
	RANGE gk, gbar :, n
	RANGE ninf, ntau
	GLOBAL Ra, Rb, caix
	GLOBAL q10, temp, tadj, vmin, vmax
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 10   	(pS/um2)	: 0.03 mho/cm2
	v 		(mV)
	cai  		(mM)
	caix = 1								
	Ra   = 0.01:0.01	(/ms)		: max act rate  
	Rb   = 0.02:0.02	(/ms)		: max deact rate 
:	dt		(ms)
	celsius		(degC)
	temp = 23	(degC)		: original temp 	
	q10  = 2.3			: temperature sensitivity
	vmin = -120	(mV)
	vmax = 100	(mV)
} 

ASSIGNED {
	a		(/ms)
	b		(/ms)
:	ik 		(mA/cm2)
	gk		(pS/um2)
:	ek		(mV)
	ninf
	ntau 		(ms)	
	tadj
}
 

STATE { n }

INITIAL { 
	rates(cai, celsius)
	n = ninf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
	gk = tadj*gbar*n
	ik = (1e-4) * gk * (v - ek)
} 

: LOCAL nexp

DERIVATIVE states {   :Computes state variable n 
        rates(cai, celsius)      :             at the current v and dt.
        n' =  (ninf-n)/ntau
}

PROCEDURE rates(cai(mM), celsius (degC)) {  
        a = Ra * cai^caix
        b = Rb
        tadj = q10^((celsius - temp)/10)
        ntau = 1/tadj/(a+b)
	ninf = a/(a+b)
:        tinc = -dt * tadj
:        nexp = 1 - exp(tinc/ntau)
}
