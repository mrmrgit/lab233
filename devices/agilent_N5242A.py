'''
import agilent_N5242A       #DON'T DO: " from agilent_N5242A import * " !!!
vna = agilent_N5242A.init_device(timeout=300)
vna.ask('syste:err?')                #visa.Instrument method
vna.set_BW(1,100)                      #user's defined method
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
    def reset(self):
        self.write("SYST:FPReset")
    def clear(self):
        self.write("*CLR")
        
    def preset(self):
        self.write("SYST:FPReset")

    def create_meas(self,window,calc,trace,name,meas_par):
        #Create and turn on window/channel 1
        self.write("DISPlay:WINDow%s:STATE ON"%window)
        #Define a measurement name, parameter
        self.write("CALCulate%s:PARameter:DEFine:EXT '%s',%s"%(calc,name,meas_par))
        #Associate ("FEED") the measurement name ('MyMeas') to WINDow 
        self.write("DISPlay:WINDow%s:TRACe%s:FEED '%s'"%(window,trace,name))
        
    def create_meas_pol(self,window,calc,trace,name,meas_par):
        #Create and turn on window/channel 1
        self.write("DISPlay:WINDow%s:STATE ON"%window)
        #Define a measurement name, parameter
        self.write("CALCulate%s:PARameter:DEFine:EXT '%s',%s"%(calc,name,meas_par))
        #Associate ("FEED") the measurement name ('MyMeas') to WINDow 
        self.write("DISPlay:WINDow%s:TRACe%s:FEED '%s'"%(window,trace,name))
        self.write("CALC:FORM POL")
        

    def set_frequency_range(self,sens,start,stop):
        self.write(':SENS%s:FREQ:STAR %s' %(sens,start))
        self.write(':SENS%s:FREQ:stop %s' %(sens,stop))

    def set_frequency_range(self,sens,start,stop):
        self.write(':SENS%s:FREQ:STAR %s' %(sens,start))
        self.write(':SENS%s:FREQ:stop %s' %(sens,stop))

    def set_nop(self,sens,nop):
        self.write("SENS%s:SWE:POIN %f" %(sens,nop))

    def set_BW(self,sens,bw):
        self.write(':SENS%s:BAND %f'%(sens,bw))
                  
    def set_BWID(self,calc,mark,bwid):
        self.write('CALC%s:MARK%s:BWID %f'%(calc,mark,bwid))
                  
    def set_marker_on(self,calc,mark):
        self.write("CALC%s:MARK%s ON"%(calc,mark))

    def set_trigger_mode(self,mode):
        self.write("TRIG:SOUR %s"%(mode))

    def set_sweep_mode(self,sens,mode):
        self.write("SENS%s:SWE:MODE %s"%(sens,mode))

    def set_power(self,sour,power):
        self.write(':SOUR%s:POW %s' %(sour,power))

    def do_one_sweep(self,sens):
        self.write("SENS%s:SWE:MODE SINGle;*wai"%(sens))

    def auto_scale(self,window,trace):
        self.write("DISP:WIND%s:TRAC%s:Y:AUTO"%(window,trace))

    def find_max(self,calc,mark):
        self.write('CALC%s:MARK%s:FUNC:EXEC MAX'%(calc,mark))

    def get_bwid(self,calc,mark):
        resp = self.ask('CALC%s:MARK%s:BWID?'%(calc,mark))
        return map(float,resp.split(','))          

    def get_quality(self,calc,mark,bwid):
        self.find_max(calc,mark)
        self.set_BWID(calc,mark,bwid)
        resp=self.get_bwid(calc,mark)    
        return resp

    def get_trace(self,name,calc,data_format,startf,stopf,nop):
        self.write("CALC%s:PAR:SEL '%s'"%(calc,name))
        resp = self.ask("CALC%s:DATA? %s"%(calc,data_format))
        y=map(float,resp.split(','))
        y=np.array(y)
        x=np.linspace(startf,stopf,num=nop,endpoint=True)
        return x,y

    def get_trace_pol(self,name,calc,data_format,startf,stopf,nop):
        self.write("CALC%s:PAR:SEL '%s'"%(calc,name))
        d = self.ask("CALC%s:DATA? %s"%(calc,data_format))
        
        d=map(float,d.split(','))
        

        amp=[d[i] for i in range (0,len(d),2)]
        pha=[d[i] for i in range (1,len(d),2)]
        x=np.linspace(startf,stopf,num=nop,endpoint=True)
        amp=np.array(amp)
        pha=np.array(pha)
        return x,amp,pha

    def get_trace_dual(self,name,calc,data_format,startf,stopf,nop):
        self.write("CALC%s:PAR:SEL '%s'"%(calc,name))
        resp = self.ask("CALC%s:DATA? %s"%(calc,data_format))
        y=map(float,resp.split(','))
        y=np.array(y)
        xf=np.linspace(startf,stopf,num=nop,endpoint=True)
        xr=np.linspace(stopf,startf,num=nop,endpoint=True)
        x=np.append(xf,xr)
        return x,y

    def set_sweep_type(self,cnum,stype):
        self.write('SENS%s:SWE:TYPE %s'%(cnum,stype))

    def set_segment_shortlist(self,cnum,numSegs,state,nop,fstart,fstop):
        self.write('SENS%s:SEGM:LIST SSTOP,%s,%s,%s,%s,%s'%(cnum,numSegs,state,nop,fstart,fstop))
      
    def set_segment_list(self,cnum,numSegs,state,nop,fstart,fstop,IFBW,dwelltime,power):
        self.write('SENS%s:SEGM:LIST SSTOP,%s,%s,%s,%s,%s,%s,%s,%s,'%(cnum,numSegs,state,nop,fstart,fstop,IFBW,dwelltime,power))

    def set_dual_sweep(self,cnum,nop,fstart,fstop,IFBW,dwelltime,power):
        self.write('SENS%s:SEGM:LIST SSTOP,2,1,%s,%s,%s,%s,%s,%s,1,%s,%s,%s,%s,%s,%s'%(cnum,nop,fstart,fstop,IFBW,dwelltime,power,nop,fstop,fstart,IFBW,dwelltime,power))

    def set_dual_sweep_short(self,cnum,nop,fstart,fstop):
        self.write('SENS%s:SEGM:LIST SSTOP,2,1,%s,%s,%s,1,%s,%s,%s'%(cnum,nop,fstart,fstop,nop,fstop,fstart))

    def arb_segment_sweep_on(self,cnum):
        self.write('SENS:SEGM:ARB ON')

    def arb_segment_sweep_off(self,cnum):
        self.write('SENS:SEGM:ARB OFF')

    def set_pulse_on(self,measN):
        self.write("SENS:PULS '%s' 1"%(measN))

    def set_pulse_off(self,measN):
        self.write("SENS:PULS '%s' 0"%(measN))

    def set_pulse_period(self,measN,period):
        self.write("SENS:PULS:PER '%s' %s"%(measN,period))

    def set_pulse_delay(self,measN,delay):
        self.write("SENS:PULS:DEL '%s' %s"%(measN,delay))
        
    def set_pulse_widt(self,measN,widt):
        self.write("SENS:PULS:WIDT '%s' %s"%(measN,widt))
    
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
        
    def set_trans_meas(self,peaks):
        self.reset()
        self.write('*cls')
        it=1
        for pk in peaks:
            self.create_meas(it,it,it,'MyMeas%s'%it,'S21')
            self.set_frequency_range(it,pk[2],pk[3])
            self.set_nop(it,pk[4])
            self.set_BW(it,pk[0])
            self.set_marker_on(it,1)
            self.set_sweep_mode(it,'HOLD')
            it+=1
        self.set_trigger_mode("IMM")
        
        self._check_errors()#####
        
    def run_trans_meas(self,pk,it_pk,it_p,bw,pwr,dual_swp):        
        if dual_swp: self.set_dual_sweep_short(it_pk+1,pk[4],pk[2],pk[3])
        self.set_BW(it_pk+1,bw[it_pk][it_p-1])
        self.set_power(it_pk+1,pwr)
        self.do_one_sweep(it_pk+1)
        self.auto_scale(it_pk+1,it_pk+1)
        return self.get_quality(it_pk+1,1,-3)
    
    def set_point_meas(self,peaks):
        #peak=[IFBW_ref,P_ref,f,avg]
        self.write('syst:fpr')
        self.write('*cls')####### TEST
        it=1
        for pk in peaks:
            self.write('disp:wind%i:stat on'%it)
            self.write('calc%i:par:def:ext m%i,S21'%(it,it))
            self.write('disp:wind%i:trac%i:feed m%i'%(it,it,it))
            self.write('calc%i:par:sel m%i'%(it,it))
            self.write('calc%i:mark1 on'%it)
            self.write('calc%i:mark:form logp'%it)
            self.write('sens%i:freq:cent %f'%(it,pk[2]))
            self.write('sens%i:freq:span 0'%it)
            self.write('sens%i:swe:poin 1'%it)
            self.write('sens%i:band %f'%(it,pk[0]))
            self.write('sens%i:aver on'%it)
            self.write('sens%i:aver:coun %i'%(it,pk[3]))
            self.write('sens%i:swe:gro:coun %i'%(it,pk[3]))
            it+=1

        self._check_errors()#####
        
    def run_point_meas(self,it_pk,it_p,bw,pwr):########## TEST!!! ################
        self.write('calc%i:par:sel m%i'%(it_pk,it_pk))
        self.set_power(it_pk,pwr)
        self.set_BW(it_pk,bw[it_pk-1][it_p-1])
        self.write('sens%i:swe:mode gro;*wai'%it_pk)
        amp_phase = self.ask(':calc%i:mark1:Y?'%it_pk)
        amp,phase = amp_phase.split(',')
        return float(amp), float(phase)

    def prelocate(self,peaks,region,sp):
        #it is used only once in a script, so it doesn't matter that
        #'functions' is imported here 
        from lab233.functions import find_fit_region, fit_lorentz
        it=1
        for pk in peaks:
            self.set_BW(it,pk[0])            
            self.set_power(it,pk[1])
            self.do_one_sweep(it)            
            self.auto_scale(it,it)
            p=self.get_quality(it,1,-3)
            x,y=self.get_trace('MyMeas%s'%(it),(it),'FDATA',pk[2],pk[3],pk[4])
            startp,stopp=find_fit_region(pk[2],pk[3],p[1],pk[4],region)#fitting region
            p1,chi1=fit_lorentz(x[startp:stopp],y[startp:stopp],p)#fitting
            pk[2],pk[3]=p[1]*(1-sp/p[2]),p[1]*(1+sp/p[2])
            self.set_frequency_range(it,pk[2],pk[3])
            it+=1

    def autoadjust_freq(self,pk,it_pk,p,sp):
        pk[2],pk[3]=p[1]*(1-sp/p[2]),p[1]*(1+sp/p[2])
        self.set_frequency_range(it_pk+1,pk[2],pk[3])

    def set_transM_meas(self, power, f1, f2, nf, ifbw, avg):
        #matus -for MAG 
        self.write('syst:fpr')
        self.write('*cls')

        self.write('disp:wind:stat on')
        self.write('calc:par:def:ext m,S21')
        self.write('disp:wind:trac:feed m')
        self.write('calc:par:sel m')
        self.write('sour:pow %f' %power)
        self.write('sens:freq:star %f' %f1)
        self.write('sens:freq:stop %f' %f2)
        self.write('sens:swe:poin %i' %nf)
        self.write('sens:band %f' %ifbw)
        self.write('sens:aver on')
        self.write('sens:aver:coun %i' %avg)
        self.write('sens:swe:gro:coun %i'% avg)
            
        self._check_errors()#####       

    def run_transM_meas(self):
        #matus -for MAG
        self.write('sens:swe:mode gro;*wai')
        self.write('calc:form mlog')
        amp = self.ask("calc:data? fdata")
        self.write('calc:form phas')
        phs = self.ask("calc:data? fdata")
        amp_f = np.array(map(float,amp.split(',')))
        phs_f = np.array(map(float,phs.split(',')))
        return amp_f, phs_f

    def set_reflectM_meas(self, power, f1, f2, nf, ifbw, avg):
        #matus -for MAG 
        self.write('syst:fpr')
        self.write('*cls')

        self.write('disp:wind:stat on')
        self.write('calc:par:def:ext m,S11')
        self.write('disp:wind:trac:feed m')
        self.write('calc:par:sel m')
        self.write('sour:pow %f' %power)
        self.write('sens:freq:star %f' %f1)
        self.write('sens:freq:stop %f' %f2)
        self.write('sens:swe:poin %i' %nf)
        self.write('sens:band %f' %ifbw)
        self.write('sens:aver on')
        self.write('sens:aver:coun %i' %avg)
        self.write('sens:swe:gro:coun %i'% avg)
            
        self._check_errors()#####
        
    def run_transM_measXY(self):
        #matus -for MAG
        '''
        output X and Y quadratures (lin)
        Transmission: 10*log_10(x_lin**2+y_lin**2) [dB]
        '''
        self.write('sens:swe:mode gro;*wai')
        self.write('calc:form pol')
        data = self.ask('calc:data? fdata')
        data_f = np.array(map(float,data.split(',')))
        x_lin = data_f[:len(data_f):2]
        y_lin = data_f[1:len(data_f):2]
        return x_lin, y_lin
    
    def set_power_ifbw(self, power_dBm, power_dBm_ref, ifbw_ref):
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

        self.write('sour:pow %f' %power_dBm)
        self.write('sens:band %f' %ifbw)

    def set_par_transM_meas(self, power, f1_recv, f2_recv, nf, ifbw, avg):
        '''
        source is set to twice the frequency of the source
        to measure parametric effects.
        '''
        self.set_transM_meas(power, f1_recv, f2_recv, nf, ifbw, avg)
        self.write('sens:fom:rang2:freq:mult 2')
        self.write('sens:fom:stat 1')

#Here you can add new methods
