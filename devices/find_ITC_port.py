'''
A script for finding ITC serial port.
'''
import visa

max_port = 20

print('''Scanning serial ports 1 - %i.
This may take a while. Please wait.'''%max_port)

for i in range(1,max_port+1):
    try:
        itc = visa.instrument('asrl%i::instr'%i,timeout=5)

        resp = itc.ask('@1R3')
        temp = resp.replace('R','')
        print('sensor: ' + str(i))
        print('TEMP_POT_HIGH: ' + temp)
        itc.close()
        break
    except visa.VisaIOError:
        pass

if i == max_port:
    print('ITC serial port has not been found. Check if the device is connected')

raw_input('press ENTER to continue...')
