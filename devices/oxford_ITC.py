'''
Wrapper for driver for Oxford instruments Intelligent Temperature Controller
for HelioxAC-V 3He Refrigerator System.

NOTE 1: It is possible to initiate the device only one instance of the Oxford_ITC.
If you want to use the device in several scripts, use oxford_ITC_virt in each script.

NOTE 2: In some commands, even thoguh it looks like write() command is more
suitable, ask() is used, only to clean output buffer. 

---------------------------------------------------------------
Example:

import oxford_ITC
itc = oxford_ITC.init_device()      #initialization
itc.get_ptc2_temp()                 #user's defined method
itc.close()                         #visa.Instrument method
---------------------------------------------------------------

Matus Rehak
'''

from visa import SerialInstrument
from .dev_addrs import *
from time import *

def init_device(**kwargs):
    itc = Oxford_ITC(ASRL_OXFORD_ITC, **kwargs)
    itc.stop_bits = 2
    return itc

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class Instrument such as write() and read()
#and also user's methods defined here. 
class Oxford_ITC(SerialInstrument): 
    senzor = 3

    def __repr__(self):
        return '<Oxford ITC device>'
    
    def get_sample_temp(self):
        '''
        Returns temperature of the sample (3He pot).
        There are 2 temperature sensors, one that works below
        and one that works above 7K.
        '''

        try:
            resp=self.ask('@1R%i' % (self.senzor))
            temp=float(resp.replace('R',''))
            
            if temp < 7 and self.senzor != 2:
                self.senzor = 2
                sleep(0.020)
                resp = self.ask('@1R%i' % (self.senzor))
                temp = float(resp.replace('R',''))
                
            elif temp >= 7 and self.senzor != 3:
                self.senzor = 3
                sleep(0.020)
                resp = self.ask('@1R%i' % (self.senzor))
                temp = float(resp.replace('R',''))
                
        except ValueError:
            try:
                resp = self.ask('@1R%i' % (self.senzor))
                temp = float(resp.replace('R',''))
                
                if temp < 7 and self.senzor!=2:
                    self.senzor = 2
                    sleep(0.020)
                    resp=self.ask('@1R%i' % (self.senzor))
                    temp=float(resp.replace('R',''))
                    
                elif temp >= 7 and self.senzor != 3:
                    self.senzor = 3
                    sleep(0.020)
                    resp = self.ask('@1R%i' % (self.senzor))
                    temp = float(resp.replace('R',''))
                    
            except ValueError:
                temp = -1            
            
        return temp

    def turn_hsw_on(self):
        '''
        Turns heat-switch ON, which means heating it to 25K.
        Heat-switch is not ON immmediately, you have to wait
        some time until it is heated to 25K.
        '''
        _ = self.ask('@2C3')
        _ = self.ask('@2T25')
        _ = self.ask('@2A1')
        
    def turn_hsw_off(self):
        '''
        Turns heat-switch OFF, which means cooling it below 7K.
        Heat-switch is not OFF immediately, you have to wait to
        cool down.
        '''
        _ = self.ask('@2C3')
        _ = self.ask('@2T00')
        _ = self.ask('@2A1')
        
    def set_sorb_temp(self,temp):
        ''' 
        Sets heating of sorbtion pump to selected temperature.
        Temperature may overshoot during heating, be careful!
        '''
        _ = self.ask('@1C3')
        _ = self.ask('@1T%s'%temp)
        _ = self.ask('@1A1')
                
    def get_ptc2_temp(self):
        '''
        Returns temperature of PTC2 which is cooled by cryopump.
        '''
        try:
            resp = self.ask('@2R2')    
            temp = float(resp.replace('R',''))

        except ValueError:
            try:
                resp = self.ask('@2R2')    
                temp= float(resp.replace('R',''))
            except ValueError:
                temp = -1
                
        return temp
        
    def get_hsw_temp(self):
        '''
        Returns temperature of heat-switch.
        '''
        try:
            resp = self.ask('@2R1')    
            temp = float(resp.replace('R',''))
        except ValueError:
            try:
                resp = self.ask('@2R1')
                temp = float(resp.replace('R',''))
            except ValueError:
                temp = -1
                
        return temp

    def get_sorb_temp(self):
        '''
        Returns temperature of sorbtion pump.
        '''
        try:
            resp = self.ask('@1R1')    
            temp = float(resp.replace('R',''))
        except ValueError:
            try:
                resp = self.ask('@1R1')
                temp = float(resp.replace('R',''))
            except ValueError:
                temp = -1
                
        return temp

       
#Here you can add new methods
