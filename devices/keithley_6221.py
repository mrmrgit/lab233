from .dev_addrs import TCPIP_KEITHLEY_6221, GPIB_KEITHLEY_6221
from visa import Instrument, VisaIOError
#ak chceme zmenit komunikacny interface(GPIB,LAN), treba ho inicializovat na pristroji:
#tlacitko COMM a v menu zvolit interface
'''
import keithley_6221                #DO NOT: " from keithley_6221 import * " !!!
ky = keithley_6221.init_device()    #initialization
ky.ask('syste:err?')                #visa.Instrument method
ky.output_on()                      #user's defined method
ky.close()
'''
def init_device(**kwargs):
    try:
        cs = Keithley_6221(TCPIP_KEITHLEY_6221, **kwargs) 
        cs.term_chars='\n'                             
    except VisaIOError:
        cs = Keithley_6221(GPIB_KEITHLEY_6221, **kwargs)
    return cs

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Keithley_6221(Instrument):
    def get_errs(self): 
        ret='current source errors: '
        err = self.ask('syst:err?')
        ret+=err
        it=0
        while not err=='0,"No error"':
            ret+=err
            err = self.ask('syst:err?')
            it+=1
            if it==100: break
        return ret
    
    def set_for_meas(self, compl, cur_range):
        self.clear()
        self.set_volt_comp(compl)
        self.auto_range_off()
        self.set_curr_range(cur_range)
        self.output_on()
        
    def set_for_magnet(self, cur):
        self.clear()
        self.reset()
        self.auto_range_on()
        #self.set_range(1e-5)
        self.output_on()
        self.set_current(cur)

    def set_for_switch(self):
        self.write('*rst')
        self.write('*cls')
        self.write('curr:comp 60.0')
        self.write('sour:wave:func squ')
        self.write('sour:wave:freq 50')
        self.write('sour:wave:ampl 80e-3')
        self.write('sour:wave:offs 0e-3')
        self.write('sour:wave:dcycle 100')
        self.write('sour:wave:pmar:stat off')
        self.write('sour:wave:dur:time 2e-2')
        self.write('sour:wave:arm')
        self.write('sour:wave:init')
        print(self.get_errs())
        self.write('sour:wave:init')
        print(self.get_errs())
        
#Here you can add new methods
