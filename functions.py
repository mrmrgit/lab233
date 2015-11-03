from scipy.optimize import leastsq
from scipy import stats
import numpy as np

def lorentz(p,x):
    #power in log
    return 10**(p[3]/10)*p[1]**2/((2*p[2]*(x-p[1]))**2+(p[1])**2)+10**(p[0]/10)
    
def fit_lorentz(x,y,p0):
    p0[0]=-100
    fitfunc = lambda p, x: 10**(p[3]/10)*p[1]**2/((2*p[2]*(x-p[1]))**2+(p[1])**2)+10**(p[0]/10) # Target function
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    y=10**(y/10)

    p1, success = leastsq(errfunc, p0[:], args=(x, y))
    chi=stats.chisquare(y,fitfunc(p1, x))
    
    return p1,chi

def find_fit_region(startf,stopf,cf,nop,fratio):
    center_poin=int((cf-startf)/(stopf-startf)*nop)
    startp,stopp=center_poin-nop*fratio/2,center_poin+nop*fratio/2
    if startp<0:
        startp=0
    if stopp>nop:
        stopp=nop
    return startp,stopp

def find_bw(p_ref,bw_ref,p):
    bw_v=[1,2,3,5,7,10,15,20,30,50,70,100,150,200,300,500,700,1e3,1.5e3,2e3,3e3,5e3,7e3,10e3,15e3,20e3,30e3]
    bw=bw_ref*10**((p-p_ref)/10)
    i=0
    if bw<=1:
        bw=1
    elif bw>=30e3:
        bw=30e3
    else:
        while bw>bw_v[i]:
            i=i+1
        if bw_v[i]-bw>bw-bw_v[i-1]:
            bw=bw_v[i-1]
        else:
            bw=bw_v[i]
    return bw

def adj_bw(peaks,powers):
    # adjusting IFBW 
    bw=[]
    for p in peaks:
        bwp=[]
        for pw in powers:
            bwp.append(find_bw(p[1],p[0],pw))
        bw.append(bwp)    
    return bw
