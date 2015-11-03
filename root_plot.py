from ROOT import TCanvas, TGraph, TLatex, TPad, gROOT,  gStyle
import os
from array import array
'''
example usage:
from lab.root_plot import *
plt=Plot(['1','2'],['x1','x2'],['y1','y2'],Ncolumns=2,meas='measurement')
plt.add_point(0,1,1)
plt.add_point(1,1,1)
plt.save_fig('meas1','measurements/new_meas')

Last update: 5.8.2015
'''
class Plot:
   def __init__(self,Title,XTitle,YTitle,meas='',size_x=1500,size_y=600,Nrows=1,Ncolumns=1,grid=True):
      '''
      Title, XTitle, YTitle - list of strings with length Nrows*Ncolumns
      meas - string, name of the measurement
      '''
      gROOT.Reset()
      gStyle.SetTitleSize(0.05,"x")    #font size of X titles
      gStyle.SetTitleSize(0.05,"y")    #font size of Y titles
      gStyle.SetTitleSize(0.05,"t")    #font size of plot titles

      self.c = TCanvas( 'c', 'ROOT plot', 0, 0, size_x, size_y )
      self.c.SetFillColor(0)
      
      if (len(Title)!=Nrows*Ncolumns) or (len(Title)!=Nrows*Ncolumns) or (len(Title)!=Nrows*Ncolumns):
         raise IndexError('list of Titles must have same length as Nrows*Ncolumns!')

      self.meas=meas
      self.XTitle=XTitle
      self.YTitle=YTitle
      self.Title=Title
      self.it=[0]*(Nrows*Ncolumns)        #iterator list for each plot in canvas
      self.p=[]                           #list of plots (pads)
      self.gr=[]                          #list of graphs
      self.lims=[]
      #This loop generates Ncolumns*Nrows pads (plots) for graphs.
      #Pads are generated from bottom left corner (i=0) to top
      #right corner (i=Ncolumns*Nrows-1) on the 100% * 90% of the 
      #canvas, top 100% * 90% of canvas is a pad with
      #the title of the measurement - "meas" string.
      M,N=float(Ncolumns),float(Nrows)
      for i in range(Nrows*Ncolumns):
         self.p.append(TPad('p%i'%i , 'p%i'%i , i%M/M, (i//M)/N*0.9 , i%M/M+1./M , ((i//M+1)/N*0.9 ) ))
         if grid: self.p[i].SetGrid()
         self.p[i].Draw()
         self.gr.append([]) #prepare for following adding of graphs
         self.lims.append([0,1,0,1])#default axis limits: xmin,xmax,ymin,ymax
      self.p.append(TPad('p%i'%(Nrows*Ncolumns),'p%i'%(Nrows*Ncolumns),0.0,0.9,1.0,1.0))#title Pad
      self.p[-1].Draw()
  
      #meas pad   
      self.p[-1].cd()
      self.ct=TLatex(0.05,0.25,meas)
      self.ct.SetTextSize(0.3)#0.5 0.2 - male
      self.ct.Draw()

      self.c.Update()

   def _add_graph(self,i,grp_type,color=4,data=[]):
      '''
      grp_type=P plot points
      grp_type=L plot lines
      '''
      self.p[i].cd()
      if data==[]:
         self.gr[i].append(TGraph( ))
      else:
         self.gr[i].append(TGraph(data[0],data[1],data[2] ))
      self.gr[i][-1].SetMarkerColor( color )
      self.gr[i][-1].SetMarkerStyle(20)
      self.gr[i][-1].SetTitle(self.Title[i])
      self.gr[i][-1].GetXaxis().SetTitle(self.XTitle[i])
      self.gr[i][-1].GetYaxis().SetTitle(self.YTitle[i])
      if len(self.gr[i])==1:
         self.gr[i][-1].Draw('A'+grp_type)
      else:
         self.gr[i][-1].Draw(grp_type)
         
   def _set_ranges(self,i,lims):
      '''
      set the limits on x and y axis in i-th pad (plot).
      It is necessary to set axis ranges if there are more graphs in single pad.
      So this function is used in add_points() and plot_arrays(). In case there
      is only single graph in a pad, ROOT autoscales it correctly.
      '''
      xmin,xmax,ymin,ymax=lims
      self.p[i].cd()
      self.gr[i][0].GetXaxis().SetLimits(xmin,xmax)
      self.gr[i][0].GetYaxis().SetRangeUser(ymin,ymax)#kokotina vyjebana SetLimits() nefunguje pre YAxis
      
   def add_point(self,i,x,y):
      '''
      Adds single point (x,y) to i-th plot.
      For adding more than one point use plot_array().
      '''
      self.p[i].cd()
      
      if self.it[i]==0: self._add_graph(i,'P')

      self.gr[i][0].SetPoint(self.it[i],x,y)
      self.gr[i][0].GetXaxis().SetTitle(self.XTitle[i])  #ROOT bug, after you add a point, ROOT erases X,Y titles
      self.gr[i][0].GetYaxis().SetTitle(self.YTitle[i])  #ROOT bug, after you add a point, ROOT erases X,Y titles
      self.c.Update()
      self.it[i]+=1

   def add_points(self,i,x_list,y_list):
      '''
      Adds multiple points (x_list,y_list) to i-th plot.
      For adding single point use add_point().
      '''
      self.p[i].cd()
      j=0

      if self.it[i]==0:
         self.lims[i]=[min(x_list),max(x_list),min(y_list),max(y_list)]
      else:
         self.lims[i]=[min(self.lims[i][0],min(x_list)),\
                       max(self.lims[i][1],max(x_list)),\
                       min(self.lims[i][2],min(y_list)),\
                       max(self.lims[i][3],max(y_list))]
      
      for x,y in zip(x_list,y_list):
         if self.it[i]==0: self._add_graph(i,'P',color=j+1)

         self.gr[i][j].SetPoint(self.it[i],x,y)
         self._set_ranges(i,self.lims[i])  # 
         self.gr[i][j].GetXaxis().SetTitle(self.XTitle[i])  #ROOT bug, after you add a point, ROOT erases X,Y titles
         self.gr[i][j].GetYaxis().SetTitle(self.YTitle[i])  #ROOT bug, after you add a point, ROOT erases X,Y titles
         j+=1
      self.c.Update()
      self.it[i]+=1
      
   def save_fig(self,name,path=''):
      '''
      path without extension
      Saves only .gif format
      '''
      if path!='':
         cur_dir=os.getcwd()
         if not os.path.exists(path):
            os.makedirs(path)
         os.chdir(path)   
         self.c.SaveAs(name+'.gif')
         os.chdir(cur_dir)
      else:
         self.c.SaveAs(name+'.gif')

   def plot_array(self,i,x_list,y_list):
      '''
      Adds whole trace (x_list, y_list) to i-th plot.
      x_list and Y_list have to be arrays of the same length
      '''
      x_array, y_array = array( 'd' ), array( 'd' )

      for x,y in zip(x_list,y_list):
         x_array.append(x)
         y_array.append(y)
      
      self.p[i].cd()
      if self.gr[i]==[]: self._add_graph(i,'L')
      self.gr[i][0].Clear()
      self.gr[i][0]=TGraph(len(x_list),x_array,y_array)
      self.gr[i][0].SetLineWidth( 4 )
      self.gr[i][0].GetXaxis().SetTitle(self.XTitle[i])  
      self.gr[i][0].GetYaxis().SetTitle(self.YTitle[i])
      self.gr[i][0].SetTitle(self.Title[i])
      self.gr[i][0].Draw('AL')
      self.c.Update()
      
   def plot_arrays(self,i,x_lists,y_lists):
      '''
      Adds whole traces (x_lists, y_lists) to i-th plot.
      x_lists and y_lists have to be arrays of arrays of the same length
      e.g. x_lists = [[1,2,3],[1,2,3],[1,2,3]] and y_lists = [[5,6,7],[15,12,9],[0.1,0.2,0.3]]
      '''
      xmin = min([min(x) for x in x_lists])#
      xmax = max([max(x) for x in x_lists])#
      ymin = min([min(y) for y in y_lists])#
      ymax = max([max(y) for y in y_lists])#
         
      j=0
      self.p[i].cd()
      for x_list, y_list in zip(x_lists,y_lists):
         x_array, y_array = array( 'd' ), array( 'd' )

         for x,y in zip(x_list,y_list):
            x_array.append(x)
            y_array.append(y)
         if len(self.gr[i])<=j: self._add_graph(i,'L')
         self.gr[i][j].Clear()
         
         #self._add_graph(i,'L', data=[len(x_list),x_array,y_array])    
         self.gr[i][j]=TGraph(len(x_list),x_array,y_array)
         self.gr[i][j].SetLineColor(j+1)
         self.gr[i][j].SetLineWidth( 4 )
         
         if j==0:
            self.gr[i][j].Draw('AL')
         else:
            self.gr[i][j].Draw('L')
         
         j+=1
      self._set_ranges(i,[xmin,xmax,ymin,ymax])  # 
      self.gr[i][0].GetXaxis().SetTitle(self.XTitle[i])  
      self.gr[i][0].GetYaxis().SetTitle(self.YTitle[i])
      self.gr[i][0].SetTitle(self.Title[i])
      self.c.Update()



