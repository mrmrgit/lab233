'''
Data handling module.

Usage:

import lab233.meas_data
sett = {
	'current': 1e-4,			
	'voltage_range': 100e-3,
}
data= lab233.meas_data.Data('new_data','0.0')
data.fill_header('MoC',RT'')
data.write_settings(sett)
data.write_data([1,2,3,4,[0.5,0.6,0.7,0.8]])
data.fill_footer()
...
Matus Rehak
Last update: 10.12.2015
'''
import time
import os
from string import digits

class Data(object):
    def __init__(self,meas_name,specifier,file_path='',delimiter='\t'):
        '''
        Creates a data file with name meas_name+specifier . dat in
        file_path. Data are separated by delimiter.
        Specifier serves for distinguishing between the measurements.
        It is automatically increased if a file with the specific name
        already exists.
        
        meas_name, specifier - strings,
        delimiter - character for separation of data points
        '''
        self.delimiter = delimiter
        self.specifier = specifier

        if file_path and (not os.path.exists(file_path)):
            os.makedirs(file_path)
        
        self.file_name = os.path.join(file_path, meas_name + self.specifier)
        
        #if file already exists, this part of code increases specifier
        #or add ".0" at the end of the file name. Specifier ending by 9
        #is increased to 9.0
        while os.path.isfile(self.file_name+'.dat'):
            #if last char. of string is a number except 9
            if not self.specifier == '' and self.specifier[-1] in digits[:-1]: 
                ls = list(self.specifier)
                ls[-1] = str(int(ls[-1]) + 1)
                self.specifier = "".join(ls)
            else:
                self.specifier += '.0'

            self.file_name = os.path.join(file_path, meas_name + self.specifier)    
               
        data=open(self.file_name+'.dat','a')
        data.close()

    def __repr__(self):
        return '<Data file %s.dat>' %self.file_name

    def fill_header(self,sample, meas_type):
        '''
        Fills header of the data file.
        It add following lines: date, sample descriptions, mesaurement details
        '''
        data=open(self.file_name+'.dat','a')
        data.write('\n#DATE:\t\t%s\n' %time.ctime())     
        data.write('#SAMPLE:\t\t%s\n' %sample)
        data.write('#MEASUREMENT:\t%s\n' %meas_type)
        data.close()

    def fill_footer(self):
        '''
        Adds the time of the end of the measurement.
        '''
        data=open(self.file_name+'.dat','a')
        data.write('\n#END OF MEASUREMENT:\t\t%s\n' %time.ctime())
        data.write('\n\n#--------------------------------------------------------------------------')
        data.close()        
 
    def write_data(self, *data_list):
        '''
        Writes data to the file, single value or array (dim N*1) of values
        '''
        data=open(self.file_name+'.dat','a')
        for d in data_list:
            if hasattr(d,'__iter__'):
                for di in d:
                    data.write(str(di)+self.delimiter)
            else:
                data.write(str(d)+self.delimiter)
        data.write('\n')    
        data.close()
        
    def write_note(self,note):
        '''
        Writes a note to the file.
        '''
        data=open(self.file_name+'.dat','a')
        data.write('#%s\n'%note)
        data.close()

    def write_settings(self, dict_of_variables):
        '''
        Writes dictionary of settings to the file. If dictionary value is
        an iterable, it writes first value, last value ,its length and then
        all the values.
        '''
        data=open(self.file_name+'.dat','a')
        for k,v in dict_of_variables.iteritems():
            if hasattr(v,'__iter__'):
                data.write('#%s[0]=%s \t'%(k,v[0]))
                data.write('%s[-1]=%s \t'%(k,v[-1]))
                data.write('length %s=%s \t values: '%(k,len(v)))
                for v_i in v: data.write('%s \t'%v_i)
            else:
                data.write('#%s=%s \t'%(k,v))
            data.write('\n')
        data.close()
    
    def write_tmp_data(self, *data_list):
        '''
        Writes *data, which should be arrays (lists, tuples, numpy_arrays,..)
        of numbers. Length of the arrays should be equal. They are written 
        in a temporary file with the same name as the instance datafile,
         only the extension is not ".dat", but ".tmp"
        '''
        
        #check if the data arrays have the same length
        data_length = len(data_list[0])
        for d in data_list:
            if not len(d) == data_length:
                raise RuntimeError("Data arrays have to be of the same length")

        data=open(self.file_name+'.tmp','w')
        for i in range(data_length):
            for d in data_list:
                data.write(str(d[i]) + self.delimiter)
            data.write('\n')

        data.close()
        
