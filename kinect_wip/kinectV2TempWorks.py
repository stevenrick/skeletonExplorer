'''
Created on Apr 10, 2015

@author: rick
'''

import os
import csv
import re
import fnmatch
import Tkinter, tkFileDialog


root = Tkinter.Tk()
root.withdraw()

globalStartTime=0


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


def hms_to_seconds_custom(tIn):
    tCells = tIn.split('-')
    return (int(tCells[0]) * 3600) + (int(tCells[1]) * 60) + int(tCells[2]) + (0.001 * float(tCells[3]))


def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def writeToCsv(outputDir,type,inList):
    header=True
    global globalStartTime

    outPath=os.path.join(outputDir,type+"ImageSequence.csv")
    print outPath
    with open(outPath,'wb') as outCsv:
        csvWriter = csv.writer(outCsv)
        if header:
            csvWriter.writerow(["Time","Filename"])
            header=False
        for entry in inList:
            if globalStartTime==0:
                globalStartTime=entry[0]
            offsetTime = entry[0]-globalStartTime
            csvWriter.writerow([offsetTime,entry[1]])
    return


def bodyConvertTime(inFile,outDir,startTime):
    header=True
    print inFile
    inPath = os.path.join(outDir,inFile)
    fileName = os.path.splitext(inFile)[0]+"_timeClean.csv"
    outPath=os.path.join(outDir,fileName)
    with open(inPath,'rb') as inCsv, open(outPath,'wb') as outCsv:
        csvRead = csv.reader(inCsv)
        csvWrite = csv.writer(outCsv)
        for row in csvRead:
            if header:
                csvWrite.writerow(row)
                header=False
            else:
                row[0] = hms_to_seconds(row[0]) - startTime
                csvWrite.writerow(row)
    return


def main(directory):
    print 'Starting color/depth csv generation'
    for subdir in os.listdir(directory):
        if subdir=="frames":
            subDirectory = os.path.join(directory,subdir)
            for subSubDir in os.listdir(subDirectory):
                if subSubDir=="color":
                    colorList=[]
                    subSubDirectory = os.path.join(subDirectory,subSubDir)
                    for filename in sorted((os.listdir(subSubDirectory)), key=numericalSort):
                        if fnmatch.fnmatch(filename, '*.png') or fnmatch.fnmatch(filename, '*.jpg'):
                            colorList.append([hms_to_seconds_custom(os.path.splitext(filename)[0]),filename])

                    if colorList!=[]:
                        writeToCsv(subSubDirectory,'color',colorList)

                if subSubDir=="depth":
                    depthList=[]
                    subDirectory = os.path.join(directory,subdir)
                    subSubDirectory = os.path.join(subDirectory,subSubDir)
                    for filename in sorted((os.listdir(subSubDirectory)), key=numericalSort):
                        if fnmatch.fnmatch(filename, '*.png') or fnmatch.fnmatch(filename, '*.jpg'):
                            depthList.append([hms_to_seconds_custom(os.path.splitext(filename)[0]),filename])

                    if depthList!=[]:
                        writeToCsv(subSubDirectory,'depth',depthList)
        if subdir=="color":
            colorList=[]
            subDirectory = os.path.join(directory,subdir)
            for filename in sorted((os.listdir(subDirectory)), key=numericalSort):
                if fnmatch.fnmatch(filename, '*.png') or fnmatch.fnmatch(filename, '*.jpg'):
                    colorList.append([hms_to_seconds_custom(os.path.splitext(filename)[0]),filename])
            
            if colorList!=[]:
                writeToCsv(subDirectory,'color',colorList)
        
        if subdir=="depth":
            depthList=[]
            subDirectory = os.path.join(directory,subdir)
            for filename in sorted((os.listdir(subDirectory)), key=numericalSort):
                if fnmatch.fnmatch(filename, '*.png') or fnmatch.fnmatch(filename, '*.jpg'):
                    depthList.append([hms_to_seconds_custom(os.path.splitext(filename)[0]),filename])
            
            if depthList!=[]:
                writeToCsv(subDirectory,'depth',depthList)
    print 'color/depth csv done, starting body'
    global globalStartTime
    for filename in sorted((os.listdir(directory)), key=numericalSort):
         if fnmatch.fnmatch(filename, '*.csv') and not fnmatch.fnmatch(filename, '*_timeClean.csv'):
             bodyConvertTime(filename,directory,globalStartTime)


numbers = re.compile(r'(\d+)')
'''
if running script by itself, uncomment below
'''

directory = tkFileDialog.askdirectory()
main(directory)