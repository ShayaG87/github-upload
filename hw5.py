from tkinter import *
from tkinter import filedialog, Listbox, END, Button, messagebox
import pyodbc
from geoGrid import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")


class App:
    def __init__(self, master):  #constuctor/ all the buttons and labels on the GUI and all the class variables.

        self.master=master
        self.master.title('users interface for parcel search')
        self.point = Label(text='point').grid(row=0,sticky=E)
        self.e1 = Entry()
        self.e1.grid(row=0, column=1)
        self.radius = Label(text='radius').grid(row=1,sticky=E)
        self.e2 = Entry()
        self.e2.grid(row=1, column=1)
        self.ratio = Label( text='ratio').grid(row=2,sticky=E)
        self.myRatio = Entry()
        self.myRatio.grid(row=2, column=1)
        self.averg = Label( text='average points in cell').grid(row=3, sticky=E)
        self.myAverage = Entry()
        self.myAverage.grid(row=3,column=1)
        self.var1 = IntVar()   # used to set the state of checkbox
        self.check1 = Checkbutton(variable=self.var1, command=self.changeChecks1).grid(row=4, column=1, sticky=W)
        self.search_a = Label(text='search all').grid(row=4,sticky=E)
        self.label_time1=Label()
        self.var1.set(1)
        self.var2 = IntVar()
        self.check2 = Checkbutton(variable=self.var2, command=self.changeChecks2).grid(row=5,column=1, sticky=W)
        self.search_b = Label( text='search by equal cells').grid(row=5, sticky=E)
        self.label_time2=Label()
        self.chooseButton = Button( text='Please choose database', fg='blue', command=self.choose).grid(row=6) # call choose function
        self.browseButton = Button( text='BROWSE', fg='black', command=self.browse).grid(row=6,column=1)     #  call to browse function
        self.quitButton = Button(text='Quit', fg='red', command=quit).grid(row=6,column=2)
        self.label_pnt=Label(master=self.master)
        self.label_rad=Label(master=self.master)
        self.label_rat=Label(master=self.master)
        self.label_ave=Label(master=self.master)
        self.label_db=Label(master=self.master)
        self.scrollbar = Scrollbar(master=self.master)
        self.listbox3=Listbox(master=self.master)
        self.pList = []
        self.fig, self.ax = plt.subplots()
        self.listbox1=Listbox(master=self.master)
        self.label_cells=Label()
        self.label_time=Label()
        self.cells = []
        self.new_cells=[]



    def check_entry(self,a,b,c,d):     #   checks all the entries if they're valid.
        a=str(a).split()
        try:
            int(a[0]),int(a[1])
        except ValueError:
            self.label_pnt = Label(text='enter valid point!', fg='red')
            self.label_pnt.grid(row=7,column=1 )
            return False
        try:
            int(b)
        except ValueError:
            self.label_rad = Label(text='enter valid radius!', fg='red')
            self.label_rad.grid(row=8,column=1 )
            return False
        try:
            float(c)
        except ValueError:
            self.label_rat = Label(text='enter vaild ratio!', fg='red')
            self.label_rat.grid(row=9,column=1 )
            return False
        try:
            int(d)
        except ValueError:
            self.label_ave = Label(text='enter valid average!', fg='red')
            self.label_ave.grid(row=10,column=1 )
            return False
        return True


    def changeChecks1(self):  #   swaps the state of checkboxes/
        if self.var1.get():
            self.var2.set(0)
        else:
            self.var2.set(1)

    def changeChecks2(self):#    swaps the state of checkboxes/
        if self.var2.get():
            self.var1.set(0)
        else:
            self.var1.set(1)

    def check_db(self):     #  ensure valid database
        try:
            self.conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + self.file)
        except Exception:
            messagebox.showerror( 'error',"please try again \n " )
            return False
        return True



    def choose(self):   #  creates instance of geogrid class
        if not self.check_entry(self.e1.get(),self.e2.get(),self.myRatio.get(),self.myAverage.get()):
            return
        self.label_pnt.destroy()
        self.label_rad.destroy()
        self.label_rat.destroy()
        self.label_ave.destroy()

        self.file = filedialog.askopenfilename(title="Select Microsoft Access database file",
                                          filetypes=[('Access Database files', '.mdb;.accdb')])

        if not self.check_db():
            return
        selection = ('select n,e,pntid from points')  # get all points coordinates from DB
        self.points_list = self.execution(selection)
        for row in self.points_list:   #  set selection format to string tuple
            row=str(row).split(',')

        self.myGeo = geogrid(self.points_list, float(self.myRatio.get()), int(self.myAverage.get())) # geogrid instance
        self.point_cells = [[] for _ in range(self.myGeo.num_cells)]
        for count, row in enumerate(self.points_list):
            nX, nY = self.myGeo.associate(row[0], row[1])
            convert = self.myGeo.convert2D_1D(nX, nY)
            self.point_cells[convert].append(row)  #  attach each point to its cell

    def browse(self):   #   decides which search to do
        if not self.check_entry(self.e1.get(),self.e2.get(),self.myRatio.get(),self.myAverage.get()):
            return
        if not self.check_db():
            return
        x = self.var1.get()
        y = self.var2.get()
        if x == 0 and y==1 :
            self.browse_equal()         # call equal cells search -function
        elif x==1 and y==0:
            self.browse_all()       #   call all points search -function


    def browse_all(self):
        self.pList,time=self.myGeo.reg_search(self.e1.get(), self.e2.get())
        self.calculation()
        self.listbox3 = Listbox(master=self.master, font='monospace', width=50, bg='green',xscrollcommand=self.scrollbar.set)
        self.listbox3.grid(row=9, rowspan=7, columnspan=3)
        self.label_time=Label(text=time,anchor=W,bg='purple',fg='yellow').grid(row=7, sticky=W)


    def browse_equal(self):
        my_point = self.e1.get().split()  #     set point to tuple ( makes search possible)
        self.myGeo.rect_search(my_point, self.e2.get())     #  ensures to search only whitin rectangle
        self.pList = []
        a,b=self.myGeo.associate(self.myGeo.lower_left_x,self.myGeo.lower_left_y)
        e,f=self.myGeo.associate(self.myGeo.upper_right_x, self.myGeo.upper_right_y)
        time_start = datetime.now().microsecond / 1000
        for i in range(a,e+1):  #  start 2 dimensional search. i runs vertical
            for j in range(b,f+1):  #  j runs horizontal
                k = self.myGeo.convert2D_1D(i,j)
                for new_point in self.point_cells[k]:  # checks all points in particular cell
                    if ((int(new_point[0]) - int(my_point[0])) ** 2 + (int(new_point[1]) - int(my_point[1])) ** 2) <= (int(self.e2.get())) ** 2:
                        self.pList.append(new_point)    #   list with all points in radius
        time_end = datetime.now().microsecond / 1000
        tot_time=round((time_end-time_start),8)
        time=("Time ellapsed: " + str(tot_time)+" [msec]")
        for i in range(a,e+1):   #   re-run loop (outside of time measurement) in order to get coordinates of cells that contain points
            for j in range(b,f+1):
                k = self.myGeo.convert2D_1D(i,j)
                for new_point in self.point_cells[k]:
                    if ((int(new_point[0]) - int(my_point[0])) ** 2 + (int(new_point[1]) - int(my_point[1])) ** 2) <= (int(self.e2.get())) ** 2:
                        '''
                        coordinates of cells containg points
                        '''
                        self.cells.append([[self.myGeo.y_min+(j*self.myGeo.cell_length),self.myGeo.x_min+(i*self.myGeo.cell_hight)],
                                           [self.myGeo.y_min+((j+1)*self.myGeo.cell_length),self.myGeo.x_min+(i*self.myGeo.cell_hight)],
                                           [self.myGeo.y_min+((j+1)*self.myGeo.cell_length),self.myGeo.x_min+((i+1)*self.myGeo.cell_hight)],
                                           [self.myGeo.y_min+(j*self.myGeo.cell_length),self.myGeo.x_min+((i+1)*self.myGeo.cell_hight)]])

        self.calculation()     #   call function that gets parcels
        self.lstbx3()
        self.label_time = Label(text=time,anchor=W,bg='purple',fg='yellow').grid(row=7, sticky=W)

    def lstbx3(self):   #  creates new listbox with list of cells and points in them
        self.listbox3 = Listbox(master=self.master, font='monospace', width=50, bg='green', xscrollcommand=self.scrollbar.set)
        self.listbox3.grid(row=9, rowspan=6,columnspan=3)
        for count, row in enumerate(self.point_cells):
            self.listbox3.insert(END,count, row)
            x = count
        self.label_cells = Label(text='The amount of cells is: ' + str(x) + '.  and the points in them are:').grid(row=8)

    def calculation(self):      #   gets parcels
        parcel_list=[]
        new_prcList=[]
        for row in self.pList:
            pntId=str(row[2])
            selection = ("select distinct Parcel.parcelName, Block.blockID , Block.blockName from Block,Parcel,(select polyID from PartOf where pntID = " + pntId + " ) where Parcel.polyID = PartOf.polyID and Block.blockID=Parcel.blockID ")
            parcel_list.append(self.execution(selection))    #   list with all parcelsnames, blockId and blockname

        for row in parcel_list:
            if not row:
                continue
            for item in row:
                newItem=(str(item[0]).strip(), str(item[1]).strip(), str(item[2]).strip())
                new_prcList.append(newItem)
        len_max = 3
        for row in new_prcList:
            if len('  '+row[0]+' '+row[1]+' '+ ' '+row[2]+'  ') > len_max:
                len_max = len('  '+row[0]+' '+row[1]+' '+ ' '+row[2]+'  ')
        set(new_prcList)
        out = set([i for i in new_prcList])    #   loop over list in order to remove duplicates
        self.header= Label(text=' ParcelName         BlockID            BlockName').grid(row=0, column=3)
        self.listbox1 = Listbox( master=self.master, font='monospace', selectmode=single, width= len_max, bg='blue',  fg='white')
        self.listbox1.grid(row=1, rowspan=5, column=3,columnspan=4)
        for row in out:
            self.listbox1.insert(END, (row[0],"  |  ",row[1]," | ",row[2]))

        for i in self.cells:
            cell=plt.Polygon(i,fill=False,color='grey')    #plot cells containing points in radius
            self.ax.add_patch(cell)
        self.get_parcel()  # call function to plot parcels
        self.plot_circle(self.e1.get(), self.e2.get())  #  call function to plot circle and point

        self.listbox1.bind('<<ListboxSelect>>', lambda event: self.CurSelect())

    def CurSelect(self):   #  read selection of item in listbox
        value = self.listbox1.get(self.listbox1.curselection())
        blockID=value[2]
        selection = ("SELECT area, Block.planID, MutationPlan.surveyID FROM MutationPlan, Polygon,  Block WHERE Block.blockID = " + blockID + "  AND Block.polyID = Polygon.polyID AND Block.planID = MutationPlan.planID")
        selection = self.execution(selection)
        for item in selection:
            newItem = (str(item[0]).strip(), str(item[1]).strip(), str(item[2]).strip())
        self.label_surv=Label(master=self.master,text='area                       planID              surveyor')
        self.label_surv.grid(row=7,column=3)
        self.listbox2 = Listbox(master=self.master, font='monospace',width= len(newItem[0]+newItem[1]+newItem[2]), bg='yellow')
        self.listbox2.grid(row=8, rowspan=5, column=3)
        self.listbox2.insert(END, newItem)
        parcelName = value[0]     #   variable gets parcelname in order to search vertexes coordinates
        selection2 = ("SELECT E, N FROM Points, (SELECT  pntID, pntOrder FROM PartOf,(SELECT  polyID FROM Parcel WHERE parcelName = '" + parcelName + "'AND blockID =" + blockID + ')WHERE Parcel.polyID = PartOf.polyID) WHERE Points.pntID = PartOf.pntID ORDER BY pntOrder')
        selection2 = self.execution(selection2)
        my_parcel2 = plt.Polygon(selection2, fill=True, color='blue')  #  plot selected parcel in blue color
        self.ax.add_patch(my_parcel2)
        self.fig.show()

    def execution(self, selection):
        self.cursor = self.conn.cursor()
        self.cursor.execute(selection)
        self.f_list = self.cursor.fetchall()
        return self.f_list         #   return sql query

    def plot_circle(self,point,radius):
        point=point.split()
        x = (int(point[1]),int(point[0]))
        r = int(radius)
        my_circle = plt.Circle(x,  r, fill = False)       #  plot circle
        self.ax.add_patch(my_circle)
        plt.scatter(x[0],x[1])        #  plot point
        self.fig.show()

    def get_parcel(self):
        rectangle=[[self.myGeo.y_min,self.myGeo.x_min],
                   [self.myGeo.y_max,self.myGeo.x_min],
                   [self.myGeo.y_max,self.myGeo.x_max],
                   [self.myGeo.y_min,self.myGeo.x_max]]                #   vertexes coordinates of rectangle
        rect = plt.Polygon(rectangle,fill=False,color='brown')     #  plot rectangle
        self.ax.add_patch(rect)

        polygs=[]
        for point in self.pList:
            my_point = str(point[2])
            selection = ('SELECT N, E, polyID FROM Points,(SELECT pntOrder, pntID AS selectpolyid, polyID FROM PartOf, (SELECT  PartOf.polyID AS selectpoly FROM PartOf, Parcel WHERE pntID = ' + my_point + 'AND Parcel.polyID = PartOf.polyID) WHERE polyID =  selectpoly) WHERE Points.pntID = selectpolyid ORDER BY polyID,pntOrder')
            parcels = self.execution(selection)     #   get coordinates of parcel vertexes- ordered
            polygs.append(parcels)
        new_polygs=[]
        now_polygs=[]
        for i in polygs:
            new_polygs.extend(i)       #  extend lists to one long list
        for i in new_polygs:
            tup = (i[0], i[1], i[2])
            now_polygs.append(tup)
        my_parcels=[]
        for i in now_polygs:       #    loop to remove duplicates
            if i not in my_parcels:
                my_parcels.append(i)
        new_parc = []
        p = 0
        j = 0
        i = my_parcels[0][2]
        while p <= len(my_parcels):
            while my_parcels[j][2]==i:
                new_parc.append([my_parcels[j][1],my_parcels[j][0]])   #  list "new_parc" gets lists of coordinates in order to plot them
                if j == (len(my_parcels)-1):
                    break
                j+=1
            my_parcel = plt.Polygon(new_parc, fill=False, color='red')
            self.ax.add_patch(my_parcel)

            if j == (len(my_parcels) - 1):
                break
            new_parc = []  # empty the list to get new parcel coordinates
            p = j
            i = my_parcels[j][2]



root = Tk()

app = App(root)

root.mainloop()

