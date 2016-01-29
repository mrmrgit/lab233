'''
Device which consists of source (Agilent E3648A), multimeter (HP 34401A),
home-made current source with +/-12 V voltage reference (TESLA BK126),
electromagnet and Hall sensor.

example program:
from lab233.devices import magnet
mg = magnet.MAG()
mg.reset()
mg.set_current(50e-3)
b=mg.get_field()
print b
mg.set_current(0)
mg.close(outp='OFF')

power source (Agilent E3648A) and multimeter (HP 34401A) can be individually
controlled e.g.:

from lab233.devices import magnet
mg = magnet.Mag()
mg.reset()
print mg.ps.ask('syst:err?')
print mg.multi.ask('syst:err?')
mg.close(outp='OFF')

Calibration date: Wed Jul 30 16:39:55 2014

Last update: 29.1.2016
'''

import visa
from .dev_addrs import *
from time import sleep
        
def calib(volt):
    '''
    calculates magnetic field (in mT) from voltage
    '''
    return  -13.5851268865 + 11765.5761598*volt

class Mag():
    def __init__(self):
        self.ps=visa.instrument(GPIB_AGILENT_E3648A)
        self.multi = visa.instrument(GPIB_HP_33401A)

    def __repr__(self):
        return '<lab233 electomagnet>'
                
    def reset(self):
        curr = float(self.ps.ask('MEAS:CURR:DC?'))
        if (self.ps.ask('outp?')=='1') and (curr>0.001):
            curr = float(self.ps.ask('CURR?'))
            for _ in range(int(round(curr*1e4))):
                self.ps.write('CURR down')
                sleep(0.001)
        
        self.ps.write('*rst')
        self.ps.write('*cls')
        self.multi.write('*rst')
        self.multi.write('*cls')
        self.ps.write('curr:step 1e-4')
        self.ps.write('CURR 0.0')
        self.ps.write('VOLT 20.0')
        self.ps.write('OUTP ON')            
    
    def get_current(self):
        curr = float(self.ps.ask('MEAS:CURR:DC?'))
        relay = 2*float(self.ps.ask('outp:rel?'))-1 #relay +1 or -1
        return relay*curr

    def get_voltage(self):
        return float(self.multi.ask('MEAS:VOLT:DC?'))

    def get_field(self):
        volt = float(self.multi.ask('MEAS:VOLT:DC?'))
        return calib(volt)

    def get_status(self):
        return self.ps.ask('outp?')

    def set_status(self,stat):
        self.ps.write('outp '+stat)

    def set_range(self,rng='high'):
        if rng =='high':
            self.ps.write('volt:rang P20V')
        elif rng == 'low':
            self.ps.write('volt:rang P8V')
        else:
            print 'range not changed, '+self.ps.ask('volt:rang?')
            
    def set_current(self,curr,slp=0.0):
        '''
        sets current in 0.1mA-step sweeps with 0.1mA precision
        '''
        #getting values and settings
        curr=float(round(curr,4))
        curr_abs0=float(self.ps.ask('CURR?'))       #set current, not flowing current
        relay0 = 2*float(self.ps.ask('outp:rel?'))-1#relay +1 or -1
        curr0 = relay0*curr_abs0
        #setting current
        if curr*curr0>=0:
            if relay0*curr<0:
                self.ps.write('outp:rel '+str((1-relay0)/2)) #change relay state
                print 'CLICK'####### VYMAZ
            if abs(curr)>abs(curr0):
                for _ in range(int(round(abs(curr0-curr)*1e4))):
                    self.ps.write('CURR up')
                    sleep(slp)
                    if _==200: print self.get_field()####### VYMAZ
            elif abs(curr)<abs(curr0):
                if curr==0:  #problem with step 1e-4 -> 0.0, it has to be done like this
                    for _ in range(int(round(abs(curr0)*1e4))-2):
                        self.ps.write('CURR down')
                        sleep(slp)
                        if _==200: print self.get_field()######### VYMAZ
                    self.ps.write('curr 0')
                else:
                    for _ in range(int(round(abs(curr0-curr)*1e4))):
                        self.ps.write('CURR down')
                        sleep(slp)
                        if _==200: print self.get_field()########## VYMAZ
        else:
            for _ in range(int(round(curr_abs0*1e4))-2):#problem with step 1e-4 -> 0.0, it has to be done like this
                self.ps.write('CURR down')
                sleep(slp)
                if _==200: print self.get_field()########## VYMAZ
            self.ps.write('curr 0')
            self.ps.write('outp:rel '+str((1-relay0)/2)) #change relay state
            print 'CLICK'####### VYMAZ
            for _ in range(int(round(abs(curr*1e4)))):
                self.ps.write('CURR up')
                sleep(slp)
                if _==200: print self.get_field()########## VYMAZ
        
        #checking if the field is stabilized:
        flds=list()
        for _ in range(5): flds.append(self.get_field())

        while (max(flds)-min(flds))>0.015:
            flds.pop(0)
            flds.append(self.get_field())
            sleep(0.01)
                    
    def set_field(self,fld):
        '''
        NOT IMPLEMENTED
        '''
        pass

    def get_errs(self):#test
        ret='Power source errors: '
        err = self.ps.ask('syst:err?')
        ret+=err
        it=0
        while not err=='+0,"No error"':
            ret+=err
            err = self.ps.ask('syst:err?')
            it+=0
            if it==100: break
            
        ret+='\tMultimeter errors: '
        err = self.multi.ask('syst:err?')
        ret+=err
        it=0
        while not err=='+0,"No error"':
            ret+=err
            err = self.multi.ask('syst:err?')
            it+=0
            if it==100: break
        return ret
    
    def close(self,outp='ON'):
        self.ps.write('outp '+outp)
        self.ps.close()
        self.multi.close()



