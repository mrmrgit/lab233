from .dev_addrs import *
from visa import Instrument, VisaIOError

def init_device(**kwargs):
    ps = Agilent_3648A(gpib_agilent3648A, **kwargs)
    return ps

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Agilent_3648A(Instrument):
    def clear(self):
        self.write('*cls')

    def reset(self):
        self.write('*rst')

    def set_current(self,current):
        self.write('CURR %e' %current)

    def set_voltage(self,volt):
        self.write('VOLT %e' %volt)

    def output_on(self):
        self.write('OUTP ON')

    def output_off(self):
        self.write('OUTP OFF') 

    def get_errs(self):
        ret='power source errors: '
        err = self.ask('syst:err?')
        ret+=err
        it=0
        while not err=='+0,"No error"':
            ret+=err
            err = self.ask('syst:err?')
            it+=1
            if it==100: break
        return ret
#Here you can add new methods
