#!/usr/bin/python
# ===========================================================================
# =========================================================== SHELLFIT ======
# ===========================================================================
# 
# Version 2025.11.07
#
# A function fitting code utilizing shell-style history. 
# Press up to get your last fit result as the new fit input. 
# 
# Author: dr Andrii Shyichuk, University of Wrocław, 
# email: andrii.shyichuk@uwr.edu.pl 
#
#  This code is distributed under a Source-Available license.
#  Commercial use requires a separate license. Contact me for details.
#  Copyright (c) 2025 Andrii Shyichuk. All rights reserved.
#
# ===========================================================================
# Beware: the code uses main as a container for functions and data
# ===========================================================================
#
#
#
# ===========================================================================
# ====================================================== GENERAL INFO =======
# ===========================================================================
#
# This program fits a given function to an experimental curve from the input 
#   file. Input file must be a multi-column whitespace-separated data file.
#
# Output file will contain formula of the function, optimized parameters and 
#   the fitted curve
#
# Input file name is automatically the job name. 
#
# There will be a jobname.history file with guess history.
#
# The program supports function mixing, add functions one by one as much 
#   as you need.
#
# ===========================================================================
#
# Note: there are two kinds of offsets, global and function-specific
# Global offsets xo and yo act on the whole sum of functions.
# Function-specific offsets (if present in the definition) only appy to 
#   their respective functions.
# Function-specific offsets are not recommended.
#
# ===========================================================================

import readline as rl 
# readline has different versions issues, lets make an alternative manual reader

import sys, os

# Thread limit for numpy. It is not more efficient with more threads, at least
#  the least_squares routine. 
# This gotta go before "import numpy"
# https://stackoverflow.com/questions/30791550/limit-number-of-threads-in-numpy
os.environ["OMP_NUM_THREADS"] = "1"


import scipy as sp
from scipy.optimize import least_squares as lsq 
from matplotlib import pyplot as plt
import datetime

from shellfitfuncs import *

# External module is loaded after shellfitfuncs.
# Thus, funcs list and other function-container lists already exist.

i = None
try:
    i=sys.argv.index("-e")
except Exception:
    try:
        i=sys.argv.index("--external")
    except Exception:
        pass

if i != None:
    exname = sys.argv[i+1]
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("external", exname)
    exte = importlib.util.module_from_spec(spec)
    sys.modules["external"] = exte
    spec.loader.exec_module(exte)

     # Import everything that doesn't start with "_"
    globals_get = globals()
    for name in dir(exte):
        if not name.startswith("_"):
            globals_get[name] = getattr(exte, name)
   
    print("External module imported:", exname) 
    print("External module comment:", external_comment)
    print

    del sys.argv[i+1], sys.argv[i]
    del i

colors = ['black', 'blue', 'green', 'red', 'pink', 'yellow', 'cyan']

inf = np.inf 

# ===========================================================================
# =========================================================== CONVENTION ====
# ===========================================================================
#
# The functions are to be called as f(*args)
# Residual is calcualted by wrapper fuction 
#
# ===========================================================================

X  = []     # global X
Y  = []     # global Y (fit)
Ye = []     # global Y (experimental)

# This arrays are declared here so that the functions below do not complain about
#   unassigned variables. The real variables are declared below, after file read.

func = None
slen = 0

# ===========================================================================
# =========================================================== CONSTANTS =====
# ===========================================================================

exp = np.exp 
ni = np.inf

kB = 8.61733035051e-5 # eV/K

# ===========================================================================
# ================================================ FUNCTION DEFINITION ======
# ===========================================================================

# =============================================== Digits formattings function 

def digform(fl):
    global digits
    return ''.join(['%#.', str(digits), 'g']) % fl 

# ======================================================== Fix SCale function

def fsc(x):

    #y = x[:]
    y = np.zeros_like(x)
    
    for i in range(0, len(x)):
        if x[i] == 0:
            y[i] = 0.00000000001
        elif x[i]<0:
            y[i] = -x[i]
        else:
            y[i] = x[i]
    
    return y 

# ======================================================= File read function

def readfile(inpfile, xl, xu, fl, fu, sk, x0, xc, yc):  
    #I'm doing it the wrong way coz  I'm lazy
    global normalize
    
    # full resolution flag
    # 0 - N.A.
    # 1 not the full resolution region
    # 2 full resolution region
    
    if fl == None and fu == None:
        frfl = 0 
    else:
        frfl = 1
    
    # column indices
    xi = xc - 1
    yi = yc - 1 

    # test xl, xu for "p" at the end and crop datasequence accordingly 

    xpu = None
    xpl = 0
    
    fpl = None
    fpu = None
    
    # This weird code goes as follows.
    # Array can return stuff x[y:] even if y is 0.
    # So, xpl (points to skip at the beginning) is set to 0 and remains 0 
    #    unless 123p input is given.
    # However, arrays do not return stuff for [:0], but return for [:None].
    # So, xpu is set to None.
    # If there are points to skip at the end, it is set to -int(input[:-1]),
    #   so that array x[:-y] will be y points from the end shorter.
    
    if xl == None:
        xl = -np.inf
    elif xl[-1] == "p":
        xpl = int(xl[:-1])
        xl = -np.inf 
    else:
        xl = float(xl)
        
    if xu == None:
        xu = np.inf
    elif xu[-1] == "p":
        xpu = -int(xu[:-1])
        xu = np.inf 
    else:
        xu = float(xu)

    if frfl != 0:
        if fl == None:
            fl = -np.inf
        elif fl[-1] == "p":
            fpl = int(fl[:-1])
            fl = -np.inf 
        else:
            fl = float(fl)
        
        if fu == None:
            fu = np.inf
        elif fu[-1] == "p":
            fpu = -int(fu[:-1])
            fu = np.inf 
        else:
            fu = float(fu)
    
    xerr = False
        # xl must be less then xu
    if xl >= xu:
        print("Error: lower bound is larger then upper bound:", xl, xu, "(units of x).")
        xerr= True
    
    if xpu != None and xpl >= xpu:
        
            print("Error: lower bound is larger then upper bound:", xpl, xpu, "(points).")
            xerr= True
    if frfl != 0:
        if fl >= fu:
            print("Error: full resolution lower bound is larger then full resolution upper bound:", fl, fu, "(units of x).")
            xerr= True
        if fpl >= fpu:
            if not (fpl == None and fpu == None):
                print("Error: full resolution lower bound is larger then full resolution upper bound:", fpl, fpu, "(points).")
                xerr= True
    if xerr:
        print("Exiting due input errors.")
        sys.exit()

    
    
    inpf = open(inpfile, 'r')
    
    if normalize:
        ymn = inf
        ymx = -inf
    
    aX = []
    aY = []
    for line in inpf:
        lsp = line.split()

        try:
                x = float(lsp[xi])

                if normalize or (xl <= x <= xu):
                    
                    try:
                        flsp1 = float(lsp[yi])
                    except ValueError:
                        flsp1 = 0.0
                
                if normalize:
                    if flsp1 < ymn:
                        ymn=flsp1
                    if flsp1 > ymx:
                        ymx = flsp1
            
                if xl <= x <= xu:
                    aX.append(x)
                    aY.append(flsp1)
            
        except Exception:
                pass
    
    if not aX:
        print("Something wrong, no data sequence created.")
        print("Either bad file or insufficient -u/-f.")
        sys.exit()
    
    # Sort array anyway, what if its messed up in the file
    agsX = np.argsort(aX)[xpl:xpu]
    
    
    if normalize:
        yd = ymx - ymn
        ymnd = ymn/yd
        
        # Y -= ymin, then Y/=(ymax - ymin)
        # or, together:
        # (Y-ymin)/(ymax-ymin) = (Y/(ymax-ymin) - ymin/(ymax-ymin))
         
        for ii in range(0, len(aX)):
            aY[ii] = aY[ii] / yd - ymnd
    
    # sort aX and get array of indices of elements of aX that will return a sorted array
    # we crop the array using [xpl:xpu]
    
    if sk <= 0:
        
        # if no skip

        bX = []
        bY = []
        
        for i in agsX:
            bX.append(aX[i])
            bY.append(aY[i])
        

        rX = np.array(bX, dtype=def_dtype)
        rY = np.array(bY, dtype=def_dtype)
    
    else:
        
        frfl = 1
        #special region key 
        
        bX = []
        bY = []
        
        sk1 = sk+1
        d = float(sk1)
    
        
        lx = len(agsX)
        
        for i in range(0, lx, sk1):
            
            mx = 0.0
            my = 0.0
            d  = 0.0
            
            spX = []
            spY = []
            
            for j in range(0, sk1):
                
                ij = i+j
                
                # so it goes along ranges until ij == lx
                if ij < lx:
                
                    k = agsX[ij]
                    #k is index of current x-y data in the aX, aY arrays, sorted x
                    
                    # if x[k] is not in spr - it will be averaged 
                    # else, it will be appended
                    
                    # if it is not the special region
                    if frfl == 1:
                        # check maybe it is
                        if fpl == None: 
                            if fu >= aX[k] >= fl:
                                frfl = 2
                        elif fpu >= ij >= fpl:
                            frfl = 2
                            
                    # if it is the special region
                    elif frfl == 2:
                        # check maybe it is no more 
                        if fpu == None:
                            if aX[k] > fu:
                                frfl = 1 
                        elif ij > fpu:
                            frfl = 1
                            
                    
                    if frfl == 1:
                
                        mx+=aX[k]
                        my+=aY[k]
                        d+=1.0
                        
                    elif frfl ==2:
                        spX.append(aX[k])
                        spY.append(aY[k])
                        
   
                
                # else, e.g. ij == lx, it is time to exit
                #
                # when ij == lx it means that ij index is larger by 1 
                #  than max index of the range
                #
                # so far, components from j = 0, 1, ... lx-i are in the sum, 
                #  and there are j of them when ij == lx 

            if mx !=0.0 and my != 0.0:
                bX.append(mx/d)
                bY.append(my/d)
                
            if spX and spY:
                bX+=spX
                bY+=spY
                
            
        #print(xl, xpl, xu, xpu
        
        rX = np.array(bX, dtype=def_dtype)
        rY = np.array(bY, dtype=def_dtype)
        

        
    if x0 == None:
        
        return rX, rY
        
    else:
            
        return rX-rX[0]+x0, rY 
        


# ============================================================ GSPLIT
#
# splits guess array on the basis of functions in gflist

def gsplit(arr):
    global gflist, fvlen
    
    #print(gflist, arr 
    
    la = len(arr)
    
    out = []
    
    i = 0 
    for f in gflist:
        out.append([])
        for j in range(0, fvlen[f]):
            out[-1].append(arr[i])
            i+=1
    return out 
    
  
# =========================================================== filter function
def numfilter(inparray):
    rarray = np.clip(np.nan_to_num(inparray), a_min=-1e100, a_max=1e100)
    if np.iscomplexobj(rarray):
        return np.sqrt(np.real(rarray*np.conj(rarray)))
    else:
        return rarray
        
    
# =========================================================== WRAPPER FUNCTION 
#
# Let us build wrapper with sp.least_squares in mind.
# Wrapper calcualtes delta for all samples.

def wrap(args, **kwargs):
    
    global gflist
    
    # task 0 is calculate and return residual
    # task 1 is calculate and plot stuff
           
    if not "task" in kwargs:
        task = 0
    else:
        task = kwargs["task"]
        
    zargs = gsplit(args)
    
    D = np.zeros(L, float)
    x0 = 0.0
    for j in range(0, nf):
        
        if gflist[j] == xo:
            x0 = zargs[j][0]
        
        elif gflist[j] == yo:
            D += zargs[j][0]
        
        else:
            if nfilter:
                D += numfilter(gflist[j](Xe-x0, *zargs[j]))
            else:
                D += gflist[j](Xe-x0, *zargs[j])

    if task == 0:
        D -=Ye

        # Residual normalization (in a classical sense, division by residual max)
        #   is not kosher:
        # residual is used to get gradient, 
        #   and if residual has a different norm at different grad steps - 
        #   the whole thing kinda loses sense. 
        # Thus, mixing via normalization is not good;
        # I.e. norm_res_fraction*D_norm/ D_norm.max + (1-norm_res_fraction)*D/D.max() is not ok. 
        # Lets stick to linear mixing, meh. 

        # Also, compression based on average is thus also not ok.

        if normalize_residual == 1 and norm_res_fraction != 0 :
            Ye_ne_0 = Ye!=0
            D_norm = np.copy(D)

            D_norm[Ye_ne_0]/=Ye[Ye_ne_0]
            
            if norm_res_fraction == 1:
                D = D_norm
            else:
                D = norm_res_fraction*D_norm + (1-norm_res_fraction)*D


        elif normalize_residual == 2 and norm_res_fraction != 0:
            
            abs_D = np.absolute(D)

            residual_average = np.average(abs_D)

            aDm = abs_D.max()

            #compressed_residual = np.clip(D, -residual_average, residual_average)

            compressed_residual = np.copy(D)
            
            # Idea: values higher than the average will be multiplied by the ratio of average/max
            # Max will be reduced to average, the rest will be reduced proportionally. 
            compressed_residual[abs_D>=residual_average] *= ( residual_average/aDm)
            # compressed residual max is now residual_average
            # compressed_residual.max() before multipliction is aDm
            # after its aDm * residual_average/aDm == residual_average
            
            if norm_res_fraction == 1:
                D = compressed_residual
            else:
                #D = norm_res_fraction * compressed_residual / residual_average  + ( 
                #          1-norm_res_fraction) * D / aDm

                D = norm_res_fraction * compressed_residual  + ( 1-norm_res_fraction) * D 

    elif task == 1:
        pass
    
    return D
         

# ========================================================== Plotting function

# styles contains linewidth and color index
styles = [[2,0, '-'], [1.5, 1, '-'], [1, 2, '--'], [0.5, 3, '-']]


# tasks
# 1 = plot and recursively plot residual on double click
# 2 = save
# 3 = 1 + 2
# 4 just plot 

def mkplot(arrs, types, ttl, task, **kwargs):
    
        global Xe, styles, logplot, generator
        
        if len(arrs)!=len(types):
            print("Error in mkplot: arrs and types lenght mismatch. Return None.")
            return None
        
        fig = plt.figure()

        
        if not generator:
            ax1  = plt.axes()
            ax2 = ax1.twinx()
        
        else:
            ax2  = plt.axes()




        im = len(arrs)
       
        for i in range(0, im):
            j = types[i]
            if j == 3:
                ax = ax1
                zo = 0
            else:
                ax = ax2
                zo = i+1
                
            
            ax.plot(Xe, arrs[i], lw = styles[j][0], color = colors[styles[j][1]],
                                 ls = styles[j][2], zorder = zo )
        
        if "ylim" in kwargs:
            
            mn, mx = kwargs["ylim"]
            
            dm = mx - mn
            dm5p = dm*0.05
            
            ax2.set_ylim([mn-dm5p, mx+dm5p])    
        
        if not generator:
            ax1.tick_params(axis='y', colors='r', which='both', labelleft=False, labelright=True)
            ax1.set_xlim(np.amin(Xe), np.amax(Xe))
        else:
            ax2.set_xlim(np.amin(Xe), np.amax(Xe))
        ax2.tick_params(axis='y', which='both', labelleft=True, labelright=False)
            
        
        if task in [1,3]:
            connection_id = fig.canvas.mpl_connect('button_press_event', onclick)
            
        
        if task in [2,3]:
            outn = ''.join([jobname, ".", datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S"), ".png"])
            plt.savefig(outn)
        
        if task in [1,3,4]:
            plt.show()
        
        return None
    
# This is a double click tracer, which will plot residual in a separate window.

def onclick(event):
    global Rplot
    if event.dblclick:
        if type(Rplot) != type(None):
            if len(plt.get_fignums()) ==1:        # if no skip

                mkplot([Rplot], [3], "", 4)
        else:
            print("Double-click on the graph plots residual - if any.")
        
# ===========================================================================
# ============================================= Function that does the fit ==
# ===========================================================================

#residual plot pointer    
Rplot = None

def dothefit(guess, bounds, plotflag):

    # plotflag is a flag for plotting 
    # 0 will only create Yplot, Gplot, Rplot
    # 1,2,3 ... will be forwarded to mkplot 

    global func, X, Y, Ye, saveline, Lr, jobname, met, mnfev, scaleflag, loss, R2
    # global gcoefs
    global fnames, fvlist, funcs, fkeys, gflist, nf, colors, sstot, logplot
    global Gplot, Yplot, Rplot, maxYe, minYe, gotPlot 
    
    # Fitting is called for array of ones,
    # which is multiplied by gcoefs in the wrap function.
    # Now, however, variations in variables during fit will be proportionally the same.
    # Because, least_squares modifies all vars by step which is 1e-8.
    # As far as s is 1e12 and E is 1-3 it's kinda incorrect 
    #   (see thermoluminescence glow curves).

    # Bounds apply to gcoefs
    # so, l <= gcoefs <= u
    # x values are ones*gcoefs
    #  l*ones < ones*gcoefs < u*ones
    #  l/gcoefs < ones < u/gcoefs
    
    if mnfev == 0:
        if len(guess) < 25:
            mnfev = 2500
        else:
            mnfev = 100*len(guess)
    
    fitargs = {"jac":jacobian, "tr_solver":"lsmr", "method":input_method,
               "max_nfev":mnfev, "loss":loss, "verbose":ls_verbosity, 
               "diff_step":input_diff_step}
    
    if bounds != None:
        
        fitargs["bounds"] = bounds
        
    
    if scaleflag == True:
        fitargs["x_scale"] = fsc(guess)

    
    res = lsq(wrap, guess, kwargs={"task":0}, **fitargs)
   
    
    rlarr = []
    
    # Raluclate RMS in parameters:
    # - assume guess as 100% 
    # - delta_guess are relative changes in guess
    delta_guess = (res.x-guess)/guess
    
    # RMS of delta_guess 
    rms_guess_perc = 100 * np.average(delta_guess*delta_guess)**0.5 

    # res.fun is residual at solution
    
    # Calculate R2:
    if normalize_residual:
        unnormed_residual =  wrap(res.x, task=1)-Ye
        ssres = np.sum((unnormed_residual).dot(unnormed_residual))
    else:
        ssres = np.sum((res.fun).dot(res.fun))
    
    R2 = 1.0 - ssres/sstot 
    
    rsp = gsplit(res.x)
    
    for i in range(0, nf):
        rlarr.append(fkeys[funcs.index(gflist[i])])
        for x in rsp[i]:
            rlarr.append(digform(x))
        rlarr.append('  ')
            
    rline = ' '.join(rlarr)
    print(rline, "    R2:", R2, "RMSG%:", '%.4f' % rms_guess_perc, "nfev:", res.nfev, "Success:", res.success, end='')
    if res.success==False:
        print(res.message)
    else:
        print("")

    try:
        if gflist[-1] == p2:

            # assume p2: c + bx +ax2
            p2a = float(res.x[-1])
            p2b = float(res.x[-2])
            #c = float(sys.argv[-3])

            # dp2/dx = b + 2ax 
            # b + 2ax = 0
            # x = -b / (2a) 
            p2m = -p2b *0.5 /p2a
            if xo in gflist:
                # x_min = p2m
                # but, x = true_x-xo
                # x_min = true_min - xo
                # true_min = x_min + xo
                p2m += res.x[0]
            
            print("p2 minimum at:", digform(p2m )) 


        elif gflist[-1] == p3:
            # assume p3
            p3a = float(res.x[-1])
            p3b = float(res.x[-2])
            p3c = float(res.x[-3])
            #u = float(sys.argv[-4])
    
            # dp3/dx = c + 2bx + 3cx^2 

            p3a*=3
            p3b*=2
    
            p3d=p3b*p3b-4*p3a*p3c

            p3m1 = (-p3b+p3d**0.5) / (p3a*2)
            p3m2 = (-p3b-p3d**0.5) / (p3a*2)

            if xo in gflist:
            #if p3d <0:
            #    d = complex(d)
                p3m1 += res.x[0]
                p3m2 += res.x[0]

            print("p3 minima at:", digform( p3m1) , digform( p3m2))

        elif gflist[-1] == lj: 
            print("Sigma = sigma6 ^ 1/6:", digform(res.x[-1]**0.166666666667))

    except Exception as e:
        pass

    # Plot results:

    if plotflag in [1,2,3]:    
        
        Yplot = wrap(res.x, task=1)
        Gplot = wrap(guess, task=1)
        Rplot = res.fun

        if logplot:
            global logYe
            pYe    = logYe
            pYplot = np.log10(Yplot+1e-15)
            pGplot = np.log10(Gplot+1e-15)
            pRplot = Rplot 
            ymin = np.amin(pYplot)
            
        else:
            pYe = Ye
            pYplot = Yplot
            pGplot = Gplot
            pRplot = Rplot
            ymin = min([np.amin(pYplot), minYe])
        
        gotPlot = True 

        ymax = maxYe 
        
        
        # Apparently, pyplot has a tendency to hang on large numbers, so:
        ymax1 = ymax + abs(ymax)*10
        ymin1 = ymin - abs(ymin)*10
        
        
        pGplot[ pGplot > ymax1] = ymax1
        pGplot[ pGplot < ymin1] = ymin1

        
        mkplot( [pYe, pYplot, pGplot, pRplot], [0,1,2,3], 
        ''.join([rline, "  R2: ", '%.5f' % R2]), plotflag, ylim=[ymin, ymax] )
    else:
        gotPlot = False 
        
    return rline 
    
# ===========================================================================
# ======================================== Function to convert test guess
# ========================================  into single array of floats guess
# ===========================================================================

def makeguess(gline):

        global nf, fkeys, funcs, fvlen, gflist, fnames
        
        guess = []
        
        if type(gline) is str:
            rsp = gline.split()
        elif type(gline) is list:
            rsp = gline[:]
                
        # Split guess by functions
        # and move x0, y0 to beginning
    
        gok = True
    
        nf = 0
        gflist = []
        
        gcount = []

    
        for g in rsp:
            if g in fkeys:
                f = funcs[fkeys.index(g)]
        
                gflist.append(f)
                nf +=1
                
                gcount.append(0)
                
            else:
                try:
                    
                    guess.append(float(g))
                    gcount[-1]+=1
                except Exception as e:
                    
                    print("Error in guess: this value is neither func nor float:", g)
                
                    return None
                
        # Check if guess conponents length corresponds correctly to the functions
        
        for i in range(0, nf):
            if gcount[i]!=fvlen[gflist[i]]:
                gok = False 
                j = gflist[i]
                print("")
                print("Guess error: incorrect number of variables -", gcount[i], end='')
                print("- for function", i, fkeys[funcs.index(j)], '"'+fnames[j]+'".')
                print("Must be", fvlen[j], ",   e.g.",  end='')
                print(fkeys[funcs.index(j)], fvlist[j].replace(',', ''))
                
        if not gok:
            return None 
            
        try:
            xoi = gflist.index(xo)
        except ValueError:
            xoi = None
        
        try:
            yoi = gflist.index(yo)
        except ValueError:
            yoi = None
        
        if not (xoi, yoi) in [(None, None), (0, None), (None, 0), (0,1)]:
            gok = False
            print("Error in guess:")
            print(" - xo, if present, must be the first function; its position is:", xoi+1)
            print(" - yo, if present, must be either first function, or go after xo;")
            print("   yo postion is:", yoi+1)
    
        if not gok:
            print('Guess was not ok')
            return None
        else:
            return guess

def savefile(sline):

    global Xe, Ye, Yplot, Lr, jobname, nf, gflist, gotPlot, R2 
    if not generator:
        global Rplot
            
    #Xe, Ye are global
    # if saveline is set, the variables were set during last plot 
          
    outn = ''.join([jobname, ".", datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S"), ".txt"])

    outf = open(outn, "w")
    if generator:
        outf.write(''.join(["# Generated curve, xmin = ", str(Xe[0]), 
                            ", xmax = ", str(Xe[-1]), 
                            ", step = ", str(Xe[1]-Xe[0]), '.  \n']))
        outf.write(''.join(["# Guess line: ", sline, '\n']))
        outf.write('# \n')
        
        outf.write(''.join(["# "] + [w.center(15) for w in ("X", "Y")]+['\n']))

        for i in Lr:
            outf.write(''.join([('%.5e' % w).rjust(15) for w in (Xe[i], Yplot[i]) ]+['\n']))
        outf.write(' \n')
    else:
        
        outf.write("# %s \n" % ' '.join(sys.argv) )
        outf.write(''.join(["# Fitting results of data from ", sys.argv[1], '\n']))
        outf.write(''.join(["# Final guess line: ", sline, '\n']))
        outf.write(''.join(["# Coefficient of determination, R^2= ", str(R2), '\n']))
        outf.write("# Function details: \n")
    
        guess = makeguess(sline)
                                        
        slsgs = gsplit(guess)
    
        # now, global nf and gflist contain guess from saveline
    
    
        for i in range(0, nf):
                
            fk = fkeys[funcs.index(gflist[i])]
            fa = fvlist[gflist[i]]
            
            outf.write(''.join(["# Function ", fk, ", arguments: "] + [w.rjust(22) for w in fa.split(", ")] + ['\n']))
            outf.write(''.join(["# Values:".ljust(22+len(fk))] + [str(w).rjust(22) for w in slsgs[i]] + ['\n']))
                                        
        outf.write('#  \n')
                
        outf.write(''.join(["# "] + [w.center(15) for w in ("X", "Y", "Fitted Y", "Residual")]+['\n']))
        
        if not gotPlot:
            Yplot = wrap( makeguess(sline), task=1)
            Rplot = Yplot-Ye  

        for i in Lr:
            outf.write(''.join([('%.5e' % w).rjust(15) for w in (Xe[i], Ye[i], Yplot[i], Rplot[i]) ]+['\n']))
                
        outf.write(' \n')
    
    outf.close()
    
    return outn
    
# ================================================================
# ======================================================= MAIN ===
# ================================================================

# global list of funcs at particular guess step
gflist = []

# number of fuctions, it will be modified in the guess section
nf = 0
 

# ================================================================
# =============================================== OPTION PARSER ==
# ================================================================


# -------------------------------------------------- help --------
hlp = [ "Use as: shellfit file --option value", 
        "The file must be a multy-column white-space separated data.",
        "",
        "Type shellfit -h or shellfit --help for help.",
        "Type shellfit -hf or shellfit --funcs fot function details.",
        "",
        "General options:",
        "  --help,   -h  Print help and exit.",
        "  --funcs,  -hf  List available functions and exit.",
        "  --plot,   -p  If set, plot graph after fit completion.",
        "                Default: False, i.e no plotting.",
        "  --image,  -i  Save image of fit result.",
        "  --Plot,   -P  Only plot curves, without fitting; with -g also plots guess.",
        "  --Image,  -I  Only save image, without fitting; with -g also plots guess.",
        "  --lgplot, -L  Logarithmic scale for functions and guess plots.",
        "",
        "Input data options:",
        "  --norm,   -n  Normalize input Y to [1,0], default - false.",
        "  --skip,   -k  Number of points to skip after reading one.",
        "                Default is 0, i.e. no skipping ",
        "  --xmax,   -u  Upper bound (x <= xmax) of x axis.",
        "  --xmin,   -l  Lower bound (x >= xmin) of x axis.",
        "                * l/u can be a number, e.g. 123,",
        "                  the limit will be in the units of x, l <= x <= u;",
        "                * l/u can be a number ended with p, e.q. 123p,",
        "                  such input will discard l points from the beginnig ",
        "                  and/or u points from the end of the original data file.",
        "                The -k skip will be applied after the crop of the data sequence. ",
        "",          
        "  --fxmax, -fu  Upper bound of a full resolution region, works with --skip only.",
        "  --fxmin, -fl  Lower bound of a full resolution region, works with --skip only.",
        "                This options define region where there is no skipping.",  
        "  --x0,    -x0  Set first value of x axis, e.g. -x0 0. ",
        "  --xmult, -xm  Multiply x values by a constant.",
        "  --xcol   -xc  Number of column for x data.",
        "  --ycol   -yc  Number of column for y data.",
        "",
        "Formatting options:",
        "  --digits, -d  Set the displayed significant digits, default: 6",
        "  --float32, -32  Use float32 for data arrays.",
        "",
        "Fitting algorithm options:",
        "  --verbose, -v Verbosity level of least_squares, 0,1,2. Default 0. ",
        "  --maxstp, -m  Maximum number of function evaluations.",
        "  --scale,  -c  If specified, use scale (see scipy.oprimize.lease_squares manual).",
        "  --step,   -s  Step size for the finite difference approximation of the Jacobian. ",
        "                The actual step is computed as x * diff_step.",
        "  --filter, -F  Check for infs/nans, and remove them.",
        "  --jac,    -j  2- or 3-point Jacobian. Allowed values: 2, 3, 2-point, 3-point",
        "  --alg,   -a   Minimization algorithm: trf, dogbox, lm.",
        "  --rnorm  -N   Normalize residual. I.e. minimize (f_fit - f_exp)/f_exp instead of (f_fit - f_exp)",
        "                  If a float number ( 0 < norm < 1) is given after -N, only the norm fraction of the ",
        "                  normaized residual will be used,",
        "                   i.e. norm * (f_fit - f_exp)/f_exp  + (f_fit - f_exp) * (1-norm)",
        "                  Default norm is 1. ",
        "  --rcomp  -C   Compress residual. ",
        "                  If a float number ( 0 < cr < 1) is given after -C, only the cr fraction of the ",
        "                  compressed residual will be used, i.e. cr * C(f_fit - f_exp)  + (f_fit - f_exp) * (1-cr)",
        "                  Default compression ratio is 1. ",
        "  --loss,  -S  Loss function, can be a name or a number:",
        "                 0  linear (default)",
        "                 1  soft_l1",  
        "                 2  huber", 
        "                 3  cauchy",
        "                 4  arctan",
        "",
        "External function modules:",
        "Main function module is ffitfuncs.py. Other modules can be added via",
        "  --external, -e  Specifies external function module (.py file)."
        "",
        "In-line mode:",
        "  --guess, -g  Activates in-line mode, a single fitting with the specified guess,",
        "                e.g. shellfit file -g f0 v0 v1 f1 v2 v3 ...",
        "                Default is False, no guess, regular (interactive, not in-line) mode.",
        "  --save,   -sv  If set, save results file in the in-line mode.",
        "                Ignored if -g is not specified.",
        "  --bounds, -b  Bounds, 2x the number of guess variables,",
        "                upper and lower bound for each var,",
        "                e.g. -b v1l, v1u, v2l, v2u .... ",
        "                inf stands for infinity, -inf for minus infinity.",
        "                Works with -g only.",
        "",
        "Generator mode:",
        "  --gen    -G  Activates generator mode, where curves are created.",
        "                No input file is read, all fitting options are ignored."]
        

lsa = len(sys.argv)


exception = None 
inputerror = False 

Bounds = None 

skip = 0 
normalize = False
xmin = None
xmax =  None

xcol = 1
ycol = 2

fxmax = None
fxmin = None 
setx0 = None
digits = 6 

inline = False
inlinesave = False  
plotres = 0 

plotonly = False
imageonly = False

scaleflag = False
input_diff_step=None
input_method = 'trf'

normalize_residual = 0

jacobian = "3-point"
ls_verbosity = 0

xminp = False
xmaxp = False


def_dtype = np.float64

logplot = False

generator = False

nfilter = False

xmult = 1

ifile = ""

lg = []

R2 = 0

# reading guess indicator
rg = False 

# reading bounds indicator
rb = False

#max steps
mnfev = 0

# loss function
loss = 'linear'
lossnames = [ 'linear', 'soft_l1', 'huber', 'cauchy', 'arctan' ]

gotPlot = False 


if lsa==1 or sys.argv[1] in ["-h", "--help"]:
    for l in hlp:
        print(l)
    exit()
    
ifile = None
    
i = 1

while i < lsa:

        s = sys.argv[i]
    
    
        if s in ["-p", "--plot"]:
            if plotres==0:
                plotres = 1 
            elif plotres == 2:
                plotres = 3
                
            i+=1
            rg = False
            rb = False
        
        elif s in ["-i", "--image"]:
            
            if plotres==0:
                plotres = 2 
            elif plotres == 1:
                plotres = 3
                
            i+=1
            rg = False
            rb = False
            
        elif s in ["-k", "--skip"]:
            skip = int(sys.argv[i+1])
            i+=2
            rg = False
            rb = False
    
        elif s in ["-u", "--xmax"]:
            
            xmax = sys.argv[i+1]

            i+=2
            rg = False
            rb = False
            
            
        elif s in ["-l", "--xmin"]:
        
            xmin = sys.argv[i+1]
                
            i+=2
            rg = False
            rb = False
            
        elif s in ["-xm", "--xmult"]:
            xmult = float(sys.argv[i+1])
            i+=2
            rg = False
            rb = False

        elif s in ["-xc", "--xcol"]:            
            xcol = int(sys.argv[i+1])
            i+=2
            rg = False
            rb = False
    
        elif s in ["-yc", "--ycol"]:
            ycol = int(sys.argv[i+1])
            i+=2
            rg = False
            rb = False
            
        elif s in ["-fu", "--fxmax"]:
            
            fxmax = sys.argv[i+1]

            i+=2
            rg = False
            rb = False
    
        elif s in ["-fl", "--fxmin"]:
        
            fxmin = sys.argv[i+1]

            i+=2
            rg = False
            rb = False
        
        elif s in ["-sv", "--save"]:
            inlinesave = True
            i+=1
            rg = False
            rb = False

        elif s in ["-g", "--guess"]:
            rb = False
            rg = True
            inline = True
            i+=1
            
        elif s in ["-m", "--maxstp"]:
            rb = False
            rg = False
            mnfev = int(sys.argv[i+1])
            i+=2
            
        elif s in ["-c", "--scale"]:
            rb = False
            rg = False
            scaleflag = True
            i+=1

        elif s in ["-s", "--step"]:
            rb = False
            rg = False
            input_diff_step = float(sys.argv[i+1])
            i+=2

        elif s in ["-j", "--jac"]:
            rb = False
            rg = False
            ijac = sys.argv[i+1]

            if ijac in [ "2-point", "3-point"]:
                jacobian = ijac
            elif ijac in ["2", "3"]:
                jacobian = ijac+"-point"
            else:
                print("Incorrect input for Jacobian:", ijac)
            i+=2

        elif s in ["-v", "--verbosity"]:
            rb = False
            rg = False
            ls_verbosity = int(sys.argv[i+1])
            if ls_verbosity> 2:
                ls_verbosity = 2
            elif ls_verbosity <0 :
                ls_verbosity = 0


            i+=2

        elif s in ["-a", "--alg"]:
            rb = False
            rg = False

            if sys.argv[i+1] in ['trf', 'dogbox', 'lm']:
                input_method = sys.argv[i+1]
            i+=2
        
        elif s in ["-N", "--rnorm", "-C", "--rcomp" ]:
            rb = False
            rg = False

            if s in ["-N", "--rnorm"]:
                normalize_residual = 1
                norm_res_fraction = 1
            else:
                normalize_residual = 2
                norm_res_fraction = 1


            try: 
                norm_res_fraction = float(sys.argv[i+1])
                if norm_res_fraction > 1:
                    norm_res_fraction = 1
                elif norm_res_fraction < 0:
                    norm_res_fraction = 0
                    normalize_residual = 0


                i+=2
            except Exception:
                # assume -N without argument 
                norm_res_fraction = 1
                
                i+=1

            
        elif s in ["-S", "--loss"]:
            rb = False
            rg = False
            
            losserr = True 
            try: 
                # try integer
                loss = lossnames[int(sys.argv[i+1])]
                losserr = False 
                
            except Exception:
                # assume name
                if sys.argv[i+1] in lossnames:
                    loss = sys.argv[i+1] 
                    losserr = False 
            if losserr:
                print("Loss function not recognized:", sys.argv[i+1]) 
            else:
                print("Using loss function:", loss )
            
            i+=2
            
        elif s in ["-F", "--filter"]:
            rb = False
            rg = False
            nfilter = True
            i+=1
            
        elif s in ["-n", "--norm"]:
            rb = False
            rg = False
            normalize = True
            i+=1
            
        elif s in ["-b", "--bounds"]:
            rg = False
            rb = True
            inline = True
            
            Bounds = ([], [])
            i+=1
        
            
        elif s in ["-P", "--Plot"]:
            if plotres==0:
                plotres = 1 
            elif plotres == 2:
                plotres = 3
            
            plotonly = True
                
            i+=1
            rg = False
            rb = False
            
        elif s in ["-I", "--Image"]:
            if plotres==0:
                plotres = 2 
            elif plotres == 1:
                plotres = 3
            
            imageonly = True
                
            i+=1
            rg = False
            rb = False
        
        elif s in ["-L", "--lgplot"]:
            logplot = True
            i+=1
            rg = False
            rb = False
        
        elif s in ["-x0", "--x0"]:
            setx0 = float(sys.argv[i+1]) 
            i+=2
            rg = False
            rb = False
        
        elif s in ["-d", "--digits"]:
            digits = int(sys.argv[i+1]) 
            i+=2
            rg = False
            rb = False

        elif s in ["--float32", '-32']:
            def_dtype = np.float32
            i+=1
            rg = False
            rb = False

        elif s in ["--float128", '-128']:
            def_dtype = np.float128
            i+=1
            rg = False
            rb = False
            
        elif rg:
            lg.append(sys.argv[i])
            i+=1
            
        elif rb:
            Bounds[0].append(float(sys.argv[i]))
            Bounds[1].append(float(sys.argv[i+1]))
            i+=2 

        elif s in ["-hf", "--funcs"]:
            print("Available functions:")
            for j in range(0, len(funcs)):
                f = funcs[j]
                print("Key:", fkeys[j], "; variables:", fvlist[f])
                print("Type:", fnames[f])
                print("Formula", fform[f])
                print("Usage in guess:", fkeys[j], fvlist[f].replace(',', ''))
                print("")
            i+=1
            sys.exit()
        
        elif s in ["-G", "--gen"]:
            generator = True
            rg = False
            rb = False
            i+=1
        
        elif s in ["-h", "--help"]:
            for l in hlp:
                print(l)
            sys.exit()

        elif os.path.isfile(s):
            # Assume file
            ifile = s
            i+=1

     
        else:
            
            print("Incorrect input:", s)
            print("")
            
            exit()


if ifile == None and not generator:
    print("Error: input file not specified or not found. Exiting.") 
    exit()

    
if lg:
    
    Guess = makeguess(lg)
    
    if Guess == None:
        print("Error in guess. Exiting.")
        exit()
            
if not generator:
    
    #job name
    ifspl=ifile.split('.')
    if len(ifspl)>1:
        jobname = '.'.join(ifile.split('.')[:-1])
    else:
        jobname = ifile 

    # read input file into raw data arrays
    Xe, Ye = readfile(ifile, xmin, xmax, fxmin, fxmax, skip, setx0, xcol, ycol)
    
    if xmult != 1:
        Xe*=xmult
    
    if logplot:
        logYe = np.log10(Ye+1e-15)
        minYe = np.amin(logYe)
        maxYe = np.amax(logYe)
    else:
        minYe = np.amin(Ye)
        maxYe = np.amax(Ye)


    # calculate Ye mean, Ye-Yem and sum of squares of Ye-Yem
    Yem = np.average(Ye)
    YeYem = Ye - Yem
    sstot = np.sum(YeYem.dot(YeYem))

else:
    
    jobname = "ffit_gen"
    print("Welcome to generator mode!")
    print("Create x axis by providing min, max and step values:")
    
    exitLoop = False
    
    while not exitLoop:
        lsp = input().split()
        rl.remove_history_item(rl.get_current_history_length()-1)
        
        if not lsp:
            print("You have to enter something.")
            
        elif len(lsp) == 3:
            try:
                Xe = np.arange(*map(float, lsp))
                print("Created x axis.")
                exitLoop = True
                Ye = np.zeros_like(Xe)
            except Exception as e:
                print("Your input caused an exception:", e)
                print("")
        elif len(lsp)!=3:
            print("There must be three values.")

# range from 0 to len(Xe)
L = len(Xe)
Lr = range(0, L)

#X += Xe

# ================================================================
# ========================================== Stuff happens here ==
# ================================================================

if plotonly or imageonly:

    pl = [Ye]
    ps = [0]
    
    if lg:
        pl.append(wrap(Guess, task=1))
        ps.append(2)
        
    mkplot(pl, ps, "", plotres)
    
    sys.exit()
        
        
# in case of in-line mode:
if inline:

    if generator:
        print("Generator mode.")
        if plotres != 0 or inlinesave:
            Yplot = wrap(Guess, task=1)
            resline = ' '.join(Guess)
            
        if plotres != 0:
            mkplot( [Yplot] , [1], resline, 1)  
        
    else:
        print(ifile, end='  ')
        
        resline = dothefit(Guess, Bounds, plotres)
        
    if inlinesave:
                
                
        savefile(resline)
        
    exit()
    
#else - if not inline - program will continue
    
# Read guess history:
# ifile-corresponding history file
histfn = jobname+'.history'

print(ifile, jobname)
print

# Try importing history
try:
    
    try:
        rl.read_history_file(histfn)
        print("History imported via readline.read_history_file.")
        
    except Exception as e:
    
        hfile = open(histfn, 'r')
    
        # lets put every line from file to history
        for line in hfile:
            rl.add_history(line.rstrip('\r\n'))
        hfile.close()
        
        print("History imported in a line-by-line read.")
    
    
# In case something went wrong:
except Exception as e:
    
    print("Histroy IOError:", e) 

# Now, history of previous guesses (if any) is in history buffer.

do_exit = False

saveline = ""

if plotres in [0,1] and not generator:
    print("Plotting preview...")
    mkplot([Ye], [0], "Raw data preview plot", plotres)


while not do_exit:
    
    print('')
    print('Enter guess:')
    rinp=input()
    
    # Importing readline affects input behaviour:
    # all inputs are automatically saved to the history buffer.
        
    if rinp in ['h', 'H', '-h', '--help', 'help', 'HELP', 'WTF', 'wtf']:
        print("Guess goes as func_name p0 p1 p2 func_name p0 p1 p2 ... times N functions.")
        print("  e.g. d1 x01 y01 A1 t1 d1 x02 y02  n2 E2 ...")
        print("Ask for help again for list of functions and parameters, or enter guess:")
            
        rinp=input()
        if rinp in ['h', 'H', '-h', '--help', 'help', 'HELP', 'WTF', 'wtf']:
            for i in range(0, len(funcs)):
                f = funcs[i]
                print("Key:", fkeys[i], "; variables:", fvlist[f], "; type:", fnames[f])
                print("Usage in guess:", fkeys[i], fvlist[f].replace(',', ''))
                print("")
            
            # the while cycle will return to beginning here
     
    elif rinp == "s" or rinp == "S":
        #erase this e from history:
        rl.remove_history_item(rl.get_current_history_length()-1)
        
        if saveline == "":
            print("Nothing was done so far, or the last result was already saved, nothing to save.")
        
        else:
     
            savefn = savefile(saveline)
            
            print("Results saved:", saveline)
            print("File name is:", savefn)
            
            saveline=""
            
        # the while cycle will return to beginning here
    
    elif rinp == "e" or rinp == "E":
        
        #erase this e from history:
        rl.remove_history_item(rl.get_current_history_length()-1)
        
        break
    
    else:

        rsplit = rinp.split()
        if rsplit and rsplit[-1]=="p":
            Guess = makeguess(rsplit[:-1])
            plotGuess = True 
        else:
            Guess = makeguess(rsplit)
            plotGuess = False 
            
        if Guess:
            # call for fitting
            
            if plotGuess:
                #do plotting
                
                mkplot( [wrap(Guess, task=1), Ye] , [2,1], "Guess", 1)
                
            else:
        
                if generator:
                    Yplot = wrap(Guess, task=1)
                    resline = rinp
                    saveline = resline
                    if plotres!=0:
                        mkplot( [Yplot] , [1], resline, 1)    
                    
                                    
                    
                else:
                    resline = dothefit(Guess, Bounds, plotres)
        
                    saveline = resline
            
                rl.add_history(resline)
    
        else:
            pass



# ================================================================
# ================================================ On exit: ======
# ================================================================


hfile = open(histfn, 'w')

for i in range(1, rl.get_current_history_length()+1):
    hfile.write(rl.get_history_item(i)+'\n')
    
hfile.close()

print()
exit()
    
