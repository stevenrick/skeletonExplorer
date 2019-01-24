import matplotlib
matplotlib.use('TKAgg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# import tkFileDialog, Tkinter
# tk = Tkinter.Tk()
# tk.withdraw()
# filepath = tkFileDialog.askopenfilename()

class AnimatedScatter(object):
    def __init__(self):
        self.stream = self.data_stream()
        self.angle = 0

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111,projection = '3d')
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=50, 
                                           init_func=self.setup_plot, blit=True)

    def change_angle(self):
        self.angle = (self.angle + 0.5)%360

    def setup_plot(self):
        X = next(self.stream)
        c = ['b', 'r', 'g', 'y', 'm']
        self.scat = self.ax.scatter(X[:,0], X[:,1], X[:,2] , c=c, s=200, animated=True)
        
        xmin,xmax=self.ax.get_xlim()
        ymin,ymax=self.ax.get_ylim()
        zmin,zmax=self.ax.get_zlim()

        self.ax.set_xlim3d([xmin-2,xmax+2])
        self.ax.set_ylim3d([ymin-2,ymax+2])
        self.ax.set_zlim3d([zmin-2,zmax+2])

        return self.scat,

    def data_stream(self):
        data = np.zeros(( 5 , 3 ))
        #print 'data',data
        xyz = data[:,:3]
        #print 'xyz1',xyz
        while True:
            xyz += 2 * (np.random.random(( 5,3)) - 0.5)
            #print 'xyz2',xyz
            yield data

    def update(self, i):
        data = next(self.stream)
        #print 'updateData',data
        data = np.transpose(data)
        #print 'transposeData',data

        self.scat._offsets3d = ( np.ma.ravel(data[:,0]) , np.ma.ravel(data[:,0]) , np.ma.ravel(data[:,0]) )

        self.change_angle()
        self.ax.view_init(30,self.angle)
        plt.draw()
        return self.scat,

    def show(self):
        plt.show()

if __name__ == '__main__':
    a = AnimatedScatter()
    a.show()