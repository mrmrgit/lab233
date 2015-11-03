'''
This module has the same functionality as the oxford_ITC wrapper, however
using this module, it is possible to use the device (Oxford instruments
Intelligent Temperature Controller for HelioxAC-V 3He Refrigerator System)
in more scripts.
When initiated, it starts the server on localhost (port 500007) which
directly communicates with the device. Communication between the script
and the server is established using simple socket protocol.

---------------------------------------------------------------
import oxford_ITC_virt
itc = oxford_ITC_virt.init_device()
itc.turn_hsw_on()
print(itc.get_sample_temp())
itc.close()
---------------------------------------------------------------

Matus Rehak
'''

import socket
import time
import os
import site


#run oxford_ITC_server if it is not already started
STP = site.getsitepackages()[1] #Path to site-packages. Only windows!!!
CUR_DIR = os.getcwd()           #current working directory

os.chdir(STP+'\\lab233\\devices')
os.system('START python oxford_ITC_server.py')
os.chdir(CUR_DIR)

def init_device():
    itc_virt = Oxford_ITC_virt()
    return itc_virt

class Oxford_ITC_virt:
    def __init__(self):
        '''
        Initiates the socket which connects to the server.
        The server communicates with the ITC device.
        '''        
        HOST = 'localhost'    
        PORT = 50107         #this port number has to be the same as oxford_ITC_server port number     
        self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._skt.connect((HOST, PORT))       

    def __repr__(self):
        return '<Oxford ITC virtual device>'
    
    #Decorator that checks if the communication with device was closed.
    #Every custom method in this class should be defined with @_open_check
    def _open_check(func):
        def checked_func(self, *args):
            if self._skt is not None:
                ret = func(self,*args)
                return ret
            else:
                raise RuntimeError('The virtual device is closed.')
        return checked_func
    
    def __repr__(self):
        if self._skt is not None:
            return '<Virtual temperature controller for Oxford ITC>'
        else:
            return '<CLOSED virtual temperature controller for Oxford ITC>'            

    @_open_check                     #decorator defined above
    def write(self, msg):
        '''
        Sends an arbitrary message to the server.
        '''
        self._skt.sendall(str(msg))

    @_open_check                     #decorator defined above
    def read(self):
        '''
        Reads response from the server.
        '''
        ret = self._skt.recv(1024)
        return ret

    @_open_check                     #decorator defined above
    def ask(self, msg):
        '''
        Sends an arbitrary message to the server and then reads the response.
        '''
        self._skt.sendall(str(msg))
        ret = self._skt.recv(1024)
        return ret

    @_open_check                     #decorator defined above
    def close(self):
        '''
        Closes the socket. Afterwards, no communication is available until
        new initialization.
        '''
        self._skt.close()
        self._skt = None

    @_open_check                     #decorator defined above
    def get_sample_temp(self):
        '''
        Returns temperature of the sample (3He pot).
        There are 2 temperature sensors, one that works below
        and one that works above 7K.
        '''
        msg = self.ask('GET:SAMP:TEMP')
        temp = msg.split(' ')[-1]
        return float(temp)

    @_open_check                     #decorator defined above
    def turn_hsw_on(self):
        '''
        Turns heat-switch ON, which means heating it to 25K.
        Heat-switch is not ON immmediately, you have to wait
        some time until it is heated to 25K.
        '''
        self.write('SET:HSW ON')
        self.read()                 #cleaning input buffer
        
    @_open_check                     #decorator defined above
    def turn_hsw_off(self):
        '''
        Turns heat-switch OFF, which means cooling it below 7K.
        Heat-switch is not OFF immediately, you have to wait to
        cool down.
        '''
        self.write('SET:HSW OFF')
        self.read()                 #cleaning input buffer
        
    @_open_check                     #decorator defined above
    def set_sorb_temp(self,temp):
        ''' 
        Sets heating of sorbtion pump to selected temperature.
        Temperature may overshoot during heating, be careful!
        '''
        self.write('SET:SORB:TEMP %.3f'%temp)
        self.read()                 #cleaning input buffer
        
    @_open_check                     #decorator defined above
    def get_ptc2_temp(self):
        '''
        Returns temperature of PTC2 which is cooled by cryopump.
        '''
        msg = self.ask('GET:PTC2:TEMP')
        temp = msg.split(' ')[-1]
        return float(temp)
        
    @_open_check                     #decorator defined above
    def get_hsw_temp(self):
        '''
        Returns temperature of heat-switch.
        '''
        msg = self.ask('GET:HSW:TEMP')
        temp = msg.split(' ')[-1]
        return float(temp)
        
    @_open_check                     #decorator defined above
    def get_sorb_temp(self):
        '''
        Returns temperature of sorbtion pump.
        '''
        msg = self.ask('GET:SORB:TEMP')
        temp = msg.split(' ')[-1]
        return float(temp)
