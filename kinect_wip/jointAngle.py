'''
Created on Dec 31, 2014

@author: srick
'''

import csv
import Tkinter
import tkFileDialog
import numpy as np
import math
import os


def dotProduct(A,B):
    #print 'inside dp'
    total = 0.0
    for i in range(len(B)):
        #print A[i],B[i]
        total += (A[i]*B[i])
    return total


def magnitude(x):
    #print 'inside magnitude'
    inside = 0.0
    for i in range(len(x)):
        inside += x[i]**2
    return np.sqrt(inside)


def calculateAngles(filepath):
    headerRow = True
    savename = os.path.splitext(filepath)[0]+"_jointAngles.csv"
    with open(filepath, 'rUb') as kinectCSV, open(savename,'wb') as writeCsv:
        csvWriter = csv.writer(writeCsv)
        csvReader = csv.reader(kinectCSV)
        for row in csvReader:
            if headerRow:
                header=row
                outHeader = ["Time",
                             "LeftShoulder-LeftElbow Angle",
                             "LeftElbow-LeftWrist Angle",
                             "RightShoulder-RightElbow Angle",
                             "RightElbow-RightWrist Angle"]
                csvWriter.writerow(outHeader)
                #print header
                headerRow=False
            else:
                tempHolder = [row[0]]
                print ''
                print row[0]
                #print row[1:]
                try:
                    shoulderCenter=[float(row[7]),float(row[8]),float(row[9])]#7,8,9
                except:
                    shoulderCenter=None
                try:
                    shoulderLeft=[float(row[13]),float(row[14]),float(row[15])]#13,14,15
                except:
                    shoulderLeft=None
                try:
                    shoulderRight=[float(row[25]),float(row[26]),float(row[27])]#25,26,27
                except:
                    shoulderRight=None
                try:
                    elbowRight=[float(row[28]),float(row[29]),float(row[30])]#28,29,30
                except:
                    elbowRight=None
                try:
                    elbowLeft=[float(row[16]),float(row[17]),float(row[18])]#16,17,18
                except:
                    elbowLeft=None
                try:
                    wristRight=[float(row[31]),float(row[32]),float(row[33])]#31,32,33
                except:
                    wristRight=None
                try:
                    wristLeft=[float(row[19]),float(row[20]),float(row[21])]#19,20,21
                except:
                    wristLeft=None
                
                if shoulderLeft is not None and shoulderCenter is not None:
                    leftShoulderVec = [shoulderLeft[0]-shoulderCenter[0],
                                       shoulderLeft[1]-shoulderCenter[1],
                                       shoulderLeft[2]-shoulderCenter[2]
                    ]
                else:
                    leftShoulderVec=None
                if elbowLeft is not None and shoulderLeft is not None:
                    leftElbowVec = [elbowLeft[0]-shoulderLeft[0],
                                    elbowLeft[1]-shoulderLeft[1],
                                    elbowLeft[2]-shoulderLeft[2]
                    ]
                else:
                    leftElbowVec=None
                if wristLeft is not None and elbowLeft is not None:
                    leftWristVec = [wristLeft[0]-elbowLeft[0],
                                    wristLeft[1]-elbowLeft[1],
                                    wristLeft[2]-elbowLeft[2]
                    ]
                else:
                    leftWristVec=None
                if shoulderRight is not None and shoulderCenter is not None:
                    rightShoulderVec = [shoulderRight[0]-shoulderCenter[0],
                                       shoulderRight[1]-shoulderCenter[1],
                                       shoulderRight[2]-shoulderCenter[2]
                    ]
                else:
                    rightShoulderVec=None
                if elbowRight is not None and shoulderRight is not None:
                    rightElbowVec = [elbowRight[0]-shoulderRight[0],
                                    elbowRight[1]-shoulderRight[1],
                                    elbowRight[2]-shoulderRight[2]
                    ]
                else:
                    rightElbowVec=None
                if wristRight is not None and elbowRight is not None:
                    rightWristVec = [wristRight[0]-elbowRight[0],
                                    wristRight[1]-elbowRight[1],
                                    wristRight[2]-elbowRight[2]
                    ]
                else:
                    rightWristVec=None
                                   
                angleVectors=[
                              ["leftShoulderVec","leftElbowVec"],
                              ["leftElbowVec","leftWristVec"],
                              ["rightShoulderVec","rightElbowVec"],
                              ["rightElbowVec","rightWristVec"]
                ]
                for pair in angleVectors:
                    if locals()[pair[0]] is not None and locals()[pair[1]] is not None:
                        print ''
                        aVec=locals()[pair[0]]
                        bVec=locals()[pair[1]]
                        print aVec,bVec
                        dp = dotProduct(aVec,bVec)
                        print 'dp',dp
                        magA = magnitude(aVec)
                        magB = magnitude(bVec)
                        preCos = dp/(magA*magB)
                        print 'preCos',preCos
                        rads = math.acos(preCos)
                        degs = math.degrees(rads)
                        print pair[0],'->',pair[1],':',degs
                        tempHolder.append(degs)
                    else:
                        print pair[0],'and/or',pair[1],'missing'
                        tempHolder.append("")
                csvWriter.writerow(tempHolder)
    return


def main():
    root = Tkinter.Tk()
    root.withdraw()
    filepath = tkFileDialog.askopenfilename()
    calculateAngles(filepath)
    

main()

