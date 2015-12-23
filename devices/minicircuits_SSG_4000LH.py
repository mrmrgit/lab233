'''
Windows (64-bit) wrapper around mcl_gen64.dll for

Mini-circuits USB synthesized signal generator SSG-4000LH

To make this module running, you need to copy all of the files from folder
"SSG-4000LH_dlls" to Python dll folder (e.g. "C:/Python27/DLLs"). It includes
mcl_gen64.dll - library from manufacturer and "python clr" module libraries

Example:
---------------------------------------------------------------
import time
import minicircuits_SSG_4000LH as ssg

#connect to the device and print info
mc = ssg.SSG()
mc.print_info()

#set 255 MHz sine wave with amplitude -15 dBm chopped by 120 kHz pulses
mc.set_int_modulation_status('on')
mc.set_int_trg_freq(120e3)
mc.set_freq_power(255e6, -15)

#start the generator for 5 seconds and then disconnect device
mc.set_output('on')
time.sleep(5)
mc.set_output('off')
mc.disconnect()
---------------------------------------------------------------
Matus Rehak

Last update: 22.12.2015
'''

import clr
clr.AddReference("mcl_gen64")
import mcl_gen64

class SSG(object):
    def __init__(self):
        self.device = mcl_gen64.usb_gen()
        self.device.Connect('')

        #Setting some device variables
        self.trgOUT = 0
        self.int_modulation_status = 0
        self.int_trg_freq = 100e3

        #Loading device power and frequency limits.
        #These values are used for checking if the
        #user sets valid values
        lims = self.get_dev_lims()
        self.FREQ_MAX = lims[0]     #in [Hz] 
        self.FREQ_MIN = lims[1]     #in [Hz]
        self.PWR_MAX = lims[2]      #in [dBm]
        self.PWR_MIN = lims[3]      #in [dBm]

############## "SET" COMMANDS ############################
        
    def disconnect(self):
        '''
        Disconnect the device
        '''
        self.device.Disconnect()

    def set_output(self, status):
        '''
        Set the device output on or off. 
        All of these are valid: 'on'/'off', 'ON'/'Off', 'ON'/'OFF',
        '1'/'0', 1/0 
        '''
        if str(status).lower() == 'on' or str(status) == '1':
            self.device.SetPowerON()
        elif str(status).lower() == 'off' or str(status) == '0':
            self.device.SetPowerOFF()
        else:
            raise RuntimeError('Invalid settings')

        if self.int_modulation_status:
            t, T_unit = self._mod_freq_dev_settings()
            self.device.Set_PulseMode(t/2.0, t/2.0, T_unit)

    def set_trgOUT(self, trgOUT):
        '''
        Set trigger out on or off.
        All of these are valid: 'on'/'off', 'ON'/'Off', 'ON'/'OFF',
        '1'/'0', 1/0 
        '''
        if str(trgOUT).lower() == 'on' or str(trgOUT) == '1':
            self.trgOUT = 1
        elif str(trgOUT).lower() == 'off' or str(trgOUT) == '0':
            self.trgOUT = 0
        else:
            raise RuntimeError('Invalid settings')

    def set_int_modulation_status(self, status):
        '''
        Set if the device output is modulated by square function.
        Output is "chopped" by frequency used by set_int_trg_freq()
        function.
        all of these are valid: 'on'/'off', 'ON'/'Off', 'ON'/'OFF',
        '1'/'0', 1/0, 1.0/0.0
        
        NOTE: It takes effect only after next set_output() command.
        
        BUG: If you send another device during pulsing (e.g.
        get_address() or set_power()), device will stop pulsing.
        You will restart by sending set_output(1) command.
        '''
        if str(status).lower() == 'on' or str(status) == '1':
            self.int_modulation_status = 1
        elif str(status).lower() == 'off' or str(status) == '0':
            self.int_modulation_status = 0
        else:
            raise RuntimeError('Invalid settings')

    def set_int_trg_freq(self, int_trg_freq):
        '''
        Set modulation ("chopping") frequency of the output signal.
        
        int_trg_freq -> frequency of modulation [Hz]
        
        NOTE: It takes effect after next set_output() command.
        '''
        if int_trg_freq <=0.5e6:
            self.int_trg_freq  = int_trg_freq
        else:
            raise RuntimeError('pulse frequency out of range')

    def _mod_freq_dev_settings(self):
        '''
        Device has two time scales - 1 microsecond and 1 milisecond.
        This function decides which time scale to use and how long is the
        period in this time scale. this function produces data for 50%
        ON time and 50% OFF time
        
        T_unit - range microseconds (0) or miliseconds (1)
        t - time period, ON + OFF time
        '''
        if self.int_trg_freq <=0.5e6 and self.int_trg_freq != 0:
            if self.int_trg_freq <=0.5e3:
                T_unit=1
                t = 1e3/self.int_trg_freq
            else:
                T_unit=0
                t = 1e6/self.int_trg_freq
            return t, T_unit#return t/2.0, T_unit
        else:
            raise RuntimeError('pulse frequency out of range')
        
    def set_freq_power(self, freq, pwr):
        '''
        Set device output signal frequency and power simultaneously
        
        freq -> frequency [Hz]
        pwr  -> power [dBm]
        
        NOTE: SetFreqAndPower() function below takes input argument
        frequency in MHz. That is why freq is multiplied by 1e-6
        '''
        if freq >= self.FREQ_MIN and freq <= self.FREQ_MAX:
            if pwr >= self.PWR_MIN and pwr <= self.PWR_MAX:
                self.device.SetFreqAndPower(freq*1e-6, pwr, self.trgOUT)
            else:
                raise RuntimeError('Power out of range')
        else:
            raise RuntimeError('Frequency out of range')
            
    def set_freq(self, freq):
        '''
        Set device output signal frequency
        
        freq -> frequency [Hz]
        
        NOTE: SetFreq() function below takes input argument
        frequency in MHz. That is why freq is multiplied by 1e-6
        '''
        if freq >= self.FREQ_MIN and freq <= self.FREQ_MAX:
            self.device.SetFreq(freq*1e-6, self.trgOUT)
        else:
            raise RuntimeError('Frequency out of range')
        
    def set_power(self, pwr):
        '''
        Set device output signal power
        
        pwr  -> power [dBm]
        '''
        if pwr >= self.PWR_MIN and pwr <= self.PWR_MAX:
            self.device.SetPower(pwr, self.trgOUT)
        else:
            raise RuntimeError('Power out of range')
        
    def set_noise_mode(self,mode):
        '''
        Mode -> low noise mode 0, low spur mode 1
        '''
        self.device.Set_Noise_Spur_Mode(mode)
        
############## "GET" COMMANDS ############################
        
    def get_trgIN_status(self):
        '''
        Status of the input trigger
        '''
        ret=self.device.GetTriggerIn_Status()
        return ret

    def get_10MHzRef_status(self):
        '''
        Status of the 10MHz reference
        '''
        ret = self.device.ExtRefDetected()
        return ret

    def get_int_trg_freq(self):
        '''
        Frequency of internal modulation [Hz]
        '''
        return self.int_trg_freq
    
    def get_step_freq(self):
        '''
        Frequency [Hz] of the step of the output signal in step mode,
        which is not implemented here, however it is in mcl_gen64.dll 
        
        NOTE: function below outputs frequency in kHz.
        That is why freq is multiplied by 1e3
        '''
        ret = self.device.GetGenStepFreq()        
        return ret * 1e3

    def get_noise_mode(self):
        '''
        Get either low noise mode or low spurious mode
        '''
        mod = self.device.Get_Noise_Spur_Mode(0)
        if mod[1]==0:
            ret = 'low noise mode'
        elif mod[1]==1:
            ret = 'low spur mode'
        return ret

    def get_status(self):
        '''
        Output status of the device
        '''
        ret=self.device.GetGenStatus(0,0,0,0,0,0)
        return ret[2]

    def get_freq(self):
        '''
        Frequency [Hz] of the output signal
        
        NOTE: GetGenStatus() function below takes outputs
        frequency in MHz. That is why ret is multiplied by 1e6
        '''
        ret=self.device.GetGenStatus(0,0,0,0,0,0)
        return ret[3]*1e6

    def get_power(self):
        '''
        Power [dBm] of the output singal
        '''
        stat=self.device.GetGenStatus(0,0,0,0,0,0)
        return stat[4]


    def get_dev_lims(self):
        '''
        Output list of the device limits:
        maximum frequency [Hz],
        minimum frequency [Hz],
        maximum power [dBm],
        minimum power [dBm]
        '''
        lims = []
        lims.append(self.device.GetGenMaxFreq()*1e6)
        lims.append(self.device.GetGenMinFreq()*1e6)
        lims.append(self.device.GetGenMaxPower())
        lims.append(self.device.GetGenMinPower())
        return lims
    
    def get_address(self):
        '''
        Address of the device
        ''' 
        ret=self.device.Get_Address()
        return ret

    def get_name(self):
        '''
        Model name of the device
        '''
        ret = str(self.device.Read_ModelName('')[1])
        if not ret: ret = 'not connected'       #if ret is an empty string
        return ret

    def get_serial_number(self):
        '''
        Serial number of the device
        '''
        ret = str(self.device.Read_SN('')[1])
        if not ret: ret = 'not connected'       #if ret is an empty string
        return ret

    def print_info(self):
        '''
        Prints info about the device
        '''
                
        lims = self.get_dev_lims()

        print('DEVICE INFO:')
        print('Name:\t\t\t%s' %self.get_name())
        print('Address:\t\t%s' %self.get_address())
        print('Serial number:\t\t%s' %self.get_serial_number())
        print('Maximum frequency:\t%s MHz' %(lims[0]*1e-6))
        print('Minimum frequency:\t%s MHz' %(lims[1]*1e-6))
        print('Maximum power:\t\t%s dBm' %lims[2])
        print('Minimum power:\t\t%s dBm' %lims[3])
