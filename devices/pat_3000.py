'''
Python module for communication with SYMPULS AACHEN PAT3000 pattern generator.

NOTES:
BPG_GET_FREQUENCY (0x85 command) does not work, returns four '0x00' bytes
'''

import serial
from .dev_addrs import COM_PAT_3000

class Pat_3000(object):
    def __init__(self):
        '''
        Initializes communication with the device. 
        COM_PORT parameter of Serial class is zero-based, instead of
        one-based as in Windows (as shown in Device manager).
        '''
        self.device = serial.Serial(COM_PAT_3000 - 1, 9600)
        self.COM_PORT = COM_PAT_3000
        
        # init settings:
        self.pattern_type = 4
        self.trg = 0
        self.lgc = 0
        self.freq = 200e6
        self.amp = 1.0
        self.offs = 0.0

        self.set_pattern_type(self.pattern_type)
        self.set_trigger(self.trg)
        self.set_logic(self.lgc)
        self.set_frequency(self.freq)
        self.set_amplitude(self.amp)
        self.set_offset(self.offs)
        self.set_16bit_pattern(0xaaaa)
        

    def __repr__(self):
        return '<PAT 3000 pattern generator. COM PORT: %i>'%self.COM_PORT
      
        
    def close(self):
        '''
        Closes the communication with the device.
        '''
        self.device.close()


    def _mk_buf(self, hex_list):
        '''
        Function that creates a string from input hex numbers,
        which can be fed into the device as command and data.
        '''
        chr_list = [chr(hex_i) for hex_i in hex_list]
        str_buf = ''.join(chr_list)
        return str_buf


    def _num_to_HiLo(self, number):
        '''
        Function that transforms an input from range 0 - 65535 (0x0000 - 0xffff)
        to high and low byte (first two and second two digits in hex basis)
        '''
        hi = number/0x100
        lo = number%0x100
        return hi, lo

    
    def set_pattern_type(self, pattern_type):
        '''
        Pattern of the device output
        pattern_type (int)
        0    PRS7
        1    PRS15
        2    PRS23
        3    PRS31
        4    FW16
        5    FW8M
        
        FW - user's pattern, PRS - pseudorandom sequence.
        '''
        if pattern_type > 5 or pattern_type < 0:
            raise RuntimeError("Unsupported parameter.")

        buf = self._mk_buf(bytearray([0x01, int(pattern_type)]))
        self.device.write(buf)
        self.pattern_type = pattern_type


    def set_trigger(self, trg):
        '''
        Sets output trigger format:
        trg (int)
        0    word frame (use this one for FW8M)
        1    Clock/16
        '''        
        if not (trg == 0 or trg == 1):
            raise RuntimeError("Unsupported parameter.")

        buf = self._mk_buf(bytearray([0x02, int(trg)]))
        self.device.write(buf)
        self.trg = trg
        
        
    def set_logic(self, lgc):
        '''
        Sets positive or negative logic of output pattern
        lgc (int)
        0    positive
        1    negative
        '''
        if not (lgc == 0 or lgc == 1):
            raise RuntimeError("Unsupported parameter.")

        buf = self._mk_buf(bytearray([0x03, int(lgc)]))
        self.device.write(buf)
        self.lgc = lgc


    def set_ext_clock(self):
        '''
        Locks clock to external source. To use internal clock use set_frequency
        function.
        '''
        buf = self._mk_buf(bytearray([0x05, 0x00, 0x00]))
        self.device.write(buf)
        self.freq = 0

    
    def set_frequency(self, freq):
        '''
        Sets frequency of the internal clock. If the device was previously
        locked to an external source, it is locked to internal clock now.
        frequency [Hz] can be set in range 10e6 - 2.8e9
        '''

        if freq > 2.8e9 or freq < 10e6:
            raise RuntimeError("Frequency out of range.")

        freq_to_write = int(freq*1e-5)      #10 MHz -> 100, 2.8GHz -> 28000

        byte_list = bytearray([0x05])
        byte_list.extend(self._num_to_HiLo(freq_to_write))
        
        buf = self._mk_buf(byte_list)
        self.device.write(buf)
        self.freq = freq


    def set_amplitude(self, amp):
        '''
        Sets the amplitude of the outputs NRZ and /NRZ.
        amplitude [Vpp] can be set in range 0.2 - 1
        '''

        if amp > 1 or amp < 0.2:
            raise RuntimeError("Amplitude out of range.")

        amp_to_write = int(amp*1e3)      #device accepts values in milivolts

        byte_list = bytearray([0x06])
        byte_list.extend(self._num_to_HiLo(amp_to_write))
        
        buf = self._mk_buf(byte_list)
        self.device.write(buf)
        self.amp = amp
    

    def set_offset(self, offs):
        '''
        Sets the offset of the outputs NRZ and /NRZ.
        offset [V] can be set in range from -0.5*amp to 0.5.
        '''
        if offs > 0.5 or offs < -0.5*self.amp:
            raise RuntimeError("Offset out of range.")
        
        offs_to_write = int(offs*1e3)      #device accepts values in milivolts

        if offs_to_write < 0: offs_to_write += 0x10000
        
        byte_list = bytearray([0x07])
        byte_list.extend(self._num_to_HiLo(offs_to_write))
        
        buf = self._mk_buf(byte_list)
        self.device.write(buf)
        self.offs = offs


    def set_16bit_pattern(self, patt):
        '''
        Changes the pattern_type to FW16 and updates output pattern to patt.
        Pattern corresponds to a binary number patt (1's - high voltage,
        0's -low).
        patt can be an integer from 0 to 65535 (0xffff). 
        '''
        self.set_pattern_type(4)
        self.pattern_type = 4

        patt = patt%0x10000 #if pattern is longer than 16bit, only last 16bits are used
        patt_0, patt_1 = self._num_to_HiLo(patt)

        byte_list = bytearray([0x1e, 0x02])
        byte_list.append(self._reverse_bits(patt_0))
        byte_list.append(self._reverse_bits(patt_1))
        
        buf = self._mk_buf(byte_list)
        self.device.write(buf)
        
        
    def set_8Mbit_pattern(self, patt_array, start_with = 0):
        '''
        patt_array = (A_1,A_2,A_3,A_4,...) sets the pattern. A_1, A_2 are
        numbers of ones and zeros. A_1 is number of zeros (ones), if the
        start_with is set to 0 (1). 
        sum of patt_array have to be from range(3*16,524288*16)
        '''
        if sum(patt_array) > 8388608 or sum(patt_array) < 48:
            raise RuntimeError('Invalid length of the pattern array!')
        
        if not (start_with == 0 or start_with == 1):
            raise RuntimeError("Unsupported parameter.")

        self.set_pattern_type(5)
        self.pattern_type = 5
        #from patt_array create a list of ones and zeros
        bit_list = []

        bit = int(start_with)
        for num in patt_array:
            bit_list.extend([bit] * num)
            bit = (bit+1)%2              #1 -> 0 or 0 -> 1

        #append n_bits_to_add so the seq. is divisible by 16 (one word is 16bit)
        seq_len = sum(patt_array)
        if not seq_len%16 == 0:
            n_bits_to_add = 16 - seq_len%16
            bit_list.extend([bit] * n_bits_to_add) 

        #create bytes from data bits
        #the bits have to be fed in reversed order
        data_byte_list = bytearray()
        for i in range(len(bit_list)/8):
            data_byte = bit_list[8*i]  * 0b00000001 + \
                        bit_list[8*i+1]* 0b00000010 + \
                        bit_list[8*i+2]* 0b00000100 + \
                        bit_list[8*i+3]* 0b00001000 + \
                        bit_list[8*i+4]* 0b00010000 + \
                        bit_list[8*i+5]* 0b00100000 + \
                        bit_list[8*i+6]* 0b01000000 + \
                        bit_list[8*i+7]* 0b10000000
            data_byte_list.append(data_byte)
            
        #byte to be fed into device
        byte_list = bytearray([0x1f])

        #append L3 (most significant),L2,L1,L0 (least significant) to byte_list.
        #Min. 3, max 524288. It is made from len(data_byte_list)/2 - number of
        #words (NOT BYTES!!) to send
        len_of_word_list = len(data_byte_list)/2
        len_byte_L3, len_byte_L2 = self._num_to_HiLo(len_of_word_list/0x10000)
        len_byte_L1, len_byte_L0 = self._num_to_HiLo(len_of_word_list%0x10000)

        byte_list.extend(bytearray([
            len_byte_L3, len_byte_L2, len_byte_L1, len_byte_L0
            ]))

        byte_list.extend(data_byte_list)

        buf = self._mk_buf(byte_list)
        self.device.write(buf)

    def _reverse_bits(self, patt):
        '''
        Switches the order of bits in the pattern
        (0th<->7th; 1st<->6th; 2nd<->5th; 3rd<->4th)
        '''
        a = patt
        a7 = a/0b10000000
        a6 = (a-a7*0x80)/0b1000000   
        a5 = (a-a7*0x80-a6*0x40)/0b100000
        a4 = (a-a7*0x80-a6*0x40-a5*0x20)/0b10000
        a3 = (a-a7*0x80-a6*0x40-a5*0x20-a4*0x10)/0b1000
        a2 = (a-a7*0x80-a6*0x40-a5*0x20-a4*0x10-a3*0x08)/0b100
        a1 = (a-a7*0x80-a6*0x40-a5*0x20-a4*0x10-a3*0x08-a2*0x04)/0b10
        a0 = a-a7*0x80-a6*0x40-a5*0x20-a4*0x10-a3*0x08-a2*0x04-a1*0x02

        return a0*0x80+a1*0x40+a2*0x20+a3*0x10+a4*0x08+a5*0x04+a6*0x02+a7
   
    
