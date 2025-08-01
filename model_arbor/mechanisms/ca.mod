
NEURON {
	SUFFIX ca
	USEION ca READ eca WRITE ica
	RANGE gca, gbar :, m , h
	RANGE minf, hinf, mtau, htau
	GLOBAL q10, temp, tadj, vmin, vmax, vshift
}

PARAMETER {
	gbar = 0.1   	(pS/um2)	: 0.12 mho/cm2
	vshift = 0	(mV)		: voltage shift (affects all)

	cao  = 2.5	(mM)	        : external ca concentration
	cai		(mM)
						
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

CONSTANT { 
	FARADAY = 96485.3321 (coulomb)
	R = 8.3144 (joule/degC)
	PI = 3.14159
}

ASSIGNED {
:	ica 		(mA/cm2)
	gca		(pS/um2)
:	eca		(mV)
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
        gca = tadj*gbar*m*m*h
	ica = (1e-4) * gca * (v - eca)
} 

: LOCAL mexp, hexp

:PROCEDURE states() {
:        trates(v+vshift)      
:        m = m + mexp*(minf-m)
:        h = h + hexp*(hinf-h)
:	VERBATIM
:	return 0;
:	ENDVERBATIM
:}

DERIVATIVE states {
        trates(v+vshift, celsius)      
        m' =  (minf-m)/mtau
        h' =  (hinf-h)/htau
}

PROCEDURE trates(v, celsius) {  
                      
        
:        TABLE minf, hinf, mtau, htau 
:	DEPEND  celsius, temp
	
:	FROM vmin TO vmax WITH 199

	rates(v, celsius): not consistently executed from here if usetable == 1

:        tinc = -dt * tadj

:        mexp = 1 - exp(tinc/mtau)
:        hexp = 1 - exp(tinc/htau)
}


PROCEDURE rates(vm, celsius) {  
        LOCAL  a, b

        tadj = q10^((celsius - temp)/10)

:	a = 0.055*(-27 - vm)/(exp((-27-vm)/3.8) - 1)
	a = 0.5*(-27 - vm)/(exp((-27-vm)/3.8) - 1)
	b = 0.1*exp((-75-vm)/17)
	
	mtau = 1/tadj/(a+b)
	minf = a/(a+b)

		:"h" inactivation 

	a = 0.000457*exp((-13-vm)/50)
	b = 0.0065/(exp((-vm-15)/28) + 1)

	htau = 1/tadj/(a+b)
	hinf = a/(a+b)
}

FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}
