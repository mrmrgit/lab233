import os
'''
Module for plotting measurement data during measurement.

When instance of PyGNUplot is created, it writes a script for GNUPLOT which
is then run by function "start_plot()" (Only once after first data were saved,
e.g. in first iteration of the measurement loop). GNUPLOT then every time
interval specified by parameter "pause" rereads itself, replots data and
save current figure if "savefig" is  set to True.

Matus Rehak
...
Last update: 14.12.2015
'''
class PyGnuplot(object):
    def __init__(self,
                 plotfile_name,
                 number_of_rows,
                 number_of_columns,
                 title,
                 plots,
                 pause = 1.0,
                 savefig = True,
                 file_path = ''):
        '''
        plotfile - string without extension, .gnu is added automatically
        pltofile_name.gnu - source file for gnuplot for creation of the plot

        number_of_rows,number_of_columns - number rows and columns of plots,
        number_of_rows * number_of_columns = number of graphs

        title - title on top of the window

        Plot settings:
        plot1 = (datafile_name,     #with extension .dat or .tmp!!!!
            x_columns,              #number (*) of column in datafile (1-based) corresponding to x-data
            y_columns,              #number (*) of column in datafile (1-based) corresponding to y-data
            xlabel,                 #string describing the x-axis
            ylabel,                 #string describing the x-axis
            subtitle,               #string (*) describing the graph
            markers)                #either 'line' or 'point' 
        ...
        plots = (plot1,plot2,plot3,...)
        
        pause - time interval Gnuplot waits before the window is reread again
        
        file_path - path to the data file from which to get data for plots
        .gnu, .png and .dat file will be in the same folder!!!

        DON'T FORGET TO USE DOUBLE BACKSLASH '\\' WHEN SAVING IN SUBFOLDERS (WINDOWS)!

        * - if plotting multiple lines into same graph, this is a list of
        numbers in case of x_ and y_columns and list of strings in case of
        markers. If only one string is used, each line in the graph is
        plotted that way - line or point
        '''
        self.file_path = file_path
        self.plotfile_name = plotfile_name
        
        if not len(plots) == number_of_rows*number_of_columns:
            raise RuntimeError(
                """number of plots is not equal to number """
                """of rows times number of columns"""
                )
        
        if file_path and (not os.path.exists(file_path)):
            os.makedirs(file_path)
            
        # create list of GNUPLOT commands
        # GNUPLOT documentaion:
        # http://www.gnuplot.info/documentation.html
        line_list = []
        
        multiplot_list = [
            'set multiplot layout %i,%i title "%s"'%(
                number_of_rows,
                number_of_columns,
                title
                ),
            'unset key'
            ]
        
        for plot in plots:
            multiplot_list.extend([
                'set xlabel "%s"' %plot[3],
                'set ylabel "%s"' %plot[4],
                'set title "%s"' %plot[5],
                self._plot_cmd_str(plot[0], plot[1], plot[2], plot[6]),
                ])
        
        multiplot_list.append('unset multiplot')
            
        if savefig:
            line_list.extend([
                'set term png',
                'set output "%s.png"'%(os.path.join(
                    file_path, plotfile_name).replace('\\','\\\\')
                                       )
                ])
            line_list.extend(multiplot_list)
            line_list.append('unset output ') 
        
        line_list.append('set term wxt')
        line_list.extend(multiplot_list)
        line_list.extend(['pause %f'%pause,'reread'])

        # create .gnu file filled with above commands:
        self.plotfile = open(os.path.join(file_path,plotfile_name+'.gnu'),'w')
        self._write_lines(line_list)
        self.plotfile.close()

    def __repr__(self):
        return '<GNUPLOT data visualization class >'
    
    def start_plot(self):
        '''
        start GNUPLOT as separate process and it will update plot automatically
        NOTE: you can use start_plot only when the source data file(s) for each
        plot is already created (datafilne_name.dat files).
        '''
        os.system('START wgnuplot '+os.path.join(
            self.file_path,self.plotfile_name+'.gnu')
                  )
            
    def _write_lines(self, line_list):
        for line in line_list:
            self.plotfile.write(line+'\n')

    def _add_marker_str(self,opt):
        '''
        returns string which specifies whether the data are plotted with
        lines or points.
        '''
        if opt.lower() == 'line':
            return 'with lines lw 2'
        elif opt.lower() == 'point':
            return 'with points pt 7 ps 1'
        else:
            raise RuntimeError('Invalid option. Either "line" or "point" can be used.')

    def _plot_cmd_str(self, file_name, x_columns, y_columns, markers):
        '''
        This function deals with the plotting part of gnuplot script.
        '''
        #this is case when there is only one set of data points to plot
        if (type(x_columns) == int) and (type(y_columns) == int) and (type(markers) == str):
            return 'plot "%s" using %i:%i %s'%(
                    os.path.join(self.file_path, file_name).replace('\\','\\\\'),
                    x_columns,
                    y_columns,
                    self._add_marker_str(markers)
                    )

        #this is case when there are mulitple sets of data points to plot
        elif hasattr(x_columns,'__iter__') and hasattr(y_columns,'__iter__'):
            if len(x_columns) == len(y_columns):

                #adding markers to the marker_list, so for each data set
                #has its own marker. If not specified, the marker is the
                #same as the first marker in the list of markers
                if type(markers) == str:
                    marker_list = [markers]*len(x_columns)
                else:
                    marker_list = markers[:]
                    while len(marker_list) < len(x_columns): marker_list.append(markers[0])

                #multiset plot is created like this (example):
                #plot "data.dat" using 1:2 with lines, "" using 1:3 with points, "" using 4:5 with points
                ret = 'plot "%s" ' %os.path.join(
                    self.file_path, file_name).replace('\\','\\\\')

                i = 0
                for x_c, y_c, mrkr in zip(x_columns, y_columns, marker_list):
                    if not i == 0: ret += '"" '
                    ret += 'using %i:%i %s, '%(
                        x_c,
                        y_c,
                        self._add_marker_str(mrkr)
                        )
                    i += 1

                return ret
                    
            else:
                raise RuntimeError(
                    """number of x_ and y_columns must be equal, """
                    """markers can be either of the same length """
                    """as x_ and y_columns or single string""")
            
        else:
            raise RuntimeError(
                """both x_columns and y_columns have to be integers or """
                """lists of integers with same length"""
                )
