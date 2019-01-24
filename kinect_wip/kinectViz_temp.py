import imageio
import numpy as np
import matplotlib.pylab as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.animation as manimation
from mpl_toolkits.mplot3d import Axes3D
import bisect
import datetime
import os
import pandas as pd
from decimal import Decimal
import warnings

# squelch warnings about plt.tight_layout()
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Input files
dataDir = "/Users/stevenrick/Downloads/stuff"
video = dataDir+"/color_video_cut.mp4"
body = dataDir+"/body_1_jointPosition.csv"

# Flag to add legend
plotLegend = False

# Fig meta
fig = plt.figure(figsize=(20, 10))
# initial defaults for axes
xPxMin = 0
xPxMax = 1920
yPxMin = 1080
yPxMax = 0
xMin = -1.15
xMax = 1.65
yMin = -0.25
yMax = 4.85
zMin = -0.25
zMax = 1.75

# Movie Attributes
DPI = 200  # quality of saved picture (see writer)  (older- 300)
FPS = 30   # increase to speed up movie
FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(artist='Matplotlib')
writer = FFMpegWriter(fps=FPS, codec='h264', metadata=metadata)

# Kinect Meta #
KinectJointConnections = [['SpineBase', 'SpineMid'],
                          ['SpineMid', 'SpineShoulder'],
                          ['SpineShoulder', 'Neck'],
                          ['Neck', 'Head'],
                          ['SpineShoulder', 'ShoulderLeft'],
                          ['ShoulderLeft', 'ElbowLeft'],
                          ['ElbowLeft', 'WristLeft'],
                          ['WristLeft', 'ThumbLeft'],
                          ['WristLeft', 'HandLeft'],
                          ['HandLeft', 'HandTipLeft'],
                          ['SpineShoulder', 'ShoulderRight'],
                          ['ShoulderRight', 'ElbowRight'],
                          ['ElbowRight', 'WristRight'],
                          ['WristRight', 'ThumbRight'],
                          ['WristRight', 'HandRight'],
                          ['HandRight', 'HandTipRight']]

in_fields = ['Time', 'HeadX', 'HeadY', 'HeadZ', 'HeadTrackingState',
             'NeckX', 'NeckY', 'NeckZ', 'NeckTrackingState',
             'SpineShoulderX', 'SpineShoulderY', 'SpineShoulderZ', 'SpineShoulderTrackingState',
             'SpineMidX', 'SpineMidY', 'SpineMidZ', 'SpineMidTrackingState',
             'SpineBaseX', 'SpineBaseY', 'SpineBaseZ', 'SpineBaseTrackingState',
             'ShoulderLeftX', 'ShoulderLeftY', 'ShoulderLeftZ', 'ShoulderLeftTrackingState',
             'ShoulderRightX', 'ShoulderRightY', 'ShoulderRightZ', 'ShoulderRightTrackingState',
             'ElbowLeftX', 'ElbowLeftY', 'ElbowLeftZ', 'ElbowLeftTrackingState',
             'ElbowRightX', 'ElbowRightY', 'ElbowRightZ', 'ElbowRightTrackingState',
             'WristLeftX', 'WristLeftY', 'WristLeftZ', 'WristLeftTrackingState',
             'WristRightX', 'WristRightY', 'WristRightZ', 'WristRightTrackingState',
             'HandLeftX', 'HandLeftY', 'HandLeftZ', 'HandLeftTrackingState',
             'HandRightX', 'HandRightY', 'HandRightZ', 'HandRightTrackingState',
             'HandTipLeftX', 'HandTipLeftY', 'HandTipLeftZ', 'HandTipLeftTrackingState',
             'HandTipRightX', 'HandTipRightY', 'HandTipRightZ', 'HandTipRightTrackingState',
             'ThumbLeftX', 'ThumbLeftY', 'ThumbLeftZ', 'ThumbLeftTrackingState',
             'ThumbRightX', 'ThumbRightY', 'ThumbRightZ', 'ThumbRightTrackingState']

KinectJointHeader = ['Time', 'Head_X', 'Head_Y', 'Head_Z', 'Head_TrackingState',
                     'Neck_X', 'Neck_Y', 'Neck_Z', 'Neck_TrackingState',
                     'SpineShoulder_X', 'SpineShoulder_Y', 'SpineShoulder_Z', 'SpineShoulder_TrackingState',
                     'SpineMid_X', 'SpineMid_Y', 'SpineMid_Z', 'SpineMid_TrackingState',
                     'SpineBase_X', 'SpineBase_Y', 'SpineBase_Z', 'SpineBase_TrackingState',
                     'ShoulderLeft_X', 'ShoulderLeft_Y', 'ShoulderLeft_Z', 'ShoulderLeft_TrackingState',
                     'ShoulderRight_X', 'ShoulderRight_Y', 'ShoulderRight_Z', 'ShoulderRight_TrackingState',
                     'ElbowLeft_X', 'ElbowLeft_Y', 'ElbowLeft_Z', 'ElbowLeft_TrackingState',
                     'ElbowRight_X', 'ElbowRight_Y', 'ElbowRight_Z', 'ElbowRight_TrackingState',
                     'WristLeft_X', 'WristLeft_Y', 'WristLeft_Z', 'WristLeft_TrackingState',
                     'WristRight_X', 'WristRight_Y', 'WristRight_Z', 'WristRight_TrackingState',
                     'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z', 'HandLeft_TrackingState',
                     'HandRight_X', 'HandRight_Y', 'HandRight_Z', 'HandRight_TrackingState',
                     'HandTipLeft_X', 'HandTipLeft_Y', 'HandTipLeft_Z', 'HandTipLeft_TrackingState',
                     'HandTipRight_X', 'HandTipRight_Y', 'HandTipRight_Z', 'HandTipRight_TrackingState',
                     'ThumbLeft_X', 'ThumbLeft_Y', 'ThumbLeft_Z', 'ThumbLeft_TrackingState',
                     'ThumbRight_X', 'ThumbRight_Y', 'ThumbRight_Z', 'ThumbRight_TrackingState']
# End Kinect Meta #

# video data prep
# videoTime = float(Decimal(os.path.splitext(os.path.basename(video))[0].split("_")[1]) / Decimal(1000.0))
videoTime = float(760.0)
videoStart = datetime.datetime.utcfromtimestamp(videoTime)

reader = imageio.get_reader(video)
video_meta = reader.get_meta_data()
video_fps = video_meta['fps']
video_len = video_meta['nframes']

# body data prep
# kinect_array = np.genfromtxt(open(body, "rb"),
#                              delimiter=",",
#                              skip_header=1,
#                              filling_values=0
#                              )
kinect_DF = pd.read_csv(body, header=0, usecols=in_fields)
kinect_DF.columns = KinectJointHeader

# prep timestrings to datetimes and ignore before videoStart
kinect_DF["Time"] = pd.to_datetime(kinect_DF["Time"], unit="s")
kinect_DF = kinect_DF[kinect_DF["Time"] >= videoStart]

# ignoreIds = []
# remove undesired trackingIDs
# for badId in ignoreIds:
#     kinect_DF = kinect_DF[kinect_DF["TrackingID"] != badId]

# shift all times relative to start
kinect_DF["Time"] = kinect_DF["Time"] - videoStart
kinect_DF["TrackingID"] = 123

# define 6 distinct colors, never need more at any one time
# good_colors = ["#ffaa00", "#258c00", "#00ffee", "#00aaff", "#ad00d9", "#7f0044"]
good_colors = ["#ffaa00"]
nice_gray = "0.75"

# plot marker size
msize = 2
headSize = 400

# faster than df.unique()
colorIds = pd.unique(kinect_DF["TrackingID"].values.ravel())
colorIds = np.array(colorIds, dtype=np.dtype(Decimal))

# assign colors to IDs and store in dict
colorDict = dict()
for id in colorIds:
    # colorDict[id] = good_colors[np.where(colorIds == id)[0] % 6]
    colorDict[id] = "#ffaa00"

# pull out timestamps from CSV data for binary search
bodyTimes = kinect_DF["Time"]
s = sorted(bodyTimes)
# print s


def nearestBodyData(ts):
    # binary search of timestamps for nearest data, given a presorted list of timestamps -> s
    i = bisect.bisect_left(s, ts)
    # print i
    return min(s[max(0, i-1): i+2], key=lambda t: abs(ts - t))


def ClearPlotObjects(PltObjArr):
    # pass in plot object array from user, clear from the map
    while len(PltObjArr) > 0:
            ob = PltObjArr.pop()
            ob.remove()
            del ob
            ob = []
    return


def getAxisRange():
    # need to check X min and max, Y max, and Z max
    global xMin
    global xMax
    global yMax
    global zMax
    # select 3D data
    # three_d = kinect_DF.filter(regex="(X|Y|Z)").filter(regex="^((?!2D|Face).)*$")
    three_d = kinect_DF.filter(regex="(X|Y|Z)").filter(regex="^((?!2D|Face).)*$")
    x_data = three_d.filter(regex="X")
    y_data = three_d.filter(regex="Y")
    z_data = three_d.filter(regex="Z")
    temp_xMin = x_data.min().min()
    temp_xMax = x_data.max().max()
    temp_yMax = y_data.max().max()
    temp_zMax = z_data.max().max()
    if xMin > temp_xMin:
        xMin = temp_xMin
    if xMax < temp_xMax:
        xMax = temp_xMax
    if yMax < temp_yMax:
        yMax = temp_yMax
    if zMax < temp_zMax:
        zMax = temp_zMax
    return


def main():
    getAxisRange()
    count = 0
    PltObjs = {}
    with writer.saving(fig, dataDir+"/video_output.mp4", DPI):
        totalFrames = len(reader)

        ax1 = fig.add_subplot(121, projection='3d')
        ax1.grid(False)
        ax1.set_xlim(xMin, xMax)
        ax1.set_ylim(yMin, yMax)
        ax1.set_zlim(zMin, zMax)
        ax1.hold(True)

        ax2 = fig.add_subplot(122)
        ax2.axis([xPxMin, xPxMax, yPxMin, yPxMax])
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.hold(True)

        titleTxt = fig.suptitle('', fontsize=15, fontweight='bold')

        plt.tight_layout()
        plt.draw()

        for num, img in enumerate(reader):
            Progress = (float(count) / float(totalFrames))*100
            print("Progress: %i/%i = %.2f %%" % (count, totalFrames, Progress))
            frame_time = datetime.timedelta(seconds=(num / video_fps))

            # timestamp = (videoStart + frame_time).strftime('%d/%m/%Y %H:%M:%S.%f')

            # titleTxt.set_text('KinectSense - ' + timestamp)

            nearest = nearestBodyData(frame_time)
            diff = abs((nearest - frame_time).total_seconds())

            print frame_time, diff

            PltObjs["NA"] = list()
            PltObjs["NA"].append(ax2.imshow(img))

            if diff < 0.15:
                plotData = kinect_DF[kinect_DF["Time"] == nearest]
                # print plotData
                numPeople = plotData.shape[0]
                for n in range(numPeople):
                    id_n = int(plotData["TrackingID"].iloc[n])
                    PltObjs[id_n] = list()
                    personData = plotData[plotData["TrackingID"] == id_n]
                    # create three df which are subsamples based on regex
                    # states = plotData.filter(regex="State")
                    # two_d = plotData.filter(regex="2D")
                    # three_d = plotData.filter(regex="(X|Y|Z)").filter(regex="^((?!2D|Face).)*$")

                    # head 3D data
                    head_trackingState = personData["Neck_TrackingState"].values[0]
                    if head_trackingState == "Inferred":
                        headColor = nice_gray
                        fade = .5
                    else:
                        headColor = colorDict[id_n];
                        fade = 1
                    head_x = personData["Head_X"]
                    head_y = personData["Head_Y"]
                    head_z = personData["Head_Z"]
                    PltObjs[id_n].append(ax1.scatter(head_x, head_z, head_y, c=headColor,
                                                     alpha=fade, marker='o', edgecolor=headColor, s=headSize))

                    # body 3D and 2D data
                    for pair in KinectJointConnections:
                        j1 = pair[0]
                        j2 = pair[1]
                        TrackingState1 = personData[j1+"_TrackingState"].values[0]
                        TrackingState2 = personData[j2+"_TrackingState"].values[0]
                        x1 = personData[j1+"_X"].values[0]
                        y1 = personData[j1+"_Y"].values[0]
                        z1 = personData[j1+"_Z"].values[0]
                        x2 = personData[j2+"_X"].values[0]
                        y2 = personData[j2+"_Y"].values[0]
                        z2 = personData[j2+"_Z"].values[0]
                        # x1_px = personData[j1+"_2D_X"].values[0]
                        # y1_px = personData[j1+"_2D_Y"].values[0]
                        # x2_px = personData[j2+"_2D_X"].values[0]
                        # y2_px = personData[j2+"_2D_Y"].values[0]
                        if TrackingState1 == "Inferred" or TrackingState2 == "Inferred":
                            markerColor = nice_gray
                            fade = .5
                        else:
                            markerColor = colorDict[id_n];
                            fade = 1
                        # 3D plot - flip Y and Z to make orientation look natural
                        PltObjs[id_n].append(ax1.plot([x1, x2], [z1, z2], [y1, y2], '-', alpha=fade, lw=1.5,
                                                      color=markerColor, markersize=msize)[0])

                        # # 2D plot
                        # if x1_px == "NA" or x2_px == "NA" or y1_px == "NA" or y2_px == "NA":
                        #     nothing = True
                        # elif x1_px == 0 or x2_px == 0 or y1_px == 0 or y2_px == 0:
                        #     nothing = True
                        # else:
                        #     PltObjs[id_n].append(ax2.plot([x1_px, x2_px], [y1_px, y2_px], color=markerColor,
                        #                                   linestyle='-', linewidth=2)[0])
                        #     circ1 = mpatches.Circle((x1_px, y1_px), 10, facecolor=markerColor, edgecolor=markerColor)
                        #     circ2 = mpatches.Circle((x2_px, y2_px), 10, facecolor=markerColor, edgecolor=markerColor)
                        #     PltObjs[id_n].append(ax2.add_patch(circ1))
                        #     PltObjs[id_n].append(ax2.add_patch(circ2))

                if plotLegend:
                    # dynamically generate legend
                    legendIds = []
                    for id in PltObjs:
                        if id != "NA":
                            tempString = 'legend' + str(id)
                            locals()[tempString] = mlines.Line2D([], [], color=colorDict[id], label=id, linewidth=2)
                            legendIds.append(locals()[tempString])
                    PltObjs["NA"].append(ax2.legend(handles=legendIds, loc='upper center', bbox_to_anchor=(0.5, 1.2)))
                    # cleanup dynamic legend
                    for id in PltObjs:
                        if id != "NA":
                            tempString = 'legend' + str(id)
                            del locals()[tempString]
                    del legendIds

            writer.grab_frame()
            plt.draw()
            for id in PltObjs.keys():
                ClearPlotObjects(PltObjs[id])
                PltObjs.pop(id, None)
            count += 1
    return


main()
