import matplotlib.pyplot as plt
from scipy.optimize import leastsq
'''
Functions for fitting lorentzian peaks
'''
def lorentz_err(p,y,x):
    '''
    p0 = [A, B, xc, offs]
    Q = xc/(2*B)
    y = A/(1+((x-xc)/B)**2)+offs
    '''
    A,B,xc,offs = p
    return y-A/(1+((x-xc)/B)**2)-offs

def lorentz(p,x):
    '''
    p0 = [A, B, xc, offs]
    Q = xc/(2*B)
    y = A/(1+((x-xc)/B)**2)+offs
    '''
    A,B,xc,offs = p
    return A/(1+((x-xc)/B)**2)+offs

def fit_lorentz(x_array, y_array, p0):
    '''
    p0 = [A, B, xc, offs]
    Q = xc/(2*B)
    y = A/(1+((x-xc)/B)**2)+offs
    '''
    pfit, suc = leastsq(lorentz_err, p0, args=(y_array, x_array))
    return pfit

def plot_fit_and_data(x_array, y_array, pfit):
    plt.plot(x_array, y_array, 'or')
    plt.plot(x_array, lorentz(pfit, x_array),'b')
    plt.show()

# test
def load_dummy_data():
    import numpy as np

    p_dummy = [1, 1e8, 1.5e9, 0.001]
    
    x = np.linspace(1e9, 2e9, 100)
    y = lorentz(p_dummy, x)
    y_r = (1-0.1*np.random.random(100))*y

    p_guess = [0.8, 2e8, 1.45e9, 0]
    
    pfit = fit_lorentz(x, y_r, p_guess)

    plot_fit_and_data(x,y_r,pfit)
