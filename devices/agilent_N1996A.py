from .dev_addrs import TCPIP_AGILENT_N1996A
from visa import Instrument, VisaIOError

def init_device(**kwargs):
    multi = Agilent_N1996A(TCPIP_AGILENT_N1996A, **kwargs)
    return multi

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Agilent_N1996A(Instrument):
    def get_errs(self):
        ret='spectrum analyzer errors: '
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
