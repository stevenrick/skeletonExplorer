'''
Created on Oct 30, 2014

@author: srick
'''

import csv
import Tkinter, tkFileDialog, Tkconstants
import tkSimpleDialog
import os
from Tkinter import * 
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D


#globals
time=0.0
filepath=""
body=[]
filetext='Select bodyTracking.csv file'
filelabel=''
timelabel=''


def hms_to_seconds(tIn):
    tCells = tIn.split(':')
    if len(tCells) == 3:
        #has h:m:s
        return int(tCells[0]) * 3600 + int(tCells[1]) * 60 + float(tCells[2])
    else:
        if len(tCells) == 2:
            #has m:s
            return int(tCells[0]) * 60 + float(tCells[1])
        else:
            #has s
            return float(tCells[0])


def drawSkeleton(body):
    fig=plt.figure()
    ax=fig.add_subplot(111, projection='3d')
    '''
    -draws scatter plot of joints
    -requires that joints be a list of 3 dimensional arrays in the following order:
    head, shoulderCenter, shoulderLeft, elbowLeft, wristLeft, handLeft,
    shoulderRight, elbowRight, wristRight, handRight, spine, hipCenter,
    hipLeft, kneeLeft, ankleLeft, footLeft, hipRight, kneeRight, ankleRight, footRight
    This is passed in this format and order from grabTime
    -Takes joints and turns it into three arrays composed of x, y, and z values
    -zdir is what component to treat as z values
    -s is size of points
    -c is point color
    -depthshade dims farther points to give sensation of depth
    -color is color of line between joints
    '''
    xs=[]
    ys=[]
    zs=[]
    for point in body:
        #print point[0]
        if point[0] != None:
            xs.append(point[0])
            ys.append(point[1])
            zs.append(point[2])
    ax.scatter(xs, ys, zs, zdir=u'z', s=20, c=u'b', depthshade=False)
    bodyArray=["head","shoulderCenter","shoulderLeft","elbowLeft","wristLeft","handLeft",
                 "shoulderRight","elbowRight","wristRight","handRight","spine","hipCenter",
                 "hipLeft","kneeLeft","ankleLeft","footLeft","hipRight","kneeRight","ankleRight","footRight"]
    x = 0
    for joint in bodyArray:
        #print body[x][0]
        if body[x][0] != None:
            globals()[joint]=body[x]
#             print joint,globals()[joint]
        else:
            joint
#             print joint,'Empty'
        x+=1
    bonesArray=[["head","shoulderCenter"],["shoulderCenter","shoulderLeft"],["shoulderCenter","shoulderRight"],
                  ["shoulderLeft","elbowLeft"],["elbowLeft","wristLeft"],["wristLeft","handLeft"],
                  ["shoulderRight","elbowRight"],["elbowRight","wristRight"],["wristRight","handRight"],
                  ["shoulderCenter","spine"],["spine","hipCenter"],["hipCenter","hipLeft"],["hipCenter","hipRight"],
                  ["hipLeft","kneeLeft"],["kneeLeft","ankleLeft"],["ankleLeft","footLeft"],
                  ["hipRight","kneeRight"],["kneeRight","ankleRight"],["ankleRight","footRight"]]
    for bone in bonesArray:
        #print bone
        #print bone[0],globals()[bone[0]],(globals()[bone[0]])[0],(globals()[bone[0]])[1],(globals()[bone[0]])[2]
        #print bone[1],globals()[bone[1]]
        try:
            ax.plot([(globals()[bone[0]])[0],(globals()[bone[1]])[0]],
                [(globals()[bone[0]])[1],(globals()[bone[1]])[1]],
                [(globals()[bone[0]])[2],(globals()[bone[1]])[2]], color=u'r')
        except:
            bone
    xmin,xmax=ax.get_xlim()
    ymin,ymax=ax.get_ylim()
    zmin,zmax=ax.get_zlim()
    ax.set_ylim([ymin-2,ymax+2])
    fig.show()


def getDataAtTime(dataFile,time):
    timeArray=[]
    headerRow=True
    with open(dataFile, 'rUb') as kinectCSV:
        csvReader = csv.reader(kinectCSV)
        for row in csvReader:
            if headerRow:
                row
                #print row[1:]
                headerRow=False
            else:
                timeArray.append(hms_to_seconds(row[0]))
        closest = (min(enumerate(timeArray), key=lambda x: abs(x[1]-time)))[1]
        #print closest
    headerRow = True
    with open(dataFile, 'rUb') as kinectCSV:
        csvReader = csv.reader(kinectCSV)
        for row in csvReader:
            if headerRow:
                row
                headerRow=False
            else:
                if hms_to_seconds(row[0]) == closest:
                    raw = row[1:]
    rawToJoints = [(9,10,11),(6,7,8),(12,13,14), #head,shoulderCenter,shoulderLeft
                   (15,16,17),(18,19,20),(21,22,23), #elbowLeft,wristLeft,handLeft
                   (24,25,26),(27,28,29),(30,31,32), #shoulderRight,elbowRight,wristRight
                   (33,34,35),(3,4,5),(0,1,2), #handRight,spine,hipCenter
                   (36,37,38),(39,40,41),(42,43,44), #hipLeft,kneeLeft,ankleLeft
                   (45,46,47),(48,49,50),(51,52,53), #footLeft,hipRight,kneeRight
                   (54,55,56),(57,58,59)] #ankleRight,footRight
    for xyz in rawToJoints:
        if raw[(xyz[0])] != "":
            body.append((10*float(raw[xyz[0]]),10*float(raw[xyz[2]]),10*-float(raw[xyz[1]])))
        else:
            body.append((None,None,None))
    #print body
    return


def openFile():
    global filepath
    global filetext
    global filelabel
    filepath = tkFileDialog.askopenfilename(title=filetext)
    filename = os.path.basename(filepath)
    filelabel.set(str(filename)+" Loaded")


def setTime():
    global time
    global timelabel
    time = float(tkSimpleDialog.askfloat("Time Input", "Input time point in data to draw skeleton for (in seconds)")) 
    timelabel.set(str(time))


def prepDraw():
    global filepath
    global time
    global body
#     print filepath
#     print time
    plt.close()
    body = []
    getDataAtTime(filepath,time)
    drawSkeleton(body)


def main():
    global filetext
    global filelabel
    global timelabel
    timetext= 'Select a time'
    root = Tk()
    root.title('Skeleton Explorer')
    button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}
    
    filebut = Button(root, text = filetext, fg = 'black', command= openFile)
    filebut.pack()
    filelabel = StringVar()
    filelabel.set("No File Loaded")
    Label(root, textvariable=filelabel).pack()
    
    dirbut= Button(root, text = timetext, fg = 'black', command= setTime)
    dirbut.pack()
    timelabel = StringVar()
    timelabel.set("No Time Specified")
    Label(root, textvariable=timelabel).pack()
    
    drawbut = Button(root, text = "Draw Skeleton", fg = 'black', command=prepDraw)
    drawbut.pack()
    
    root.mainloop()


main()

