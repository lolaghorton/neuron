
NEURON {
	SUFFIX kap
	USEION k READ ek WRITE ik
        RANGE gbar,gka
        GLOBAL ninf,linf,taul,taun,lmin
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	v (mV)
	celsius		(degC)
	gbar=.008 (mho/cm2)
     	vhalfn=11   (mV)
     	vhalfl=-56   (mV)
     	a0l=0.05      (/ms)
     	a0n=0.05    (/ms)
     	zetan=-1.5    (1)
     	zetal=3    (1)
     	gmn=0.55   (1)
     	gml=1   (1)
	lmin=2  (mS)
	nmin=0.1  (mS)
	pw=-1    (1)
	tq=-40
	qq=5
	q10=5
	qtl=1
	ek
}

STATE {
	n
        l
}

ASSIGNED {
:	ik (mA/cm2)
        ninf
        linf      
        taul
        taun
        gka
}

INITIAL {
	rates(v, celsius)
	n=ninf
	l=linf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gka = gbar*n*l
	ik = gka*(v-ek)
}

FUNCTION alpn(v(mV), celsius (degC)) {
LOCAL zeta
  zeta=zetan+pw/(1+exp((v-tq)/qq))
  alpn = exp(1.e-3*zeta*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betn(v(mV), celsius (degC)) {
LOCAL zeta
  zeta=zetan+pw/(1+exp((v-tq)/qq))
  betn = exp(1.e-3*zeta*gmn*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION alpl(v(mV), celsius (degC)) {
  alpl = exp(1.e-3*zetal*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betl(v(mV), celsius (degC)) {
  betl = exp(1.e-3*zetal*gml*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
        rates(v, celsius)
        n' = (ninf - n)/taun
        l' =  (linf - l)/taul
}

PROCEDURE rates(v (mV), celsius (degC)) { :callable from hoc
        LOCAL a,qt
        qt=q10^((celsius-24)/10)
        a = alpn(v, celsius)
        ninf = 1/(1 + a)
        taun = betn(v, celsius)/(qt*a0n*(1+a))
	if (taun<nmin) {taun=nmin}
        a = alpl(v, celsius)
        linf = 1/(1+ a)
	taul = 0.26*(v+50)/qtl
	if (taul<lmin/qtl) {taul=lmin/qtl}
}
