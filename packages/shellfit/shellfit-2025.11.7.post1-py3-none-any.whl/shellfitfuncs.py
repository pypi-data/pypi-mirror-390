#!/usr/bin/python

# ===========================================================================
# Function container for shellfit. Add your functions here. 
# Use the existing functions as examples.
# ===========================================================================
#
# Version 26.10.2025
#
# A function fitting code utilizing shell-style history. 
# Press up to get your last fit result as the new fit input. 
# 
# Author: dr Andrii Shyichuk, University of Wrocław, 
# email: andrii.shyichuk@uwr.edu.pl 
#
# ===========================================================================
# Beware: the code uses main as a container for functions and data
# ===========================================================================

import scipy as sp
import numpy as np
import sys
from scipy.special import gamma as gamma_function
from scipy.integrate import odeint
from scipy.optimize import least_squares as lsq


exp = np.exp
spp = np.power

# --------------------------------------------------------- Constants

kB_eVK = 8.617333262145e-5

# --------------------------------------------------------- Math functions
# ------------- user can add new functions here --------------------------

# fuction descriptors 

fvlist = {}  # dictionary of variable list, per function
fvlen  = {}  # dictionary of length of variable list, per function
fnames = {}  # dictionary of function names
fform = {}   # dictionary of function formulas
funcs = []
fkeys = [] 

# ---------------------------------------------- function mixer ----
# do not remove this one
def mix(f1, f2, A, *args):
    return A*f1(*args) + (1.0-A)*f2(*args)
    
funcs.append(mix)
fkeys.append("mix")

fvlist[mix] = 'mix'
fvlen[mix] = 0
fnames[mix] = "returns A f1 + (1-A) f2 "
fform[mix]  =  "A f1 + (1-A) f2 " 

# ---------------------------------------------- z offset ----
# do not remove this one
def zo():
    pass

funcs.append(zo)
fkeys.append("zo")

fvlist[zo] = 'zo'
fvlen[zo] = 1
fnames[zo] = "z offset, z0"
fform[zo]  = "z = z0"

# ---------------------------------------------- y offset ----
# do not remove this one
def yo():
    pass

funcs.append(yo)
fkeys.append("yo")

fvlist[yo] = 'yo'
fvlen[yo] = 1
fnames[yo] = "y offset, y0"
fform[yo]  = "y = y0"
    
# ---------------------------------------------- x offset ----
# do not remove this one
def xo():
    pass

funcs.append(xo)
fkeys.append("xo")

fvlist[xo] = 'xo'
fvlen[xo] = 1
fnames[xo] = "x offset, x0"
fform[xo]  = "x = x - x0"


# ---------------------------------------------- Fermi-Dirac ----

# Typical Fermi-Dirac:
# Population of i-th state ni:
# ni = 1 / (     exp((ei-mu)/(kBT)) + 1  ) 
#  ei is the energy of the single-particle state i, and mu is the total chemical potential (Fermi level)

# Here, it is:
# A  (  1    -    1/(   exp( (x-x0)*p) + 1)  

# Inverse Fermi-Dirac, inverse means e<mu has small population, e > mu has large population

# p == kBT 
def ifd(x, A, x0, p):
        return A - A/(exp((x - x0)*p)+1.0)


funcs.append(ifd)
fkeys.append("ifd")

fvlist[ifd] = 'A, x0, p - amplitude, center position, power'
fvlen[ifd] = 3
fnames[ifd] = "Inverse Fermi-Dirac"
fform[ifd]  = "A - A/(np.exp((x - x0)*p)+1.0)"

# p == kBT 
def fd(x, A, x0, p):
        return A/(exp((x - x0)*p)+1.0)


funcs.append(fd)
fkeys.append("fd")

fvlist[fd] = 'A, x0, p - amplitude, center position, power'
fvlen[fd] = 3
fnames[fd] = "Fermi-Dirac distribution"
fform[fd]  = "A/(np.exp((x - x0)*p)+1.0)"


# ---------------------------------------------- lifetime thermometry Eq. 1 ---
# PhotoLuminescence Lifetime Thermometry 
#It's Eq. 2 from DOI: 10.1021/jp512685u

def pllt1(T, p21, p31, dE):
    ekt = exp(dE/(kB_eVK * T))

    return 1 / (p21 * ekt / (1+ekt) + p31/(1+ekt))

funcs.append(pllt1)
fkeys.append("pllt1")

fvlist[pllt1] = ' p21, p31, dE'
fvlen[pllt1] = 3
fnames[pllt1] = "Eq. 2 from DOI: 10.1021/jp512685u, lifetime = f(abs temperature)"
fform[pllt1]  = " 1 / (p21 * ekt / (1+ekt) + p31/(1+ekt) )"

def rpllt1(T, p21, p31, dE):
    ekt = exp(dE/(kB_eVK * T))

    return p21 * ekt / (1+ekt) + p31/(1+ekt)

funcs.append(rpllt1)
fkeys.append("rpllt1")

fvlist[rpllt1] = ' p21, p31, dE'
fvlen[rpllt1] = 3
fnames[rpllt1] = "Eq. 2 from DOI: 10.1021/jp512685u, decay rate = f(abs temperature)"
fform[rpllt1]  = " p21 * ekt / (1+ekt) + p31/(1+ekt) "

def rpllt2(T,  p31, dE):
    return p31 / (1+ exp(dE/(kB_eVK * T)))


funcs.append(rpllt2)
fkeys.append("rpllt2")

fvlist[rpllt2] = '  p31, dE'
fvlen[rpllt2] = 2
fnames[rpllt2] = " part of Eq. 2 from DOI: 10.1021/jp512685u, decay rate = f(abs temperature)"
fform[rpllt2]  = "  p31/(1+ekt) "


def x2pllt1(T, p21_1, p31_1, dE_1, p21_2, p31_2, dE_2 ):
    ekt_1 = exp(dE_1/(kB_eVK * T))
    ekt_2 = exp(dE_2/(kB_eVK * T))

    return 1 / ( 
                 p21_1 * ekt_1 / (1+ekt_1) + p31_1/(1+ekt_1) +
                 p21_2 * ekt_2 / (1+ekt_2) + p31_2/(1+ekt_2) )

funcs.append(x2pllt1)
fkeys.append("x2pllt1")

fvlist[x2pllt1] = ' p21_1, p31_2, dE_2, p21_2, p31_2, dE_2'
fvlen[x2pllt1] = 6
fnames[x2pllt1] = "Eq. 2 from DOI: 10.1021/jp512685u, lifetime = f(abs temperature)"
fform[x2pllt1]  = " 1 / (  p21_1 * ekt_1 / (1+ekt_1) + p31_1/(1+ekt_1) +  p21_2 * ekt_2 / (1+ekt_2) + p31_2/(1+ekt_2)  )"


# ---------------------------------------------- Boltzmann ----

#pi/pj  = exp( (ej-ei)/kT)

def bd(x, Q, D):
    # x is kT, T is variable 
    return exp(-D/x)/Q

funcs.append(bd)
fkeys.append("bd")

fvlist[bd] = 'bd'
fvlen[bd] = 2
fnames[bd] = " norm factor, energy difference (x must be in the units of kT!)"
fform[bd]  = "exp(-D/x)/Q"


# ---------------------------------------------- Boltzmann 2 state----

def bd2(x, D1, D2):
    # x is kT, T is variable 
    e1 = exp(-D1/x)
    e2 = exp(-D2/x)
    return e1/(e1+e2)

funcs.append(bd2)
fkeys.append("bd2")

fvlist[bd2] = 'bd2'
fvlen[bd2] = 2
fnames[bd2] = " e1, e2, (x must be in the units of kT!)"
fform[bd2]  = "Boltzmann probability of state 1 in a 2-state system:  exp(-D1/x)/  (  exp(-D1/x) + exp(-D2/x)) "

# ---------------------------------------------- Boltzmann 3 state----

def bd2(x, D1, D2, D3):
    # x is kT, T is variable 
    e1 = exp(-D1/x)
    e2 = exp(-D2/x)
    return e1/(e1+e2)

funcs.append(bd2)
fkeys.append("bd2")

fvlist[bd2] = 'bd2'
fvlen[bd2] = 2
fnames[bd2] = " e1, e2, (x must be in the units of kT!)"
fform[bd2]  = "Boltzmann probability of state 1 in a 2-state system:  exp(-D1/x)/  (  exp(-D1/x) + exp(-D2/x)) "


# ---------------------------------------------- Murnaghan EOS ---
# x is scale, V/V0

def MEOS(x, E0, K0V0, Kp0):
    K1 = Kp0-1.
    
    return E0 + K0V0 * ( sp.power(x, 1.-Kp0) / (Kp0*K1) + x/Kp0 - 1./K1 )

funcs.append(MEOS)
fkeys.append("MEOS")
fvlist[MEOS] = 'E0, K0V0, Kp0'
fvlen[MEOS] = 3
fnames[MEOS] = "Murnaghan EOS "
fform[MEOS]  = "E0 + K0V0 * ( x^(1.-Kp0) / (Kp0*K1) + x/Kp0 - 1./K1 )"    




# ---------------------------------------------- Linear chirp ----
# do not remove this one
pi2 = np.pi*2.0
def chl(x, phi, f0, k):
    return sp.sin( phi + pi2*(f0*x + k*x*x/2.0))  

funcs.append(chl)
fkeys.append("chl")

fvlist[chl] = 'phi f0 k'
fvlen[chl] = 3
fnames[chl] = "Chirp with linear frequency"
fform[chl]  = "y = sin( phi + pi2*(f0*x + k*x*x/2.0) "

# -------------------------------------------- Maxwell-Boltzmann


def lsmb(x, x0, a, Tm):
    # T == T/m
    xx0 = x-x0
    xx0[xx0>0]=0
    x2 = xx0*xx0
    return a * pow(  2 * np.pi * kB_eVK * Tm, -1.5) * 4 *np.pi * x2 * sp.exp( -x2 / (2 * kB_eVK * Tm) )

funcs.append(lsmb)
fkeys.append("lsmb")

fvlist[lsmb] = 'peak 0 position, amplitude,  temperature (K) over mass'
fvlen[lsmb] = 3
fnames[lsmb] = "Maxwell-Boltzmann distribution that broadens to the left"
fform[lsmb]  = " a * (m / ( 2pi kB T))^1.5   4pi (x-x0)^2  exp ( -m (x-x0) / (2 kB T) )"

def rsmb(x, x0, a, Tm):
    # T == T/m
    xx0 = x-x0
    xx0[xx0>0]=0
    x2 = xx0*xx0
    return a * pow(  2 * np.pi * kB_eVK * Tm, -1.5) * 4 *np.pi * x2 * exp( -x2 / (2 * kB_eVK * Tm) )

funcs.append(rsmb)
fkeys.append("rsmb")

fvlist[rsmb] = 'peak 0 position, amplitude,  temperature (K) over mass'
fvlen[rsmb] = 3
fnames[rsmb] = "Maxwell-Boltzmann distribution that broadens to the right"
fform[rsmb]  = " a * (m / ( 2pi kB T))^1.5   4pi (x-x0)^2  exp ( -m (x-x0) / (2 kB T) )"

# -------------------------------------------- Rayleigh distribution

def rr(x, x0, a, sigma):
    xx0 = x-x0
    xx0[xx0<0] = 0
    ps = pow(sigma, -2)
    return a * xx0 * ps * exp ( -xx0*xx0 * 0.5 * ps)

funcs.append(rr)
fkeys.append("rr")

fvlist[rr] = 'peak 0 position, amplitude, scale parameter (sigma)'
fvlen[rr] = 3
fnames[rr] = "Rayleigh distribution that broadens to the right"
fform[rr]  = " a (x-x0)/sigma^2   exp ( - (x-x0)^2 / (2 sigma^2 ))"

def lr(x, x0, a, sigma):
    xx0 = x-x0
    xx0*=-1
    xx0[xx0<0] = 0
    ps = pow(sigma, -2)
    return a * xx0 * ps * exp ( -xx0*xx0 * 0.5 * ps)

funcs.append(lr)
fkeys.append("lr")

fvlist[lr] = 'peak 0 position, amplitude, scale parameter (sigma)'
fvlen[lr] = 3
fnames[lr] = "Rayleigh distribution that broadens to the left"
fform[lr]  = " a (x-x0)/sigma^2   exp ( - (x-x0)^2 / (2 sigma^2 ))"



# -------------------------------------------- log-normal distribution

def llnd(x, x0, a, mu, sigma):
    xx0 = x-x0
    xx0*=-1
    xx = xx0[xx0>0]
    y = np.zeros_like(xx0)

    y[xx0>0] = a * exp ( -0.5 * sigma**-2 *  (np.log(xx) - mu)**2 ) / ( xx * sigma * (2*np.pi)**0.5 ) 
    return y 

funcs.append(llnd)
fkeys.append("llnd")

fvlist[llnd] = 'peak 0 position, amplitude, mu, sigma'
fvlen[llnd] = 4
fnames[llnd] = "Log-normal distribution that broadens to the left"
fform[llnd]  = " a / ( (x-x0) * sigma * 2pi^0.5 )    exp ( - ( ln(x-x0) - mu )^2 / (2 sigma^2 ))"


def lsiX2(x, x0, a, v, t2):
    xx0 = -x+x0

    xx = np.float128(xx0[xx0>0])
    
    v2 =  v/2
    gv2 = gamma_function(v2)

    y = np.zeros_like(xx0)

    v2 = np.float128(v2)

    # Hack time!
    #a^b = ( a^(b/2) )^2 
    
    v8 = v2/4
    y1 = np.float128( (( np.float128(t2)* v2 )**v8) / (np.float128(gv2)**0.25) ) 
    y1 = np.float128(a*y1*y1*y1*y1)

    y1 *= xx**(-1-v2)                 
    y2 = exp( -v*t2*0.5 /xx)
    y[xx0>0] = y1*y2

    y[y==np.inf] = 0
    y[np.isnan(y)] = 0
    return y


funcs.append(lsiX2)
fkeys.append("lsiX2")

fvlist[lsiX2] = 'peak 0 position, amplitude, nu, tau squared'
fvlen[lsiX2] = 4
fnames[lsiX2] = "Scaled inverse chi-squared distribution that broadens to the left"
fform[lsiX2]  = " a * ( (t2 * v/2)**(v/2) / G(v/2)) exp( -v*t2*0.5 /xx) * xx**(-1-v/2)"


# -------------------------------------------- Gaussian 

#ln2=sp.log(2.0)  #numpy.log is ln
#ln2 = 0.6931471805599453
def g(x, m, a, w): #x, middle, amplitude, width (fwhm)
    
    xm  = x-m
    #dc2 = 0.25*w*w/ln2
    #return a*exp(-1*(xm*xm)/dc2)   #  -xm^2 / dc2 = -xm^2 ln2 4 / w^2
    
    #print xm.dtype
    # its float32 with --float32

    #gcoef = -4.0*ln2/(w*w)
    #gcoef = -4.0*0.6931471805599453/(w*w)
    
    gcoef = -2.772588722239781/(w*w)
    return a*exp( xm*xm *gcoef)
    
funcs.append(g)
fkeys.append("g")

fvlist[g] = 'peak pos, amplitude, width (fwhm)'
fvlen[g] = 3
fnames[g] = "gaussian peak"
fform[g]  = "gaussian"


# -------------------------------------------- single-width Voigt  

#https://en.wikipedia.org/wiki/Voigt_profile#Pseudo-Voigt_approximation
def v(x, m, a, fg): # center position, amplitude, fwhm
    
    xm  = x-m
#    return a*voigt_profile(xm, sigma, gamma)

    #gcoef = -4.0*ln2/(fg*fg)
    gcoef = -2.772588722239781/(fg*fg)
    gauss_y = exp( xm*xm * gcoef)

    #hc = fc/2
    hc = fg/2
    ccoef = hc/np.pi 
    
    cauchy_y = ccoef / ( xm*xm + hc*hc)
    
    # fg is gaussian fwhm
    # fc is cauchy fwhm 

    #fc2 = fc*fc
    #fg2 = fg*fg
    #f5 = fg*fg*fg*fg*fg

    #fv = 0.5346*fc * (  0.2166 * fc*fc * fg*fg) **0.5

    #for fg == fc:
    #fv = 1.6376*fg
    
    # f = fg/fv 

    # eta is a function of fc / fv 
    # if fg == fc: fc/fv = fg/fv = 1/1.6376

    #f = (fg*fg2*fg2 + 2.69269*fg2*fg2*fc + 2.42843*fg*fg2*fc2 + 4.47163*fg2*fc2*fc + 0.07842*fg*fc2*fc2 + fc*fc2*fc2)**0.2
    #f = (f5 + 2.69269*f5 + 2.42843*f5 + 4.47163*f5 + 0.07842*f5 + f5)**0.2
    # this adds up to 1.63464

    # simplified:
    #f = 1/1.63464
    #eta = 1.36603*f - 0.47719*f*f + 0.11116*f*f*f
    #eta = 0.68254

    #return a * (eta*cauchy_y +  (1-eta)* gauss_y)
    return a * (0.68254 * cauchy_y + 0.31746 * gauss_y )
    
    
funcs.append(v)
fkeys.append("v")

fvlist[v] = 'peak pos, amplitude,  fwhm'
fvlen[v] = 3
fnames[v] = "pseudo-voigt peak"
fform[v]  = "pseudo-voigt"


# -------------------------------------------- two-width Voigt  

#https://en.wikipedia.org/wiki/Voigt_profile#Pseudo-Voigt_approximation
def v2(x, m, a, fg, fc): # center position, amplitude, gaussian fwhm, cauchy fwhm
    
    xm  = x-m
    #return a*voigt_profile(xm, sigma, gamma)

    #gcoef = -4.0*ln2/(fg*fg)
    gcoef = -2.772588722239781/(fg*fg)
    gauss_y = exp( xm*xm * gcoef)

    hc = fc/2
    ccoef = hc/np.pi 
    
    cauchy_y = ccoef / ( xm*xm + hc*hc)
    
    # fg is gaussian fwhm
    # fc is cauchy fwhm 

    fc2 = fc*fc
    fg2 = fg*fg

    fv = (fg*fg2*fg2 + 2.69269*fg2*fg2*fc + 2.42843*fg*fg2*fc2 + 4.47163*fg2*fc2*fc + 0.07842*fg*fc2*fc2 + fc*fc2*fc2)**0.2

    fcfv = fc/fv

    eta = 1.36603*fcfv - 0.47719*fcfv*fcfv + 0.11116*fcfv*fcfv*fcfv

    return a * (eta*cauchy_y +  (1-eta)* gauss_y)
    
    
funcs.append(v2)
fkeys.append("v2")

fvlist[v2] = 'peak pos, amplitude, gaussian fwhm, cauchy fwhm'
fvlen[v2] = 4
fnames[v2] = "pseudo-voigt peak"
fform[v2]  = "pseudo-voigt"

# -------------------------------------------- Cauchy

def c(x, m, a, b): #x, middle, amplitude, width (fwhm)
    
    abpi = a*b/(2*np.pi)
    #abpi = a*b/(np.pi)  # hwhm
    xm = x-m 
    return abpi/ ( xm*xm + b*b)
    
funcs.append(c)
fkeys.append("c")

fvlist[c] = 'peak pos, amplitude, width (fwhm)'
fvlen[c] = 3
fnames[c] = "cauchy peak"
fform[c]  = "cauchy"

# -------------------------------------------- Rayleigh_scattering


#2 * pi**5 / 3 = 204.0131231901876
def rsnm(x, A, pd,  rn): #x nm, amplitude, paticle diameter nm, refractive index
 
    n2 = rn*rn
    return A*204.0131231901876 * pd**6 * (( n2-1)/(n2+2))**2 / x**4

    
funcs.append(rsnm)
fkeys.append("rsnm")

fvlist[rsnm] = 'amplitude, paticle diameter nm, refractive index'
fvlen[rsnm] = 3
fnames[rsnm] = "Rayleigh scattering, x in nm"
fform[rsnm]  = "A * 0.66666 * pi*5 * d**6 (( n2-1)/(n2+2))**2 / lbd**4 "


# -------------------------------------------- Power function

def pwr(x, A, p):
    if p == 0:
        return sp.ones_like(x)
    elif p > 0:
        return A*spp(x, p)
    elif p < 0:
        return A/spp(x, -p)
    
funcs.append(pwr)
fkeys.append("pwr")

fvlist[pwr] = 'A p'
fvlen[pwr] = 2
fnames[pwr] = "Power function"
fform[pwr]  = "y = A x^p "

# -------------------------------------------

# -------------------------------------------- Frequency modulated signal 1:

def fms(x, A, m, tc, tm):
    mod = sp.sin(2.0*np.pi*x/tm)*m
    car = sp.sin(2.0*np.pi*x/tc)
    return A*sp.sin(2.0*np.pi*(x/tc+mod))
    
funcs.append(fms)
fkeys.append("fms")

fvlist[fms] = 'A m tc tm'
fvlen[fms] = 4
fnames[fms] = "freq mod signla"
fform[fms]  = "freq mod signal"

# -------------------------------------------- Dispersion formula n:
# dispersion formula in a from of n = ...
def ndisp(x,a,b,c,d):
    x2 = x*x
    o = sp.sqrt(a * x2/(x2 - b) + c*x2/(x2-d) +1.0)
    if sp.iscomplexobj(o):
        return sp.real(o*sp.conj(o))
    else:
        return o

funcs.append(ndisp)
fkeys.append("ndisp")

fvlist[ndisp] = 'a b c d '
fvlen[ndisp] = 4
fnames[ndisp] = "Dispersion formula in a form of n = ..."
fform[ndisp]  = " n = (a * lbd^2/(lbd^2 - b) + c*lbd^2/(lbd^20-d) +1)^0.5"



# -------------------------------------------- exp (poly 3):
def ep3(x, a, b, c, d):
    return exp(a + b*x + c*x*x + d*x*x*x)

funcs.append(ep3)
fkeys.append("ep3")

fvlist[ep3] = 'a b c d'
fvlen[ep3] = 4
fnames[ep3] = "3-polynomial, cubic function"
fform[ep3]  = "y = a + b x + c x^2 + d x^3"

# -------------------------------------------- exp (poly 2):
def ep2(x, a, b, c):
    return exp(a + b*x + c*x*x)
   
funcs.append(ep2)
fkeys.append("ep2")

fvlist[ep2] = 'a b c'
fvlen[ep2] = 3
fnames[ep2] = "exp of 2-polynomial"
fform[ep2]  = "y = exp(a + b x + c x^2)"


# -------------------------------------------- Polynomial of order 1:

def p1(x, a, b):
    return a + b*x 

funcs.append(p1)
fkeys.append("p1")

fvlist[p1] = 'a b'
fvlen[p1] = 2
fnames[p1] = "1-polynomial, line"
fform[p1]  = "y = a + b x"

# -------------------------------------------- Polynomial of order 2:
def p2(x, a, b, c):
    return a + b*x + c*x*x  
   
funcs.append(p2)
fkeys.append("p2")

fvlist[p2] = 'a b c'
fvlen[p2] = 3
fnames[p2] = "2-polynomial, parabola"
fform[p2]  = "y = a + b x + c x^2"

# -------------------------------------------- Polynomial of order 3:
def p3(x, a, b, c, d):
    return a + b*x + c*x*x + d*x*x*x  

funcs.append(p3)
fkeys.append("p3")

fvlist[p3] = 'a b c d'
fvlen[p3] = 4
fnames[p3] = "3-polynomial, cubic function"
fform[p3]  = "y = a + b x + c x^2 + d x^3"

# -------------------------------------------- Polynomial of order 4:
def p4(x, a, b, c, d, e):
    xx = x*x
    return a + b*x + c*xx + d*xx*x  + e*xx*xx

funcs.append(p4)
fkeys.append("p4")

fvlist[p4] = 'a b c d e'
fvlen[p4] = 5
fnames[p4] = "4-polynomial"
fform[p4]  = "y = a + b x + c x^2 + d x^3 + e x^4"

# -------------------------------------------- Polynomial of order 5:
def p5(x, a, b, c, d, e, f):
    xx = x*x
    x4 = xx*xx
    return a + b*x + c*xx + d*xx*x  + e*x4 + f*x4*x

funcs.append(p5)
fkeys.append("p5")

fvlist[p5] = 'a b c d e f'
fvlen[p5] = 6
fnames[p5] = "5-polynomial"
fform[p5]  = "y = a + b x + c x^2 + d x^3 + e x^4 + f x^5"

# -------------------------------------------- Polynomial of order 6:
def p6(x, a, b, c, d, e, f, g):
    xx = x*x
    x4 = xx*xx
    return a + b*x + c*xx + d*xx*x  + e*x4 + f*x4*x + g*x4*xx

funcs.append(p6)
fkeys.append("p6")

fvlist[p6] = 'a b c d e f g'
fvlen[p6] = 7
fnames[p6] = "6-polynomial"
fform[p6]  = "y = a + b x + c x^2 + d x^3 + e x^4 + f x^5 + g x^6"

# -------------------------------------------- Lennard-Jones potential:

# V = 4eps ( (sigma6^2 / r^12)  - (sigma6/r^6) )
def lj(x, epsilon, sigma6):
    
    x2 = x*x
    x6 = x2*x2*x2
    x12 = x6*x6

    return 4*epsilon * (  sigma6 * sigma6 / x12 - sigma6 / x6 )


funcs.append(lj)
fkeys.append("lj")

fvlist[lj] = 'epsilon sigma6'
fvlen[lj] = 2
fnames[lj] = "Lennard-Jones potential"
fform[lj]  = "V = 4epsilon ( (sigma6^2 / r^12)  - (sigma6/r^6) )"


# -------------------------------------------- Angular frequency sine wave :
def sin(x, A, w, ph):

    return A*np.sin(w*x + ph)

funcs.append(sin)
fkeys.append("sin")

fvlist[sin] = 'A w ph'
fvlen[sin] = 3
fnames[sin] = "sine wave with angular frequency w and phase ph"
fform[sin]  = "y = A sin (w x + ph)"

# -------------------------------------------- Exponential decay with coefs 
# From DFTB repulsive potential
# y = exp( -a  r + b ) 

def rd(x, a, b):
 
    return exp( -a*x + b)
    
funcs.append(rd)
fkeys.append("rd")

fvlist[rd] = 'a b'
fvlen[rd] = 2
fnames[rd] = "Exponential decay with coefs"
fform[rd]  = "y = exp( -a  r + b )"


# -------------------------------------------- Exponential decay 1 with offset
# y = y0 + A exp ( -(x-x0)/t)

def d1o(x, x0, y0,  A, t):
 
    return y0 + A * exp( -(x-x0)/t)
    
funcs.append(d1o)
fkeys.append("d1o")

fvlist[d1o] = 'x0, y0, A, t'
fvlen[d1o] = 4
fnames[d1o] = "Exponential decay 1 with offsets"
fform[d1o]  = "y = y0 + A exp(-(x-x0)/t)"

# -------------------------------------------- exp(x)
# y = A exp ( x/t)

def r1(x, A, t):
    return  A * exp( x/t)
    
funcs.append(r1)
fkeys.append("r1")

fvlist[r1] = 'A, t'
fvlen[r1] = 2
fnames[r1] = "Exponential rise "
fform[r1]  = "y = A exp(x/t)"


# -------------------------------------------- Exponential decay 1
# y = A exp ( -x/t)

def d1(x, A, t):
    return  A * exp( -x/t)
    
funcs.append(d1)
fkeys.append("d1")

fvlist[d1] = 'A, t'
fvlen[d1] = 2
fnames[d1] = "Exponential decay 1 "
fform[d1]  = "y = A exp(-x/t)"

# -------------------------------------------- Exponential decay 2
# y = A exp ( -x/t)

def d2(x, A, t1, t2):
    return  A * exp( -x/t1) * exp(-x/t2)
    
funcs.append(d2)
fkeys.append("d2")

fvlist[d2] = 'A, t1, t2'
fvlen[d2] = 3
fnames[d2] = "Exp dec times exp dec "
fform[d2]  = "y = A * expd1 * expd2"

# -------------------------------------------- Exponential decay 3
# y = A exp ( -x/t)

def d3(x, A, t1, t2, t3):
    return  A * exp( -x/t1) * exp(-x/t2) * exp(-x/t3)
    
funcs.append(d3)
fkeys.append("d3")

fvlist[d3] = 'A, t1, t2, t3'
fvlen[d3] = 4
fnames[d3] = "Exp dec times exp dec times exp dec"
fform[d3]  = "y = A * expd1 * expd2 * expd3"

# --------------------------------------- g1d1
def g1d1(x, A0, t1, t2):

    return A0 * exp(x/t1)*exp(-x/t2)

    
funcs.append(g1d1)
fkeys.append("g1d1")

fvlist[g1d1] = 'A, t1, t2'
fvlen[g1d1] = 3
fnames[g1d1] = "1 grwoth times 1 decay "
fform[g1d1]  = "y = A0 * exp(x/t1)*exp(-x/t2)"

# --------------------------------------- dsd1
def dsd1(x, A0, t1, t2):

    return A0 * exp(-x/t1) * exp(-x/t1) * exp(-x/t2)
    
funcs.append(dsd1)
fkeys.append("dsd1")

fvlist[dsd1] = 'A, t1, t2'
fvlen[dsd1] = 3
fnames[dsd1] = "1-exp decay squared times 1-exp decay "
fform[dsd1]  = "y = A0 (exp(-x/t1))^2 exp(-x/t2)"

# --------------------------------------- dsd2
def dsd2(x, A0, A3, t1, t2, t3):

    return A0 * exp(-x/t1) * exp(-x/t1) * ( exp(-x/t2) * A3 * exp(-x/t3) )
    
funcs.append(dsd2)
fkeys.append("dsd2")

fvlist[dsd2] = 'A0, A3, t1, t2, t3'
fvlen[dsd2] = 5
fnames[dsd2] = "1-exp decay squared times 2-exp decay "
fform[dsd2]  = "y = A0 (exp(-x/t1))^2 ( exp(-x/t2) + A3 exp(-x/t3))"

# --------------------------------------- d1d2
def d1d2(x, A0, A3, t1, t2, t3):

    return A0 * exp(-x/t1) * ( exp(-x/t2) + A3 * exp(-x/t3) )
    
funcs.append(d1d2)
fkeys.append("d1d2")

fvlist[d1d2] = 'A0, A3, t1, t2, t3'
fvlen[d1d2] = 5
fnames[d1d2] = "1-exp decay times 2-exp decay "
fform[d1d2]  = "y = A0 exp(-x/t1) ( exp(-x/t2) + A3 exp(-x/t3))"


# --------------------------------------- r1d1
def r1d1(x, A0, t1, t2):

    x[x<0] = 0 
    #c = t2 * pow((t1 +t2)/t1, -t1/t2)/(t1+t2)
    
    #return A0 * (1.0 - exp(-x/t1))*exp(-x/t2)/c
    return A0 * (1.0 - exp(-x/t1))*exp(-x/t2)
    
funcs.append(r1d1)
fkeys.append("r1d1")

fvlist[r1d1] = 'A, t1, t2'
fvlen[r1d1] = 3
fnames[r1d1] = "Pulse with 1 rise and 1 decay "
fform[r1d1]  = "y = A (1-exp(-x/t1)) exp(-x/t2)"

# --------------------------------------- d1d1
def d1d1(x, A0, t1, t2):

    return A0 * exp(-x/t1) * exp(-x/t2)
    
funcs.append(d1d1)
fkeys.append("d1d1")

fvlist[d1d1] = 'A, t1, t2'
fvlen[d1d1] = 3
fnames[d1d1] = "1-exp decay times 1-exp decay "
fform[d1d1]  = "y = A0 exp(-x/t1) exp(-x/t2)"

# --------------------------------------- rs1d1
def rs1d1(x, A0, t1, t2):

    return A0 * (1.0 - exp( -x*x/t1))*exp(-x/t2)

    
funcs.append(rs1d1)
fkeys.append("rs1d1")

fvlist[rs1d1] = 'A, t1, t2'
fvlen[rs1d1] = 3
fnames[rs1d1] = "Pulse with 1 rise and 1 decay "
fform[rs1d1]  = "y = A (1-exp(-x^2/t1)) exp(-x/t2)"

# --------------------------------------- r1d1t
def r1d1t(x, A0, A1, t1, t2):

    return (A0 + A1*(1.0 - exp(-x/t1)))*exp(-x/t2)

funcs.append(r1d1t)
fkeys.append("r1d1t")

fvlist[r1d1t] = 'A0, A1, t1, t2'
fvlen[r1d1t] = 4
fnames[r1d1t] = "Pulse with 1 rise and 1 decay "
fform[r1d1t]  = "y = (A0 + A1*(1.0 - exp(-x/t1)))*exp(-x/t2)"

# ----------------------------------------- r1d2

def r1d2(x, A0, A3, t1, t2, t3):

    x[x<0] = 0

    #cc = t2*t3 + t1*t2 + t1*t3
    #c = t2 * t3 * pow( cc/( t1*t2+t1*t3), -t1*(1.0/t2 + 1.0/t3))/cc

    return A0 * (1.0- exp(-x/t1))*(exp(-x/t2)+ A3*exp(-x/t3))
    
funcs.append(r1d2)
fkeys.append("r1d2")

fvlist[r1d2] = 'A0, A3, t1, t2, t3'
fvlen[r1d2] = 5 
fnames[r1d2] = "Pulse with 1 rise and 2 decays "
fform[r1d2]  = "y = A0 * (1.0- exp(-x/t1))*(exp(-x/t2)+ A3*exp(-x/t3))"


# ----------------------------------------- r1d2t

def r1d2t(x, A0, A1, A2, A3, t1, t3, t4):

    expr = 1.0 - exp(-x/t1)
        
    return (A0 + A1 * expr) * exp(-x/t3) + (A2 + A3 * expr) * exp(-x/t4)
    
funcs.append(r1d2t)
fkeys.append("r1d2t")

fvlist[r1d2t] = 'A0, A1, A2, A3, t1, t3, t4'
fvlen[r1d2t] = 7 
fnames[r1d2t] = "Pulse with 1 rise and 2 decays "
fform[r1d2t]  = "y = (A0 + A1 * expr) * exp(-x/t3) + (A2 + A3 * expr) * exp(-x/t4)"

# ----------------------------------------- r1d3
def r1d3(x, A, A3, A4, t1, t2, t3, t4):

    return A * (1.0- exp(-x/t1))*(exp(-x/t2)+A3*exp(-x/t3)+A4*exp(-x/t4))

    
funcs.append(r1d3)
fkeys.append("r1d3")

fvlist[r1d3] = 'A, A3, A4, t1, t2, t3, t4'
fvlen[r1d3] = 7
fnames[r1d3] = "Pulse with 1 rise and 3 decays "
fform[r1d3]  = "y = A (1-exp(-x/t1)) ( exp(-x/t2) + A3 exp(-x/t3) + A4 exp(-x/t4))"

# ----------------------------------------- r1d4
def r1d4(x, A, A3, A4, A5, t1, t2, t3, t4, t5):

    return A * (1.0 - exp(-x/t1)) * ( exp(-x/t2) + A3*exp(-x/t3) + A4*exp(-x/t4) + A5*exp(-x/t5))

    
funcs.append(r1d4)
fkeys.append("r1d4")

fvlist[r1d4] = 'A, A3, A4, A5, t1, t2, t3, t4, t5'
fvlen[r1d4] = 9
fnames[r1d4] = "Pulse with 1 rise and 4 decays "
fform[r1d4]  = "y = A (1-exp(-x/t1)) ( exp(-x/t2) + A3 exp(-x/t3) + A4 exp(-x/t4)) + A5 exp(-x/t5))"

# ----------------------------------------- r1d5
def r1d5(x, A, A3, A4, A5, A6, t1, t2, t3, t4, t5, t6):

    return A * (1.0 - exp(-x/t1)) * ( 
        exp(-x/t2) + A3*exp(-x/t3) + A4*exp(-x/t4) + A5*exp(-x/t5) + A6*exp(-x/t6))

    
funcs.append(r1d5)
fkeys.append("r1d5")

fvlist[r1d5] = 'A, A3, A4, A5, A6, t1, t2, t3, t4, t5, t6'
fvlen[r1d5] = 11
fnames[r1d5] = "Pulse with 1 rise and 5 decays "
fform[r1d5]  = "y = A r1( d2 + A3 d3 + A4 d4 + A5 d5 + A6 d6 )"

# ----------------------------------------- r2d1


def r2d1(x, A0, A2, t1, t2, t3):
    return A0*(1.0-exp(-x/t1)+A2*(1.0-exp(-x/t2)))*exp(-x/t3)
    
funcs.append(r2d1)
fkeys.append("r2d1")

fvlist[r2d1] = 'A0, A2, t1, t2, t3'
fvlen[r2d1] = 5
fnames[r2d1] = "Pulse with 2 rises and 1 decay "
fform[r2d1]  = "y = A0 (1-exp(-x/t1)+A2(1-exp(-x/t2))) exp(-x/t3)"

# ----------------------------------------- r2d1m
# regular r2d1:
# A0 (1-e1 + A2 (1-e2) ) e3 = 
# A0 (1-e1) e3 + A0 A2 (1-e2) e3  = 
# A0 e3 - A0 e13 + A0 A2 e3 - A0 A2 e23 =
# (A0+A0A2) e3 - A0 e 13 -A0 A2 e23


def r2d1m(x, A1, A2, t1, t2, t3):
    #e1 = exp(-x/t1)
    #e2 = exp(-x/t2)
    
    e13 = exp(-x/(t1+t3))
    e23 = exp(-x/(t2+t3))
    
    e3 = exp(-x/t3)
    
    #return A1*(1.0-e1)*e3 + A2*(1.0-e2)*e3
    #  4 multiplications, 3 exps, 3  vectorized sums
    
    # A1*(1.0-exp(-x/t1))*e3 + A2*(1.0-exp(-x/t2))*e3 =
    # A1 e3 - A1 e1 e3 + A2 e3 - A2 e2 e3 = 
    # (A1+A2) e3 - A1 e1 e3 - A2 e2 e3 
    # = (A1+A2) e3 - A1 e13 - A2 e23        3 multiplications, 3 exps, 2 vect sums
    
    return (A1+A2)*e3 - A1*e13 - A2*e23 
    
funcs.append(r2d1m)
fkeys.append("r2d1m")

fvlist[r2d1m] = 'A1, A2, t1, t2, t3'
fvlen[r2d1m] = 5
fnames[r2d1m] = "Pulse with 2 rises and 1 decay, mod "
fform[r2d1m]  = "y = A1 r1 d3 + A2 r2 d3"

# ----------------------------------------- r1r2d1m


def r1r2d1m(x, A1, A2, t1, t2, t3, t4):
    e14 = (1.0-exp(-x/t1))*exp(-x/t4)
    e2 = (1.0-exp(-x/t2))
    e3 = (1.0-exp(-x/t3))
    
    
    return A1*e14*e2 + A2*e14*e3
    #  4 multiplications, 4 exps, 4  vectorized sums

    #    A1*(1.0-exp(-x/t1))*(1.0-exp(-x/t2))*e4 + 
    # +  A2*(1.0-exp(-x/t1))*(1.0-exp(-x/t3))*e4 = 
    # (below, e1 = exp(-x/t1) and so on
    
    #  A1 (1 - e1) (1-e2) e4 +      A2 (1-e1) (1-e3)   e4 = 
    #
    # A1 (1 - e1 - e2 + e12) e4 +  A2  (1 - e1 - e3 + e13) e4 =
    # 
    # A1 e4 - A1 e14 - A1 e24 + A1 e124 + A2 e4 - A2 e14 - A2 e34 + A2 e134 =  
    
    # (A1+A2) e4 - (A1+A2) e14 - A1 e24 +A1 e124 - A2 e34 + A2 e134
    
    # 6 multiplications, 6 exps, 5 vect sums
    
    #return (A1+A2)*e1*e3 - A1*e1*e13 - A2*e1*e23 
    
funcs.append(r1r2d1m)
fkeys.append("r1r2d1m")

fvlist[r1r2d1m] = 'A1, A2, t1, t2, t3, t4 '
fvlen[r1r2d1m] = 6
fnames[r1r2d1m] = "Rise times 2 rises times 1 decay, mod "
fform[r1r2d1m]  = "y = A1 r1 r2 d4 + A2 r1 r3 d4"


# ----------------------------------------- r3d1


def r3d1(x, A0, A2, A3, t1, t2, t3, t4):
    return A0*( 1.0-exp(-x/t1) + A2 * (1.0-exp(-x/t2)) 
                                +A3 * (1.0-exp(-x/t3))  )  *  exp(-x/t4)
    
funcs.append(r3d1)
fkeys.append("r3d1")

fvlist[r3d1] = 'A0, A2, A3, t1, t2, t3, t4'
fvlen[r3d1] = 7
fnames[r3d1] = "Pulse with 3 rises and 1 decay "
fform[r3d1]  = "y = A0 (1-exp(-x/t1)+A2(1-exp(-x/t2))+A3(1-exp(-x/t3))) exp(-x/t4)"

# ----------------------------------------- r4d1


def r4d1(x, A0, A2, A3, A4, t1, t2, t3, t4, t5):
    return A0 * (1.0-exp(-x/t1)  +  A2*(1.0-exp(-x/t2))  +  A3*(1.0-exp(-x/t3)) +
                 A4*(1.0-exp(-x/t4))   )  *  exp(-x/t5)
    
funcs.append(r4d1)
fkeys.append("r4d1")

fvlist[r4d1] = 'A0, A2, A3, A4, t1, t2, t3, t4, t5'
fvlen[r4d1] = 9
fnames[r4d1] = "Pulse with 4 rises and 1 decay "
fform[r4d1]  = "y = A0 (r1 + A2 r2 + A3 r3 + A4 r4 ) d5"

# ----------------------------------------- r4d2


def r4d2(x, A0, A2, A3, A4, A6, t1, t2, t3, t4, t5, t6):
    return A0 * (1.0-exp(-x/t1)  +  A2*(1.0-exp(-x/t2))  +  A3*(1.0-exp(-x/t3)) +
                 A4*(1.0-exp(-x/t4))   )  *  ( exp(-x/t5) + A6*exp(-x/t6))
    
funcs.append(r4d2)
fkeys.append("r4d2")

fvlist[r4d2] = 'A0, A2, A3, A4, A6, t1, t2, t3, t4, t5, t6'
fvlen[r4d2] = 11
fnames[r4d2] = "Pulse with 4 rises and 2 decays "
fform[r4d2]  = "y = A0 (r1 + A2 r2 + A3 r3 + A4 r4 ) (d5 + A6 d6)"

# ----------------------------------------- r2d4
def r2d4(x, A, A2, A4, A5, A6, t1, t2, t3, t4, t5, t6):

    return A * (1.0 - exp(-x/t1)  + A2*(1.0-exp(-x/t2)) ) * ( 
                 exp(-x/t3) + A4*exp(-x/t4) + A5*exp(-x/t5) + A6*exp(-x/t6))

    
funcs.append(r2d4)
fkeys.append("r2d4")

fvlist[r2d4] = 'A, A2, A4, A5, A6, t1, t2, t3, t4, t5, t6'
fvlen[r2d4] = 11
fnames[r2d4] = "Pulse with 2 rises and 4 decays "
fform[r2d4]  = "y = A (1-exp(-x/t1) + A2 exp(-x/t2)) ( exp(-x/t3) + A4 exp(-x/t4) + A5 exp(-x/t5)) + A5 exp(-x/t6))"

# ----------------------------------------- r1d1d2

def r1d1d2(x, A0, A4, t1, t2, t3, t4):
    
    return A0*(1.0-exp(-x/t1))*exp(-x/t2)*(exp(-x/t3)+A4*exp(-x/t4))

    
funcs.append(r1d1d2)
fkeys.append("r1d1d2")

fvlist[r1d1d2] = 'A0, A4, t1, t2, t3, t4'
fvlen[r1d1d2] = 6
fnames[r1d1d2] = "1 rise times 1 decay times 2-exp decay "
fform[r1d1d2]  = "y = A0(1-exp(-x/t1))exp(-x/t2)(exp(-x/t3)+A4 exp(-x/t4))"

# ----------------------------------------- r1r1d1

def r1r1d1(x, A0, t1, t2, t3):
    
    # Normalization goes like, calculate whole thing without A0,
    #   then find max, then multiply y times A0/max
    #y = (1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * exp(-x/t3)
    
    #return y*A0/sp.amax(y)
    
    return A0*(1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * exp(-x/t3)
    
    
funcs.append(r1r1d1)
fkeys.append("r1r1d1")

fvlist[r1r1d1] = 'A0, t1, t2, t3'
fvlen[r1r1d1] = 4
fnames[r1r1d1] = "1 rise times 1 rise times 1-exp decay "
fform[r1r1d1]  = "y = A0(1-exp(-x/t1))(1-exp(-x/t2))exp(-x/t3)"

# ----------------------------------------- r1ar1d1

def r1ar1d1(x, A0, A1, t1, t2, t3):
    
    if A1 > 1:
        A1=1
    elif A1<0:
        A1=0
    # A0 ( 1 (1-A1) + A1 (1-e1) ) (1 - e2) e3
    #    ( 1 - A1   + A1 - A1 e1 )
    #    ( 1             - A1 e1) 
     
    return A0*(1.0 -A1* exp(-x/t1)) * (1.0-exp(-x/t2)) * exp(-x/t3)
    
    
funcs.append(r1ar1d1)
fkeys.append("r1ar1d1")

fvlist[r1ar1d1] = 'A0, A1, t1, t2, t3'
fvlen[r1ar1d1] = 5
fnames[r1ar1d1] = "1 rise with amplitude  times 1 rise times 1-exp decay "
fform[r1ar1d1]  = "y = A0( 1 - A1 e1)(1-e2) e3"

# ----------------------------------------- r1ar1d2

def r1ar1d2(x, A0, A1, A4, t1, t2, t3, t4):
    
    if A1 > 1:
        A1=1
    elif A1<0:
        A1=0
    # A0 ( 1 (1-A1) + A1 (1-e1) ) (1 - e2) e3
    #    ( 1 - A1   + A1 - A1 e1 )
    #    ( 1             - A1 e1) 
     
    return  ( A0 * (1.0 - A1 * exp(-x/t1)  ) * (1.0-exp(-x/t2)) * 
                  (exp(-x/t3) + A4 * exp(-x/t4) ) )
    
    
funcs.append(r1ar1d2)
fkeys.append("r1ar1d2")

fvlist[r1ar1d2] = 'A0, A1, A4, t1, t2, t3, t4)'
fvlen[r1ar1d2] = 7
fnames[r1ar1d2] = "1 rise with amplitude  times 1 rise times 2-exp decay "
fform[r1ar1d2]  = "y = A0( 1 - A1 e1)(1-e2) ( e3 + A4 e4)"


# ----------------------------------------- r1r1r1d1

def r1r1r1d1(x, A0, t1, t2, t3, t4):
    
    return A0*(1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * (1.0-exp(-x/t3)) * exp(-x/t4)
    
    
funcs.append(r1r1r1d1)
fkeys.append("r1r1r1d1")

fvlist[r1r1r1d1] = 'A0, t1, t2, t3, t4'
fvlen[r1r1r1d1] = 5
fnames[r1r1r1d1] = "1 rise times 1 rise times times 1 rise times 1-exp decay "
fform[r1r1r1d1]  = "y = A0 r1 r2 r3 d4"

# ----------------------------------------- r1r2d1

def r1r2d1(x, A0, A3, t1, t2, t3, t4):
    return A0*(1.0-exp(-x/t1)) * (1.0-exp(-x/t2)  + A3*(1.0-exp(-x/t3)) ) * exp(-x/t4)
    # A0 (1-e1) (1 - e2 + A3 (1-e3) ) e4 = 
    # A0 (1-e1) (1-e2) e4 + A0A3 (1-e1) (1-e3) e4 
    
funcs.append(r1r2d1)
fkeys.append("r1r2d1")

fvlist[r1r2d1] = 'A0, A3, t1, t2, t3, t4'
fvlen[r1r2d1] = 6
fnames[r1r2d1] = "1 rise times 2 rise times 1-exp decay "
fform[r1r2d1]  = "y = A0 r1 (r2 + A3 r3) d4"

# ----------------------------------------- r1r3d1

def r1r3d1(x, A0, A3, A4, t1, t2, t3, t4, t5):
    return ( A0 * (1.0-exp(-x/t1)) * 
                  (1.0-exp(-x/t2)  + A3 * (1.0-exp(-x/t3)) + A4 * (1.0-exp(-x/t4)) )
                   * exp(-x/t5) )
    
    
funcs.append(r1r3d1)
fkeys.append("r1r3d1")

fvlist[r1r3d1] = 'A0, A3, A4, t1, t2, t3, t4, t5'
fvlen[r1r3d1] = 8
fnames[r1r3d1] = "1 rise times 3 rise times 1-exp decay "
fform[r1r3d1]  = "y = A0 r1 (r2 + A3 r3 + A4 r4 ) d5"

# ----------------------------------------- r1r2d2

def r1r2d2(x, A0, A3, A5, t1, t2, t3, t4, t5):
    return ( A0 * (1.0-exp(-x/t1)) * (1.0-exp(-x/t2 ) + A3*(1.0-exp(-x/t3)) ) * (exp(-x/t4) + A5*exp(-x/t5)) )
    
    
funcs.append(r1r2d2)
fkeys.append("r1r2d2")

fvlist[r1r2d2] = 'A0, A3, A5, t1, t2, t3, t4, t5'
fvlen[r1r2d2] = 8
fnames[r1r2d2] = "1 rise times 2 rise times 2-exp decay "
fform[r1r2d2]= "y = A0 r1 (r2 + A3 r3) (d4 + A5 d5)"

# ----------------------------------------- r1r2d3

def r1r2d3(x, A0, A3, A5, A6, t1, t2, t3, t4, t5, t6):
    return ( A0 * (1.0-exp(-x/t1)) * (1.0-exp(-x/t2 ) + A3*(1.0-exp(-x/t3)) ) * 
                       (exp(-x/t4) + A5 * exp(-x/t5)  + A6 *  exp(-x/t6 ) )       )
    
    
funcs.append(r1r2d3)
fkeys.append("r1r2d3")

fvlist[r1r2d3] = 'A0, A3, A5, A6, t1, t2, t3, t4, t5'
fvlen[r1r2d3] = 10
fnames[r1r2d3] = "1 rise times 2 rise times 3-exp decay "
fform[r1r2d3]= "y = A0 r1 (r2 + A3 r3) (d4 + A5 d5 + A6 d6)"

# ----------------------------------------- r1r2d2m

def r1r2d2m(x, A124, A125, A134, A135, t1, t2, t3, t4, t5):
    e1 = 1.0-exp(-x/t1)
    e2 = 1.0-exp(-x/t2)
    e3 = 1.0-exp(-x/t3)
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    e12 = e1*e2
    e13 = e1*e3
    
    
    return A124*e12*e4 + A125*e12*e5 + A134*e13*e4 + A135*e13*e5
    
funcs.append(r1r2d2m)
fkeys.append("r1r2d2m")

fvlist[r1r2d2m] = 'A24, A25, A34, A35, t1, t2, t3, t4, t5'
fvlen[r1r2d2m] = 9
fnames[r1r2d2m] = "1 rise times 2 rise times 2-exp decay "
fform[r1r2d2m]= "y = A24 r1 r2 d4 + A25 r1 r2 d5 + A34 r1 r3 d4 + A35 r1 r3 d5"
    
# ----------------------------------------- r1r2d3m

def r1r2d3m(x, A24, A25, A26, A34, A35, A36, t1, t2, t3, t4, t5, t6):
    e1 = 1.0-exp(-x/t1)
    e2 = 1.0-exp(-x/t2)
    e3 = 1.0-exp(-x/t3)
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    e6 = exp(-x/t6)
    e12 = e1*e2
    e13 = e1*e3
    
    
    return (  A24*e12*e4 + A25*e12*e5 + A26*e12*e6 +
              A34*e13*e4 + A35*e13*e5 + A36*e13*e6   )

    
funcs.append(r1r2d3m)
fkeys.append("r1r2d3m")

fvlist[r1r2d3m] = 'A24, A25, A26, A34, A35, A36, t1, t2, t3, t4, t5, t6'
fvlen[r1r2d3m] = 12
fnames[r1r2d3m] = "1 rise times 2 rise times 3-exp decay "
fform[r1r2d3m]= "y = A24 r1 r2 d4 + A25 r1 r2 d5 + A26 r1 r2 d6 + A34 r1 r3 d4 + A35 r1 r3 d5 + A36 r1 r3 d6"



# ----------------------------------------- rsd1

def rsd1(x, A0, t1, t2):

    e1 = 1.0 - exp(-x/t1)
    
    output =  A0 * e1 * e1 * exp(-x/t2)
    output[x<0] = 0
    return output 


funcs.append(rsd1)
fkeys.append("rsd1")

fvlist[rsd1] = 'A0, t1, t2'
fvlen[rsd1] = 3
fnames[rsd1] = "1 rise times same rise times 1-exp decay "
fform[rsd1]  = "y = A0(1-exp(-x/t1))^2 exp(-x/t3)"


# ----------------------------------------- rpd1

def rpd1(x, A0, p, t1, t2):

    x[x<0] = 0
    
    return A0 * spp(1.0 - exp(-x/t1), p) * exp(-x/t2)
    

funcs.append(rpd1)
fkeys.append("rpd1")

fvlist[rpd1] = 'A0, p, t1, t2'
fvlen[rpd1] = 4
fnames[rpd1] = "1 rise to the power p times 1-exp decay "
fform[rpd1]  = "y = A0(1-exp(-x/t1))^p exp(-x/t3)"

# ----------------------------------------- rpd2

def rpd2(x, A0, A3, p, t1, t2, t3):

    x[x<0] = 0
    return A0 * spp(1.0 - exp(-x/t1), p) * ( exp(-x/t2) + A3 * exp(-x/t3) )
    

funcs.append(rpd2)
fkeys.append("rpd2")

fvlist[rpd2] = 'A0, A3, p, t1, t2, t3'
fvlen[rpd2] = 6
fnames[rpd2] = "1 rise to the power p times 2-exp decay "
fform[rpd2]  = "y = A0(1-exp(-x/t1))^p ( exp(-x/t2) + A3 exp(-x/t3) )"

# ----------------------------------------- rpd3

def rpd3(x, A0, A3, A4, p, t1, t2, t3, t4):

    x[x<0] = 0
    return A0 * spp(1.0 - exp(-x/t1), p) * ( exp(-x/t2) + A3 * exp(-x/t3) + A4 * exp(-x/t4) )
    
funcs.append(rpd3)
fkeys.append("rpd3")

fvlist[rpd3] = 'A0, A3, A4,  p, t1, t2, t3, t4'
fvlen[rpd3] = 8
fnames[rpd3] = "1 rise to the power p times 3-exp decay "
fform[rpd3]  = "y = A0(1-exp(-x/t1))^p ( exp(-x/t2) + A3 exp(-x/t3)  + A4 exp(-x/t4) )"

# ----------------------------------------- rcd1

def rcd1(x, A0, t1, t2):
   
    x[x<0] = 0
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * exp(-x/t2)

funcs.append(rcd1)
fkeys.append("rcd1")

fvlist[rcd1] = 'A0, t1, t2'
fvlen[rcd1] = 3
fnames[rcd1] = "1 rise to the power of 3 times 1-exp decay "
fform[rcd1]  = "y = A0(1-exp(-x/t1))^3 exp(-x/t3)"

# ----------------------------------------- rcd2

def rcd2(x, A0, A3, t1, t2, t3):

    x[x<0] = 0
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) )

funcs.append(rcd2)
fkeys.append("rcd2")

fvlist[rcd2] = 'A0, A3, t1, t2, t3'
fvlen[rcd2] = 5
fnames[rcd2] = "1 rise to the power of 3 times 2-exp decay "
fform[rcd2]  = "y = A0(1-exp(-x/t1))^3 ( exp(-x/t2) + A3 exp(-x/t3) )"

# ----------------------------------------- rcd3

def rcd3(x, A0, A3, A4, t1, t2, t3, t4):

    x[x<0] = 0
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) + A4 * exp(-x/t4) )

funcs.append(rcd3)
fkeys.append("rcd3")

fvlist[rcd3] = 'A0, A3, A4, t1, t2, t3, t4'
fvlen[rcd3] = 7
fnames[rcd3] = "1 rise to the power of 3 times 2-exp decay "
fform[rcd3]  = "y = A0(1-exp(-x/t1))^3 ( exp(-x/t2) + A3 exp(-x/t3) + A4 exp(-x/t4) )"
# ----------------------------------------- rqd1

def rqd1(x, A0, t1, t2):
    x[x<0] = 0
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * e1 * exp(-x/t2)

funcs.append(rqd1)
fkeys.append("rqd1")

fvlist[rqd1] = 'A0, t1, t2'
fvlen[rqd1] = 3
fnames[rqd1] = "1 rise to the power of 4 times 1-exp decay "
fform[rqd1]  = "y = A0(1-exp(-x/t1))^4 exp(-x/t3)"

# ----------------------------------------- rqd2

def rqd2(x, A0, A3, t1, t2, t3):
    x[x<0] = 0
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) )

funcs.append(rqd2)
fkeys.append("rqd2")

fvlist[rqd2] = 'A0, A3, t1, t2, t3'
fvlen[rqd2] = 5
fnames[rqd2] = "1 rise to the power of 4 times 2-exp decay "
fform[rqd2]  = "y = A0(1-exp(-x/t1))^4 ( exp(-x/t2) + A3 exp(-x/t3) )"

# ----------------------------------------- rqd3

def rqd3(x, A0, A3, A4, t1, t2, t3, t4):
    x[x<0] = 0
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) + A4 * exp(-x/t4) )

funcs.append(rqd3)
fkeys.append("rqd3")

fvlist[rqd3] = 'A0, A3, A4, t1, t2, t3, t4'
fvlen[rqd3] = 7
fnames[rqd3] = "1 rise to the power of 4 times 3-exp decay "
fform[rqd3]  = "y = A0(1-exp(-x/t1))^4 ( exp(-x/t2) + A3 exp(-x/t3)  + A4 exp(-x/t4 )"

# ----------------------------------------- rsd1d1

def rsd1d1(x, A0, t1, t2, t3):
    
    e1 = 1.0 - exp(-x/t1)
    return A0 * e1 * e1 * exp(-x/t2) * exp(-x/t3) 

    
funcs.append(rsd1d1)
fkeys.append("rsd1d1")

fvlist[rsd1d1] = 'A0, t1, t2, t3'
fvlen[rsd1d1] = 4
fnames[rsd1d1] = "1 rise times same rise times 1-exp decay times 1-exp decay "
fform[rsd1d1]  = "y = A0(1-exp(-x/t1))^2 exp(-x/t2)  exp(-x/t3)"

# ----------------------------------------- rsd2

def rsd2(x, A0, A3, t1, t2, t3):
    
    e1 = 1.0 - exp(-x/t1)
    
    output =  A0*  e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) )
    output[x<0] = 0
    return output 

    
funcs.append(rsd2)
fkeys.append("rsd2")

fvlist[rsd2] = 'A0, A3, t1, t2, t3'
fvlen[rsd2] = 5
fnames[rsd2] = "1 rise times same rise times 2-exp decay "
fform[rsd2]  = "y = A0(1-exp(-x/t1))^2 ( exp(-x/t2) + A3 exp(-x/t3)"

# ----------------------------------------- rsd4

def rsd4(x, A0, A3, A4, A5, t1, t2, t3, t4, t5):
    
    x[x<0] = 0
    e1 = 1.0 - exp(-x/t1)


    return A0 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) + A4 * exp(-x/t4) +  A5 * exp(-x/t5))

funcs.append(rsd4)
fkeys.append("rsd4")

fvlist[rsd4] = 'A0, A3, A4, A5, t1, t2, t3, t4, t5'
fvlen[rsd4] = 9
fnames[rsd4] = "1 rise times same rise times 4-exp decay "
fform[rsd4]  = "y = A0(1-exp(-x/t1))^2 ( exp(-x/t2) + A3 exp(-x/t3) + A4 exp(-x/t4) + A5 exp(-x/t5)"
# ----------------------------------------- rsd3

def rsd3(x, A0, A3, A4, t1, t2, t3, t4):
    
    x[x<0] = 0
    e1 = 1.0 - exp(-x/t1)


    return A0 * e1 * e1 * ( exp(-x/t2) + A3 * exp(-x/t3) + A4 * exp(-x/t4))

funcs.append(rsd3)
fkeys.append("rsd3")

fvlist[rsd3] = 'A0, A3, A4, t1, t2, t3, t4'
fvlen[rsd3] = 7
fnames[rsd3] = "1 rise times same rise times 3-exp decay "
fform[rsd3]  = "y = A0(1-exp(-x/t1))^2 ( exp(-x/t2) + A3 exp(-x/t3) + A4 exp(-x/t4)"

# ----------------------------------------- rs2d3

def rs2d3(x, A0, A2, A4, A5, t1, t2, t3, t4, t5):

    e1 = 1.0 - exp(-x/t1)
    e2 = 1.0 - exp(-x/t2)

    return A0 * ( e1*e1 + A2*e2*e2) * ( exp(-x/t3) + A4 * exp(-x/t4) + A5 * exp(-x/t5))
    
funcs.append(rs2d3)
fkeys.append("rs2d3")

fvlist[rs2d3] = 'A0, A2, A4, A5, t1, t2, t3, t4, t5'
fvlen[rs2d3] = 9
fnames[rs2d3] = "2 squared rises times 3-exp decay "
fform[rs2d3]  = "y = A0( (1-e1)^2 + A2(1-e1)^2) (e3 + A4 e4 + A5 e5)"

# ----------------------------------------- rs2d3m

def rs2d3m(x, A13, A14, A15, A23, A24, A25, t1, t2, t3, t4, t5):

    e1 = 1.0 - exp(-x/t1)
    e2 = 1.0 - exp(-x/t2)
    e11=e1*e1
    e22=e2*e2
    e3 = exp(-x/t3)
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)

    return    A13*e11*e3 + A14*e11*e4 + A15*e11*e5 + A23*e22*e3 + A24*e22*e4 + A25*e22*e5
    
funcs.append(rs2d3m)
fkeys.append("rs2d3m")

fvlist[rs2d3m] = 'A13, A14, A15, A23, A24, A25, t1, t2, t3, t4, t5'
fvlen[rs2d3m] = 11
fnames[rs2d3m] = "2 squared rises times 3-exp decay, mod"
fform[rs2d3m]  = "y = A13 e1 e3 + A14 e1 e4 + A15 e1 e5 + A23 e2 e3 + A24 e2 e4 + A25 e2 e5, e1,e2 are (1-e)^2"

# ----------------------------------------- r1d1d1

def r1d1d1(x, A0, t1, t2, t3):

    return A0* (1.0-exp(-x/t1)) * exp(-x/t2) * exp(-x/t3)
    
funcs.append(r1d1d1)
fkeys.append("r1d1d1")

fvlist[r1d1d1] = 'A0, t1, t2, t3'
fvlen[r1d1d1] = 4
fnames[r1d1d1] = "1 rise times 1 decay times 1-exp decay "
fform[r1d1d1]  = "y = A0(1-exp(-x/t1))exp(-x/t2)exp(-x/t3)"




# ----------------------------------------- r1r1d2

def r1r1d2(x, A0, A4, t1, t2, t3, t4):
   
    #y  = (1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * (exp(-x/t3) + A4 * exp(-x/t4))
   
    #return A0 * y /sp.amax(y)
    
    return A0*(1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * (exp(-x/t3) + A4 * exp(-x/t4))


funcs.append(r1r1d2)
fkeys.append("r1r1d2")

fvlist[r1r1d2] = 'A0, A4, t1, t2, t3, t4'
fvlen[r1r1d2] = 6
fnames[r1r1d2] = "1 rise times 1 rise times 2-exp decay "
fform[r1r1d2]  = "y = A0(1-exp(-x/t1))(1-exp(-x/t2))(exp(-x/t3)+A4 exp(-x/t4))"

# ----------------------------------------- r1r1d3

def r1r1d3(x, A0, A4, A5, t1, t2, t3, t4, t5):

    
    return A0*(1.0-exp(-x/t1)) * (1.0-exp(-x/t2)) * (
                                exp(-x/t3) + A4 * exp(-x/t4) + A5 * exp(-x/t5))


funcs.append(r1r1d3)
fkeys.append("r1r1d3")

fvlist[r1r1d3] = 'A0, A4, A5, t1, t2, t3, t4, t5'
fvlen[r1r1d3] = 8
fnames[r1r1d3] = "1 rise times 1 rise times 3-exp decay "
fform[r1r1d3]  = "y = A0 r1 r2 ( d3 + A4 d4 + A5 d5 )"

# ----------------------------------------- r2d2


def r2d2(x, A0, A2, A4, t1, t2, t3, t4):

    return A0 * ( 1.0 - exp(-x/t1) + A2 * (1.0-exp(-x/t2))   ) * (
                 exp(-x/t3) + A4 * exp(-x/t4)   )

    
funcs.append(r2d2)
fkeys.append("r2d2")

fvlist[r2d2] = 'A, A1, A2, A3, A4, t1, t2, t3, t4'
fvlen[r2d2] = 7
fnames[r2d2] = "Pulse with 2 rise and 2 decay "
fform[r2d2]  = "y = A (1-A1exp(-x/t1)-A2exp(-x/t2)) (A3 exp(-x/t3) + A4 exp(-x/t4))"

# ----------------------------------------- r2d2m

def r2d2m(x, A1, A2, A3, A4, t1, t2, t3, t4):
    e1 = (1.0 - exp(-x/t1))
    e2 = (1.0 - exp(-x/t2))
    e3 = exp(-x/t3)
    e4 = exp(-x/t4)
    return A1*e1*e3 + A2*e1*e4 + A3*e2*e3 + A4*e2*e4 
    
funcs.append(r2d2m)
fkeys.append("r2d2m")

fvlist[r2d2m] = 'A1, A2, A3, A4, t1, t2, t3, t4'
fvlen[r2d2m] = 8
fnames[r2d2m] = "Pulse with 2 rise and 2 decay "
fform[r2d2m]  = "y = A_1 r_1 d_3 + A_2 r_1 d_4 + A_3 r_2 d_3 + A_4 r_2 d_4"



# ----------------------------------------- r2d3m

def r2d3m(x, A1, A2, A3, A4, A5, A6, t1, t2, t3, t4, t5):
    e1 = (1.0 - exp(-x/t1))
    e2 = (1.0 - exp(-x/t2))
    e3 = exp(-x/t3)
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    return A1*e1*e3 + A2*e1*e4 + A3*e1*e5 + A4*e2*e3 + A5*e2*e4 + A6*e2*e5
    
funcs.append(r2d3m)
fkeys.append("r2d3m")

fvlist[r2d3m] = 'A1, A2, A3, A4, A5, A6, t1, t2, t3, t4, t5'
fvlen[r2d3m] = 11
fnames[r2d3m] = "Pulse with 2 rise and 3 decay "
fform[r2d3m]  = "y = A1 r1 d3 + A2 r1 d4 + A3 r1 d5 + A4 r2 d3 + A5 r2 d4 + A6 r2 d5"

# ----------------------------------------- r3d3m

def r3d3m(x, A1, A2, A3, A4, A5, A6, A7, A8, A9, t1, t2, t3, t4, t5, t6):
    e1 = (1.0 - exp(-x/t1))
    e2 = (1.0 - exp(-x/t2))
    e3 = (1.0 - exp(-x/t3))
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    e6 = exp(-x/t6)
    
    return (  A1*e1*e4 + A2*e1*e5 + A3*e1*e6 
            + A4*e2*e4 + A5*e2*e5 + A6*e2*e6 
            + A7*e3*e4 + A8*e3*e5 + A9*e3*e6  ) 
    
funcs.append(r3d3m)
fkeys.append("r3d3m")

fvlist[r3d3m] = 'A1, A2, A3, A4, A5, A6, A7, A8, A9, t1, t2, t3, t4, t5, t6'
fvlen[r3d3m] = 15
fnames[r3d3m] = "Pulse with 3 rise and 3 decay "
fform[r3d3m]  = "y = A1 r1 d4 + A2 r1 d5 + A3 r1 d6 + A4 r2 d4 + A5 r2 d5 + A6 r2 d6 + A7 r3 d4 + A8 r3 d5 + A9 r3 d6 "
    
# ----------------------------------------- r2d4m

def r2d4m(x, A1, A2, A3, A4, A5, A6, A7, A8, t1, t2, t3, t4, t5, t6):
    e1 = (1.0 - exp(-x/t1))
    e2 = (1.0 - exp(-x/t2))
    e3 = exp(-x/t3)
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    e6 = exp(-x/t6)
    return (  A1*e1*e3 + A2*e1*e4 + A3*e1*e5 + A4*e1*e6 +
              A5*e2*e3 + A6*e2*e4 + A7*e2*e5 + A8*e2*e6   )
    
funcs.append(r2d4m)
fkeys.append("r2d4m")

fvlist[r2d4m] = 'A1, A2, A3, A4, A5, A6, A7, A8, t1, t2, t3, t4, t5, t6'
fvlen[r2d4m] = 14
fnames[r2d4m] = "Pulse with 2 rise and 3 decay "
fform[r2d4m]  = "y = A1 r1 d3 + A2 r1 d4 + A3 r1 d5 + A4 r1 d6 + A5 r2 d3 + A6 r2 d4 + A7 r2 d5 + A8 r2 d6"
    
# ----------------------------------------- r2d3


def r2d3(x, A0, A2, A4, A5, t1, t2, t3, t4, t5):

    return A0 * (  1.0 - exp(-x/t1)  + A2 * (1.0 - exp(-x/t2))  ) * ( 
                  exp(-x/t3) + A4 * exp(-x/t4) + A5 * exp(-x/t5))
    
funcs.append(r2d3)
fkeys.append("r2d3")

fvlist[r2d3] = 'A0, A2, A4, A5, t1, t2, t3, t4, t5'
fvlen[r2d3] = 9
fnames[r2d3] = "Pulse with 2 rise and 3 decay "
fform[r2d3]  = "y = A ( (1 - exp(-x/t1)) + A2 (1 - exp(-x/t2))) ( exp(-x/t3) + A4 exp(-x/t4) + A5 exp(-x/t5)  )"

# ----------------------------------------- r3d2


def r3d2(x, A0, A2, A3, A5, t1, t2, t3, t4, t5):
    return A0 * (  1.0-exp(-x/t1) + A2*(1.0-exp(-x/t2)) + A3*(1.0-exp(-x/t3))) * (
                  exp(-x/t4) + A5 * exp(-x/t5))
    
funcs.append(r3d2)
fkeys.append("r3d2")

fvlist[r3d2] = 'A0, A2, A3, A5, t1, t2, t3, t4, t5'
fvlen[r3d2] = 9
fnames[r3d2] = "Pulse with 3 rises and 2 decays "
fform[r3d2]  = "y = A0 (1-exp(-x/t1)+A2(1-exp(-x/t2))+A3(1-exp(-x/t3)))  ( exp(-x/t4) + A5 exp(-x/t5)  )"


# ----------------------------------------- r3d2m

def r3d2m(x, A14, A15, A24, A25, A34, A35, t1, t2, t3, t4, t5):
    e1 = (1.0 - exp(-x/t1))
    e2 = (1.0 - exp(-x/t2))
    e3 = (1.0 - exp(-x/t3))
    e4 = exp(-x/t4)
    e5 = exp(-x/t5)
    return A14*e1*e4 + A15*e1*e5 + A24*e2*e4 + A25*e2*e5 + A34*e3*e4 + A35*e3*e5
    
funcs.append(r3d2m)
fkeys.append("r3d2m")

fvlist[r3d2m] = 'A14, A15, A24, A25, A34, A35, t1, t2, t3, t4, t5'
fvlen[r3d2m] = 11
fnames[r3d2m] = "Pulse with 2 rise and 3 decay "
fform[r3d2m]  = "y = A14 r1 d4 + A15 r1 d5 + A24 r2 d4 + A25 r2 d5 + A34 r3 d4 + A35 r3 d5"

# ----------------------------------------- r3d3


def r3d3(x, A0, A2, A3, A5, A6, t1, t2, t3, t4, t5, t6):
    return A0 * (  1.0-exp(-x/t1) + A2*(1.0-exp(-x/t2)) + A3*(1.0-exp(-x/t3))) * (
                    exp(-x/t4) + A5 * exp(-x/t5) + A6 * exp(-x/t6))
    
funcs.append(r3d3)
fkeys.append("r3d3")

fvlist[r3d3] = 'A0, A2, A3, A5, A6, t1, t2, t3, t4, t5, t6'
fvlen[r3d3] = 11
fnames[r3d3] = "Pulse with 3 rises and 3 decays "
fform[r3d3]  = "y = A0 ( r1 + A2 r2 + A3 r3)  ( d4 + A5 d5 + A6 d6  )"

