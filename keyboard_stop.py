'''
Function returns brk_sig=True when character stop_char is pressed.
When pause_char is pressed, program pauses.
brk_sig=False otherwise.
stop_char must be one character string
update: 22.6.2015
'''

import msvcrt       # build-in module

def kbfunc():
    return msvcrt.getch() if msvcrt.kbhit() else 0
 
def kb_stop(stop_char,pause_char='P'):
    brk_sig = False
    kp = kbfunc()
    while kp!=0:
        if kp==str(stop_char):
            brk_sig = True
            break
        if kp==str(pause_char):
            raw_input('Press enter to continue.')
        kp = kbfunc()
    return brk_sig
