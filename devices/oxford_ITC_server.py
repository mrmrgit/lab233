'''
Socket server on localhost (port 50107). It serves for communication between
Oxford instruments Intelligent Temperature Controller for HelioxAC-V 3He
Refrigerator System and measurement scripts. Communication to the device
via the server should be used when multiple scripts using the device are to
be run simultaneously (use module oxford_ITC_virt). Otherwise it is possible to
use direct communication line between script and the device (use module
oxford_ITC). Note that each script has to use oxford_ITC_virt, not only one
of them!

---------------------------------------------------------------
COMMUNICATION BETWEEN SERVER AND CLIENT:
It is possible to send any request to the server (data_in) and its response
is determined by comm_func defined below. Server also prints a message about
incoming request (also determined by comm_func).

COMMANDS:
'GET:SAMP:TEMP'   - returns temperature of the sample (3He pot)
'SET:HSW ON'      - sets the heat-switch on
'SET:HSW OFF'     - sets the heat-switch off
'SET:SORB:TEMP x' - sets sorbtion pump temperature to x Kelvin
'GET:PTC2:TEMP'   - returns PTC2 temperature
'GET:HSW:TEMP'    - returns heat-switch temperature
'GET:SORB:TEMP'   - returns sorbtion pump temperature
'CLOSE'           - terminates connection to server

NOTE: commands are case insensitive.
'''

import socket
import time
import threading

from lab233.devices import oxford_ITC


itc = oxford_ITC.init_device(timeout=20)

#communication function for server
#gets message_in from client and returns message_out 
def comm_func(message_in):
    #changing case of message_in, stripping of leading and trailing spaces
    #and splitting it to command part and parameter (if present)
    message_in = message_in.upper()
    msg_stripped = message_in.strip(' ').split(' ') 

    cmd = msg_stripped[0]
    par = None
    if len(cmd)>1: par = msg_stripped[-1]

    if cmd == 'GET:SAMP:TEMP':
        temp = itc.get_sample_temp()
        message_out = 'SAMP:TEMP %.3f'%temp
        server_message = 'SAMP:TEMP is %.3f'%temp
        
    elif cmd == 'SET:HSW':
        if par == 'ON':
            itc.turn_hsw_on()
            message_out = 'HSW ON'
            server_message = 'HSW is ON'
        elif par == 'OFF':
            itc.turn_hsw_off()
            message_out = 'HSW OFF'
            server_message = 'HSW is OFF'
        else:
            message_out = 'Wrong parameter!'
            server_message = 'Wrong parameter!'
            
    elif cmd == 'SET:SORB:TEMP':
        if par == None:
            message_out = 'Parameter missing!'
            server_message = 'Parameter missing!'
        else:
            try:
                temp = float(par)
                itc.set_sorb_temp(temp)
                message_out = 'SORB:TEMP SET'
                server_message = 'SORB:TEMP set to %3.f'%temp
            except ValueError:
                message_out = 'Wrong parameter! Must be a number!'
                server_message = 'Wrong parameter! Must be a number!'
                
    elif cmd == 'GET:PTC2:TEMP':
        temp = itc.get_ptc2_temp()
        message_out = 'PTC2:TEMP %.3f'%temp
        server_message = 'PTC2:TEMP is %.3f'%temp

    elif cmd == 'GET:HSW:TEMP':
        temp = itc.get_hsw_temp()
        message_out = 'HSW:TEMP %.3f'%temp
        server_message = 'HSW:TEMP is %.3f'%temp

    elif cmd == 'GET:SORB:TEMP':
        temp = itc.get_sorb_temp()
        message_out = 'SORB:TEMP %.3f'%temp
        server_message = 'SORB:TEMP is %.3f'%temp

    elif cmd == 'CLOSE':
        message_out = 'connection closed'
        server_message = 'connection closed'
        
    else:
        message_out = 'Unknown command!'
        server_message = 'Unknown command!'
        
    return message_out, server_message

try:
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 50107              # This port number has to be the same as oxford_ITC_virt port number 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print('Oxford ITC server started.')

    #variable which tells threads if the ITC is being used by other thread or not
    rdy_to_go = True  
    
    #function for Threads
    def return_message(conn,addr):
        global rdy_to_go
        while True:
            conn_active = True
            if rdy_to_go:
                data_in = conn.recv(1024) #wait until data received
                #if not data_in: break #?????????????????????????????
                rdy_to_go = False
                data_out, server_msg = comm_func(data_in)
                rdy_to_go = True
                print(addr[0]+':'+str(addr[1])+'\t'+str(server_msg))
                conn.sendall(data_out)
                if server_msg == 'connection closed':
                    conn_active = False
                    break
            #if not conn_active: break#??????
        conn.close()
        #time.sleep(5)
        
    communications = []   
    while True:
        conn, addr = s.accept() #waiting until connection established
        print('Connected by ' + addr[0]+':'+str(addr[1]))
        time.sleep(2)
        comm = threading.Thread(target=return_message, args=(conn,addr,))
        communications.append(comm)
        comm.start()
    s.close()
#if error is thrown, it means that the socket is already open
#and server is running

except:
    pass

