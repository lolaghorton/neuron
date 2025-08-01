
NEURON {
	SUFFIX kv
	USEION k READ ek WRITE ik
	RANGE gk, gbar :, n
	RANGE ninf, ntau, ik
	GLOBAL Ra, Rb
	GLOBAL q10, temp, tadj, vmin, vmax
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 5   	(pS/um2)	: 0.03 mho/cm2
	v 		(mV)							
	tha  = 25	(mV)		: v 1/2 for inf
	qa   = 9	(mV)		: inf slope		
	Ra   = 0.02	(/ms)		: max act rate
	Rb   = 0.006	(/ms)		: max deact rate	:0.002 before. Changed to 0.006 (Febrouary 2015) for smaller AHP.
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
	ntau (ms)	
	tadj
}

STATE { n }

INITIAL { 
	trates(v, celsius)
	n = ninf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
	gk = tadj*gbar*n
	ik = (1e-4) * gk * (v - ek)
} 

DERIVATIVE  states {   :Computes state variable n 
        trates(v, celsius)      :             at the current v and dt.
        n' =  (ninf-n)/ntau
}

PROCEDURE trates(v, celsius) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
:        TABLE ninf, ntau
:	DEPEND  celsius, temp, Ra, Rb, tha, qa
:	FROM vmin TO vmax WITH 199
	rates(v, celsius): not consistently executed from here if usetable_hh == 1
:        tinc = -dt * tadj
:        nexp = 1 - exp(tinc/ntau)
}

PROCEDURE rates(v, celsius) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        a = Ra * (v - tha) / (1 - exp(-(v - tha)/qa))
        b = -Rb * (v - tha) / (1 - exp((v - tha)/qa))
        tadj = q10^((celsius - temp)/10)
        ntau = 1/tadj/(a+b)
	ninf = a/(a+b)
}
