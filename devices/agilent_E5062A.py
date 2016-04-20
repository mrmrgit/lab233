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
    def clear(self):
        self.write("*CLS")

    def preset(self):
        self.write("*RST")

    def read_error(self):
        return self.ask("SYST:ERR?")

    def turn_on_disp(self,ndisp):
        self.write("DISP:WIND%s:ACT"%ndisp)

    def select_trace(self,nCalc,par):
        self.write('CALC%s:PAR%s:SEL'%(nCalc,par))

    def create_simple_meas(self,nCalc,Spar,fData):    
        self.write(":CALC%s:PAR:COUN 1"%nCalc)
        self.write(":CALC%s:PAR:DEF %s"%(nCalc,Spar))
        self.write(":DISP:WIND%s:ACT"%nCalc)
        self.write(":CALC%s:FORM %s"%(nCalc,fData))

    def auto_scale(self,wind,trace):
        self.write("DISP:WIND%s:TRAC%s:Y:AUTO"%(wind,trace))

    def split_display(self,N):
        """
        {D1|D12|D1_2|D112|D1_1_2|D123|D1_2_3|D12_33|D11_23|D13_23|
        D12_13| D1234|D1_2_3_4|D12_34}
        """
        if N==1:
            dispConfig='D1'
        elif N==2:
            dispConfig='D1_2'
        elif N==3:
            dispConfig='D1_2_3'
        elif N==4:
            dispConfig='D1234'
        else:
            print "to many traces"
            
        self.write("DISP:SPLit %s"%dispConfig)

    def set_trigger_source(self,source):
        self.write(':TRIG:SOUR %s'%source)

    def send_trigger(self):
        self.write(":TRIG:SING;*WAI")              
                  
    def set_initiation(self,nCalc,state):
        self.write(':INIT%s:CONT %s'%(nCalc,state))              

    def set_search_max(self,nCalc,nMark):          
        self.write('CALC%s:MARK%s:FUNC:TYPE MAX'%(nCalc,nMark))
                  
    def set_bw_search_on(selfnCalc,mark,THR):
        self.write(':CALC%s:MARK%s:BWID ON'%(nCalc,mark))
        self.write(':CALC%s:MARK%s:BWID:THR %s'%(nCalc,mark,THR))

    def execute_marker(self,nCalc,par,marker):
        self.write('CALC%s:PAR%s:SEL'%(nCalc,par))
        self.write('CALC%s:MARK%s:FUNC:EXEC'%(nCalc,marker))             

    def get_quality(self,nCalc,mark):
        resp=self.ask(':CALC%s:MARK%s:BWID:DATA?'%(nCalc,mark))    
        return map(float,resp.split(','))

    def set_one_sweep(self,i,nPeaks):

        for j in range(1,nPeaks+1):
            if j==i:
                sself.et_initiation(i,'ON')
                
            else:
                self.set_initiation(j,'OFF')
                   
    '''
    def read(self,calc):
        data = self.ask(':CALC%s:DATA:FDAT?'%calc)
        d=map(float,data.split(','))
        amp=[d[i] for i in range (0,len(dd),2)]
        pha=[d[i] for i in range (0,len(dd),2)]          
        return amp
    '''
    def get_trace(self,calc,startf,stopf,nop):
        data = self.ask(':CALC%s:DATA:FDAT?'%calc)
        d=map(float,data.split(','))
        amp=[d[i] for i in range (0,len(d),2)]
        pha=[d[i] for i in range (1,len(d),2)]
        x=np.linspace(startf,stopf,num=nop,endpoint=True)
        amp=np.array(amp)
        pha=np.array(pha)
        
        return x,amp,pha
                  
    def set_output(self,state):
        self.write(':OUTP %s'%(state))
        
    # toto funguje
    #:SENSe{[1]|2|3|4}:SEGMent:DATA 5,<mode>,<ifbw>,<pow>,<del>,<time>,<segm>,
    #agi.write("SENS1:SEGM:DATA 5,0,1,1,0,0,1,1E9,2E9,201,300,0")
    #agi.write("SENSe2:SEGMent:DATA 3,1,1,1,1")

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


    def find_max(self,calc,mark):
        self.write('CALC%s:MARK%s:FUNC:EXEC MAX'%(calc,mark))

    def get_bwid(self,calc,mark):
        resp = self.ask('CALC%s:MARK%s:BWID?'%(calc,mark))
        return map(float,resp.split(','))          

    def get_errs(self):
        #matus
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
        #matus
        self.write('*cls')          
        self.write('*rst')

        self.write('SYST:PRES')
        self.write('SOUR:POW %f' %power)
        self.write('CALC:PAR:COUN 1')
        self.write('CALC:PAR:DEF S21')
        self.write('DISP:WIND:ACT')
        self.write('CALC:FORM PLOG')
        self.write('TRIG:SOUR BUS')
        self.write('INIT:CONT ON')
        self.write("TRIG:SING;*WAI")
        sleep(0.2)
      
        self.write('SENS:FREQ:STAR %f' %f1)
        self.write('SENS:FREQ:STOP %f' %f2)
        self.write('SENS:SWE:POIN %i' %nf)    
        self.write('SENS:BAND %f' %ifbw)
        self.write('SENS:AVER ON')
        self.write('SENS:AVER:COUN %i' %avg)

    def run_transM_meas(self, avg):
        #matus
        self.write('SENS:AVER:CLE')
        self.write('OUTP ON')
        self.write('INIT:CONT ON')
        self.write(self.trigger_repeat(avg))
        self.ask('*opc?') #operation complete?
        self.write('OUTP OFF')
        dr = self.ask('CALC:DATA:FDAT?')
        
        d=map(float,dr.split(','))
        amp=np.array([d[j] for j in range (0,len(d),2)])
        pha=np.array([d[j] for j in range (1,len(d),2)])
        
        return amp, pha

    def trigger_repeat(self, N):
        #matus
        ret=''
        for _ in range(N): ret+=':TRIG:SING;*WAI;'
        return ret        
#Here you can add new methods
