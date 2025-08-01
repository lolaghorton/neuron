
NEURON {
	SUFFIX na
	USEION na READ ena WRITE ina
	RANGE gna, gbar :, m, h
	GLOBAL tha, thi1, thi2, qa, qi, qinf, thinf
	RANGE minf, hinf, mtau, htau
	GLOBAL Ra, Rb, Rd, Rg
	GLOBAL q10, temp, tadj, vmin, vmax, vshift
}

PARAMETER {
	gbar = 1000   	(pS/um2)	: 0.12 mho/cm2
	vshift = -10	(mV)		: voltage shift (affects all)								
	tha  = -35:-30:-35	(mV)		: v 1/2 for act		(-42)
	qa   = 9.8:9	(mV)		: act slope		
	Ra   = 0.182	(/ms)		: open (v)		
	Rb   = 0.14:0.124	(/ms)		: close (v)		
	thi1  = -50	(mV)		: v 1/2 for inact 	
	thi2  = -75	(mV)		: v 1/2 for inact 	
	qi   = 5	(mV)	        : inact tau slope
	thinf  = -65	(mV)		: inact inf slope	
	qinf  = 6.2	(mV)		: inact inf slope
	Rg   = 0.0091	(/ms)		: inact (v)	
	Rd   =0.024	(/ms)		: inact recov (v) 
	temp = 23	(degC)		: original temp 
	q10  = 2.3			: temperature sensitivity
	v 		(mV)
:	dt		(ms)
	celsius		(degC)
	vmin = -120	(mV)
	vmax = 100	(mV)
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

ASSIGNED {
:	ina 		(mA/cm2)
	gna		(pS/um2)
:	ena		(mV)
	minf 		hinf
	mtau (ms)	htau (ms)
	tadj
}

STATE { m h }

INITIAL { 
	trates(v+vshift, celsius)
	m = minf
	h = hinf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
        gna = tadj*gbar*m*m*m*h
	ina = (1e-4) * gna * (v - ena)
} 

DERIVATIVE states {   :Computes state variables m, h, and n 
        trates(v+vshift, celsius)      :             at the current v and dt.
        m' =  (minf-m)/mtau
        h' =  (hinf-h)/htau
}

PROCEDURE trates(v, celsius) {        
:        TABLE minf,  hinf, mtau, htau
:	DEPEND  celsius, temp, Ra, Rb, Rd, Rg, tha, thi1, thi2, qa, qi, qinf
:	FROM vmin TO vmax WITH 199

	rates(v, celsius): not consistently executed from here if usetable == 1
}

PROCEDURE rates(vm, celsius) {  
        LOCAL  a, b
	a = trap0(vm,tha,Ra,qa)
	b = trap0(-vm,-tha,Rb,qa)
        tadj = q10^((celsius - temp)/10)
	mtau = 1/tadj/(a+b)
	minf = a/(a+b)
		:"h" inactivation 
	a = trap0(vm,thi1,Rd,qi)
	b = trap0(-vm,-thi2,Rg,qi)
	htau = 1/tadj/(a+b)
	hinf = 1/(1+exp((vm-thinf)/qinf))
}

FUNCTION trap0(v,th,a,q) {
	if (fabs((v-th)/q) > 1e-6) {
	        trap0 = a * (v - th) / (1 - exp(-(v - th)/q))
	} else {
	        trap0 = a * q
 	}
}	
