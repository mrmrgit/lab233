from .dev_addrs import TCPIP_AGILENT_E5062A, GPIB_AGILENT_E5062A
from visa import Instrument, VisaIOError
import numpy as np
from time import sleep
'''
import agilent_N5062A       #DON'T DO: " from agilent_N5242A import * " !!!
vna = agilent_N5062A.init_device(timeout=300)
vna.ask('syste:err?')                #visa.Instrument method
vna.set_BW(1,100)                      #user's defined method
vna.close()
'''

def init_device(**kwargs):
    try:
        agi = Agilent_E5062A(TCPIP_AGILENT_E5062A, **kwargs) 
    except VisaIOError:
        agi = Agilent_E5062A(GPIB_AGILENT_E5062A, **kwargs)
    return agi

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Agilent_E5062A(Instrument):  
    def get_errs(self):
        ret='Network analyzer errors: '
        err = self.ask('syst:err?')
        ret+=err
        it=0
        while not err=='+0,"No error"':
            ret+=err
            err = self.ask('syst:err?')
            it+=1
            if it==100: break
        return ret

    def set_transM_meas(self, power, f1, f2, nf, ifbw, avg):
        self.write('*cls')          
        self.write('*rst')

        self.write('syst:pres')
        self.write('sour:pow %f' %power)
        self.write('calc:par:coun 1')
        self.write('calc:par:def S21')
        self.write('disp:wind:act')
        self.write('calc:form plog')
        self.write('trig:sour bus')
        self.write('init:cont on')
        self.write('trig:sing;*wai')
        sleep(0.2)
      
        self.write('sens:freq:star %f' %f1)
        self.write('sens:freq:stop %f' %f2)
        self.write('sens:swe:poin %i' %nf)    
        self.write('sens:band %f' %ifbw)
        self.write('sens:aver on')
        self.write('sens:aver:coun %i' %avg)

    def run_transM_meas(self, avg):
        self.write('sens:aver:cle')
        self.write('outp on')
        self.write('init:cont on')
        self.write(self.trigger_repeat(avg))
        self.ask('*opc?') #operation complete?
        self.write('outp off')
        dr = self.ask('calc:data:fdat?')
        
        d=map(float,dr.split(','))
        amp=np.array([d[j] for j in range (0,len(d),2)])
        pha=np.array([d[j] for j in range (1,len(d),2)])
        
        return amp, pha

    def trigger_repeat(self, N):
        ret=''
        for _ in range(N): ret+=':trig:sing;*wai;'
        return ret        

    def prelocate(self, peak, region, span):
        from ..peak_lorentz_fit import find_fit_region, fit_lorentz
        
        amp, phs = self.run_transM_meas(peak[5])
        peak_params = self.get_peak_params()

        f = np.linspace(peak[2], peak[3], peak[4])
        fit_params0 = [
            10**(peak_params[3]/10.),
            peak_params[0],
            peak_params[1],
            10**(-10)
            ]      #[loss(lin.), half-bandwidth, center_freq, offs(lin.)]        

        startp, stopp = find_fit_region(
            peak[2], peak[3], peak[4], peak_params[1], region)#fiting region
        
        fit_params, chi = fit_lorentz(
            f[startp:stopp],
            10**(amp[startp:stopp]/10.),
            fit_params0,
            chi_out=True)#fiting

        self.autoadjust_freq(peak, fit_params, span)
        
    def autoadjust_freq(self, peak, fit_params, span):
        peak[2] = fit_params[2]*(1-span*2.*fit_params[1]/fit_params[2])
        peak[3] = fit_params[2]*(1+span*2.*fit_params[1]/fit_params[2])
        self.write('sens:freq:star %f' %peak[2])
        self.write('sens:freq:stop %f' %peak[3])
        
    def set_power_ifbw(self, power_dBm, power_dBm_ref, ifbw_ref):
        '''
        setting the IFBW according to applied power to get similar
        level of noise. IFBW is adjusted to power_ref_dBm and ifbw_ref
        '''
        ifbws = [10, 30, 100, 300, 1e3, 3e3, 10e3, 30e3]

        ifbw_calc = ifbw_ref*10**((power_dBm-power_dBm_ref)/10)

        ifbw = ifbws[-1]
        for i in ifbws:
            if ifbw_calc <= i:
                ifbw = i
                break

        self.write('sour:pow %f' %power_dBm)
        self.write('sens:band %f' %ifbw)

        return ifbw

    def get_peak_params(self):
        '''
        autoscales window with i-th measurement and returns list:
        [bandwidth, center_freq, Q, loss]
        '''
        self.write('disp:wind:trac:y:auto') #autoscale
        self.write('calc:mark1 ON')
        self.write('calc:mark1:func:type MAX')
        self.write('calc:mark1:func:exec')
        self.write('calc:mark1:bwid on')
        self.write('calc:mark1:bwid:thr -3')
        resp = self.ask('calc:mark1:bwid:data?')
        return map(float, resp.split(','))
#Here you can add new methods
