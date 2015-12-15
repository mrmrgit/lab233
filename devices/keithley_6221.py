from .dev_addrs import *
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
    def clear(self):
        self.write('SOUR:CLEar')

    def cls(self):
        self.write('*CLS')

    def rst(self):
        self.write('*RST')

    def reset(self):
        self.write('*RST')    

    def output_on(self):
        self.write('OUTP:STAT ON')

    def output_off(self):
        self.write('OUTP:STAT OFF')    

    def auto_range_on(self):
        self.write('SOUR:CURR:RANG:AUTO ON')

    def set_range(self,crange):
        self.write('SOUR:CURR:RANG %e'%crange)

    def get_range(self):
        return self.ask('SOUR:CURR:RANG?')

    def auto_range_off(self):
        self.write('SOUR:CURR:RANG:AUTO OFF')    

    def set_current(self,current):
        self.write('SOUR:CURR %e' %current)

    def get_current(self):
        return self.ask('SOUR:CURR?')

    def set_pulse(self):
        
        self.write('SOUR:WAVE:FUNC SQU')
        self.write('SOUR:WAVE:FREQ 50')
        self.write('SOUR:WAVE:AMPL 80e-3')
        self.write('SOUR:WAVE:OFFS 0e-3')
        self.write('SOUR:WAVE:DCYCle 100')
        self.write('SOUR:WAVE:PMAR:STAT OFF')
        self.write('SOUR:WAVE:DUR:TIME 2e-2')
        self.write('SOUR:WAVE:ARM')
        print self.ask('STAT:QUE?')
        

    def trigger(self):
        self.write('SOUR:WAVE:INIT')

    def abortWave(self):
        self.write('SOUR:WAVE:ABOR')

    def readError(self):
       self.ask('STAT:QUE?')

    def set_compl(self,v):
        self.write('CURR:COMP %e'%v)
        
    def set_curr_range(self,crange):
        self.write('SOUR:CURR:RANG %e'%crange)

    def set_volt_comp(self,comp):
        return self.write('CURR:COMP %e'%comp)

    def read_error(self):
        error=self.ask("STAT:QUE:NEXT?")
        #self.write("STAT:CLE")    
        return error

    def preset(self):
        return self.write('STAT:PRESet')

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
    
    def set_for_meas(self,compl,cur_range):
        self.clear()
        self.set_volt_comp(compl)
        self.auto_range_off()
        self.set_curr_range(cur_range)
        self.output_on()
        
    def set_for_magnet(self,cur):
        self.clear()
        self.reset()
        self.auto_range_on()
        #self.set_range(1e-5)
        self.output_on()
        self.set_current(cur)
#Here you can add new methods
