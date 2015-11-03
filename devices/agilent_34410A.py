from .dev_addrs import *
from visa import Instrument, VisaIOError

def init_device(**kwargs):
    multi = Agilent_34410A(gpib_agilent33401A, **kwargs)
    return multi

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Agilent_34410A(Instrument):
    def clear(self):
        self.write('*cls')

    def reset(self):
        self.write('*rst')

    def get_voltage(self):
        volt=self.ask('MEAS:VOLT:DC?')
        return float(volt)

    def get_errs(self):
        ret='multimeter errors: '
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
