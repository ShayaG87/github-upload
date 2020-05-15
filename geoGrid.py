from numpy import *
import math
from datetime import datetime



class geogrid:
    def __init__(self,points,ratio,average):
        self.points= array(points).astype(int64)
        self.ratio= ratio
        self.average= average
        self.num_points=len(points)
        self.min_max()
        self.rectangle_div()
        self.num_points=len(points)

    def min_max(self):
        self.x_min= self.points[:,0].min()
        self.x_max= self.points[:,0].max()
        self.y_min= self.points[:,1].min()
        self.y_max= self.points[:,1].max()
        return()

    def rectangle_div(self):
        self.hight = self.x_max-self.x_min                 # rectangle height
        self.length = self.y_max-self.y_min               # rectangle width
        self.num_cells = int(self.num_points/self.average)       # total amount of cells
        self.area = ((self.length * self.hight)/self.num_cells)     # area of cell
        self.cell_hight = math.sqrt(self.area*self.ratio)        # cell height
        self.cell_length = math.sqrt((self.area/self.ratio))      # cell width
        self.x_cells = int(self.hight/self.cell_hight)+1      #   nr cells on axis x
        self.y_cells = int(self.length/self.cell_length)+1        #  nr cells on axis y
        self.num_cells = self.x_cells*self.y_cells              #   total amount of cells (recalculation)

    def associate(self,x,y):        # returns lower left x,y of each cell (index)
        nX= int((x-self.x_min)/(self.cell_hight+0.1))
        nY= int((y-self.y_min)/(self.cell_length+0.1))
        return nX,nY

    def convert2D_1D(self,x,y):   # returns  1 dimensional index for each cell
        return (self.x_cells*y)+x

    def reg_search(self,point, radius):   #returns list of points in radius + search time
        point=point.split()
        pList = []
        time_start = datetime.now().microsecond / 1000
        for row in self.points:
            if ((row[0]-int(point[0]))**2+(row[1]-int(point[1]))**2) <= (int(radius))**2:
                pList.append(row)
        time_end = datetime.now().microsecond / 1000
        tot_time=round((time_end-time_start),8)
        time=("Time ellapsed: " + str(tot_time)+" [msec]")
        return pList,time

    def rect_search(self,point,radius):   # arranges irregularities created by radiuses exceeding the rectangle bounderies
        self.lower_left_x,self.lower_left_y= int(point[0])-int(radius),int(point[1])-int(radius)
        self.upper_right_x,self.upper_right_y=int(point[0])+int(radius),int(point[1])+int(radius)

        if self.lower_left_x<self.x_min:
            self.lower_left_x=self.x_min
        if self.lower_left_y<self.y_min:
            self.lower_left_y=self.y_min
        if self.upper_right_x>=self.x_max:
            self.upper_right_x=self.x_max
        if self.upper_right_y>self.y_max:
            self.upper_right_y=self.y_max













