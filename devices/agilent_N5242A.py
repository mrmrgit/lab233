'''
import agilent_N5242A       #DON'T DO: " from agilent_N5242A import * " !!!
vna = agilent_N5242A.init_device(timeout=300)
vna.ask('syste:err?')                #visa.Instrument method
print(vna.get_errs())                      #user's defined method
vna.close()
'''

from .dev_addrs import TCPIP_AGILENT_N5242A, GPIB_AGILENT_N5242A
from visa import Instrument, VisaIOError
import numpy as np

def init_device(**kwargs):
    try:
        agi = Agilent_N5242A(TCPIP_AGILENT_N5242A, **kwargs) 
    except VisaIOError:
        agi = Agilent_N5242A(GPIB_AGILENT_N5242A, **kwargs)
    return agi

#Class which inherits from visa.Instrument. Doing it this way, the new instance
#will have both methods of parent class visa.Instrument such as write(), read()
#and also user's methods defined here. 
class Agilent_N5242A(Instrument):        
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

    def _check_errors(self):
        '''
        raise an error if there is an error in th device
        '''
        err = self.ask('syst:err?')
        if not err == '+0,"No error"' :
            raise RuntimeError('Agilent_N5242A:' + err)

    def set_point_meas(self, power, f, ifbw, avg, meas=1):
        if meas == 1:
            self.write('syst:fpr')
            self.write('*cls')

        self.write('disp:wind%i:stat on'%(meas))
        self.write('calc%i:par:def:ext m%i,S21' %(meas, meas))
        self.write('disp:wind%i:trac%i:feed m%i' %(meas, meas, meas))
        self.write('calc%i:par:sel m%i' %(meas, meas))
        self.write('sour%i:pow %f' %(meas, power))
        self.write('sens%i:freq:cent %f' %(meas, f))
        self.write('sens%i:freq:span 0' %(meas))
        self.write('sens%i:swe:poin 1' %(meas))
        self.write('sens%i:band %f' %(meas, ifbw))
        self.write('sens%i:aver on'%(meas))
        self.write('sens%i:aver:coun %i' %(meas, avg))
        self.write('sens%i:swe:gro:coun %i'%(meas, avg))

        self._check_errors()
        
##    def run_point_meas(self,it_pk,it_p,bw,pwr):########## TEST!!! ################
##        self.write('calc%i:par:sel m%i'%(it_pk,it_pk))
##        self.set_power(it_pk,pwr)
##        self.set_BW(it_pk,bw[it_pk-1][it_p-1])
##        self.write('sens%i:swe:mode gro;*wai'%it_pk)
##        amp_phase = self.ask('calc%i:mark1:Y?'%it_pk)
##        amp,phase = amp_phase.split(',')
##        return float(amp), float(phase)

    def prelocate(self, peak, region, span, meas=1):
        from ..peak_lorentz_fit import find_fit_region, fit_lorentz
        
        amp, phs = self.run_transM_meas(meas=meas)
        peak_params = self.get_peak_params(meas=meas)

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

        self.autoadjust_freq(peak, fit_params, span, meas=meas)

                    
    def autoadjust_freq(self, peak, fit_params, span, meas=1):
        peak[2] = fit_params[2]*(1-span*2.*fit_params[1]/fit_params[2])
        peak[3] = fit_params[2]*(1+span*2.*fit_params[1]/fit_params[2])
        self.write('sens%i:freq:star %f' %(meas, peak[2]))
        self.write('sens%i:freq:stop %f' %(meas, peak[3]))        


    def set_trans_meas_dual_swp(self, power, f1, f2, nf, ifbw, avg, meas=1):
        if meas == 1:
            self.write('syst:fpr')
            self.write('*cls')

        self.write('disp:wind%i:stat on'%(meas))
        self.write('calc%i:par:def:ext m%i,S21' %(meas, meas))
        self.write('disp:wind%i:trac%i:feed m%i' %(meas, meas, meas))
        self.write('calc%i:par:sel m%i' %(meas, meas))
        self.write('sour%i:pow %f' %(meas, power))
        self.write('sens%i:swe:type segm'%(meas))
        self.write('sens%i:segm:arb on'%(meas))
        self.write('sens%i:swe:mode hold'%(meas))
        self.write('trig:sour imm')
        self.write(
            'sens%i:segm:list sstop,2,1,%i,%f,%f,1,%i,%f,%f'%(
                meas, nf, f1, f2, nf, f2, f1
                )
            )
        self.write('sens%i:band %f' %(meas, ifbw))
        self.write('sens%i:aver on'%(meas))
        self.write('sens%i:aver:coun %i' %(meas, avg))
        self.write('sens%i:swe:gro:coun %i'%(meas, avg))

        self._check_errors()
        
    def set_transM_meas(self, power, f1, f2, nf, ifbw, avg, meas=1):
        if meas == 1:
            self.write('syst:fpr')
            self.write('*cls')

        self.write('disp:wind%i:stat on'%(meas))
        self.write('calc%i:par:def:ext m%i,S21' %(meas, meas))
        self.write('disp:wind%i:trac%i:feed m%i' %(meas, meas, meas))
        self.write('calc%i:par:sel m%i' %(meas, meas))
        self.write('sour%i:pow %f' %(meas, power))
        self.write('sens%i:freq:star %f' %(meas, f1))
        self.write('sens%i:freq:stop %f' %(meas, f2))
        self.write('sens%i:swe:poin %i' %(meas, nf))
        self.write('sens%i:band %f' %(meas, ifbw))
        self.write('sens%i:aver on'%(meas))
        self.write('sens%i:aver:coun %i' %(meas, avg))
        self.write('sens%i:swe:gro:coun %i'%(meas, avg))

        self._check_errors()

    def run_transM_meas(self, meas=1):
        self.write('sens%i:swe:mode gro;*wai'%(meas))
        self.write('calc%i:form mlog'%(meas))
        amp = self.ask("calc%i:data? fdata"%(meas))
        self.write('calc%i:form phas'%(meas))
        phs = self.ask("calc%i:data? fdata"%(meas))
        self.write('calc%i:form mlog'%(meas))
        self.write("disp:wind%i:trac%i:y:auto"%(meas, meas)) #autoscale
        amp_f = np.array(map(float, amp.split(',')))
        phs_f = np.array(map(float, phs.split(',')))
        return amp_f, phs_f

    def set_reflectM_meas(self, power, f1, f2, nf, ifbw, avg, meas=1):
        if meas == 1:
            self.write('syst:fpr')
            self.write('*cls')
            self.write('disp:wind:stat on')
        
        self.write('calc%i:par:def:ext m%i,S11' %(meas, meas))
        self.write('disp:wind%i:trac%i:feed m%i' %(meas, meas, meas))
        self.write('calc%i:par:sel m%i' %(meas, meas))
        self.write('sour%i:pow %f' %(meas, power))
        self.write('sens%i:freq:star %f' %(meas, f1))
        self.write('sens%i:freq:stop %f' %(meas, f2))
        self.write('sens%i:swe:poin %i' %(meas, nf))
        self.write('sens%i:band %f' %(meas, ifbw))
        self.write('sens%i:aver on'%(meas))
        self.write('sens%i:aver:coun %i' %(meas, avg))
        self.write('sens%i:swe:gro:coun %i'%(meas, avg))
            
        self._check_errors() 
        
    def run_transM_measXY(self):
        '''
        output X and Y quadratures (lin)
        Transmission: 10*log_10(x_lin**2+y_lin**2) [dB]
        '''
        self.write('sens:swe:mode gro;*wai')
        self.write('calc:form pol')
        data = self.ask('calc:data? fdata')
        self.write("disp:wind%i:trac%i:y:auto"%(meas, meas)) #autoscale
        data_f = np.array(map(float,data.split(',')))
        x_lin = data_f[:len(data_f):2]
        y_lin = data_f[1:len(data_f):2]
        return x_lin, y_lin
    
    def set_power_ifbw(self, power_dBm, power_dBm_ref, ifbw_ref, meas=1):
        '''
        setting the IFBW according to applied power to get similar
        level of noise. IFBW is adjusted to power_ref_dBm and ifbw_ref
        '''
        ifbws = [
            1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200,
            300, 500, 700, 1e3, 1.5e3, 2e3, 3e3, 5e3, 7e3, 10e3,
            15e3, 20e3, 30e3
            ]

        ifbw_calc = ifbw_ref*10**((power_dBm-power_dBm_ref)/10)

        ifbw = ifbws[-1]
        for i in ifbws:
            if ifbw_calc <= i:
                ifbw = i
                break

        self.write('sour%i:pow %f' %(meas, power_dBm))
        self.write('sens%i:band %f' %(meas, ifbw))

        return ifbw

    def set_par_transM_meas(self, power, f1_recv, f2_recv, nf, ifbw, avg):
        '''
        source is set to twice the frequency of the source
        to measure parametric effects.
        '''
        self.set_transM_meas(power, f1_recv, f2_recv, nf, ifbw, avg)
        self.write('sens:fom:rang2:freq:mult 2')
        self.write('sens:fom:stat 1')

    def get_peak_params(self, meas=1):
        '''
        autoscales window with i-th measurement and returns list:
        [bandwidth, center_freq, Q, loss]
        '''
        self.write("disp:wind%i:trac%i:y:auto"%(meas, meas)) #autoscale
        self.write('calc%i:mark1 ON' %(meas))
        self.write('calc%i:mark1:func:exec MAX'%(meas))
        self.write('calc%i:mark1:bwid -3'%(meas))
        resp = self.ask('calc%i:mark1:bwid?'%(meas))
        return map(float, resp.split(','))

        
#Here you can add new methods
