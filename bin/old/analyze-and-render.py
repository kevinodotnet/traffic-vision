import numpy as np
import cv2
import pickle
import time
import calendar
import sys
import trafficvision as tv
import logging
import json
import argparse
import pprint

pp = pprint.PrettyPrinter(indent=2)
log = tv.logger()

parser = argparse.ArgumentParser(description='Process video file of intersections')
parser.add_argument('-c',action='store_const', const=1, help='Display crosshairs in output frames')
parser.add_argument('--outfps',metavar='10',type=int,default=10,help='FPS of output file')
parser.add_argument('--inskip',metavar='3',type=int,default=3,help='Frames to skip while reading input file') # TODO: just calculate based on INPUT_FRAMERATE/OUTFPS
parser.add_argument('-w',metavar='x:y',action='append',help='Watchpoint in x:y format')
parser.add_argument('-o',metavar='output/path/prefix',help='basename of output file(s)')
parser.add_argument('-i',metavar='filename',type=file,action='append',help='Input movie file(s) with OS globbing',nargs=argparse.REMAINDER)

args = parser.parse_args()
#print ""
#print args
#print ""

# collect -w into list of WatchPoint
watchPoints = []
for w in args.w:
    xy = w.split(':')
    wp = tv.WatchPoint()
    wp.x = int(xy[0])
    wp.y = int(xy[1])
    watchPoints.append(wp)
    log.info("%s" % wp)

# collect all the -i into one list
inFiles = []
for x in args.i:
    if isinstance(x,list):
        for xx in x:
            inFiles.append(xx)
            log.info("inputfile: %s" % xx)
    else:
        inFiles.append(x)
        log.info("inputfile: %s" % x)

videoJob = tv.VideoJob()
videoJob.inFiles = inFiles
videoJob.crosshairs = args.c
videoJob.outFPS = args.outfps
videoJob.frameSkip = args.inskip
videoJob.watchPoints = watchPoints
videoJob.outputPrefix = args.o
videoJob.saveStateChange()
videoJob.runJob()
exit(0)

in_file = sys.argv[1]
out_file = sys.argv[2]
fileTag = sys.argv[3]

start_time = calendar.timegm(time.gmtime())

# /Applications/HandBrakeCLI -i 00000.MTS  --start-at duration:30 --stop-at duration:30 -o 1.mp4   -w 1080
# /Applications/HandBrakeCLI -i 00000.MTS  -o 1.mp4 -w 1080

def mouse_click(event, x, y, flags, param):
    global watchPoints
    global watchRadius
    if event == cv2.EVENT_LBUTTONDOWN:
        wp = tv.WatchPoint()
        wp.x = x
        wp.y = y
        watchPoints.append(wp)
        print wp
        print "wp = WatchPoint()"
        print "wp.x = %d" % x
        print "wp.y = %d" % y
        print "watchPoints.append(wp)"
        cv2.circle(frame,(x,y),watchRadius,(255,0,0),-1)
        smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        cv2.imshow('frame',smallframe)

cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mouse_click)
cv2.moveWindow('frame',100,100)

frameNum=0

global_frame = 0

#cap = cv2.VideoCapture('/Users/kevino/Downloads/leiper-traffic/00000.MTS.mp4')
cap = cv2.VideoCapture(in_file)

frameNum = 0

print "init video writer..."
out_fps = 10
vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out_size = (vid_width,vid_height)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
vw_out = cv2.VideoWriter()
success = vw_out.open("%s_%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 
print "... ready"
print success

cycleOutputAtFrameNum = 99999999

current_milli_time = lambda: int(round(time.time() * 1000))

now_time = current_milli_time()

while(True):

    ret, frame = cap.read()

    if ret == False:
        print "END of video"
        break;

    if frameNum < startskip:
        if frameNum % 100 == 0:
            print "skipping, frames left %d //  frame %d time %d " % ((startskip-frameNum),frameNum,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
        frameNum += 1 
        continue

    if frameNum % frameskip == 0:
        stageChange = tv.processframe(frameNum,fileTag,frame,cap,watchPoints)
        if frameNum > 0 and frameNum % 30 == 0:
            prev_time = now_time
            now_time = current_milli_time()
            processing_fps = frameNum/(now_time-start_time)
            print "frame %d time %d timeFor %d " % (frameNum,cap.get(cv2.CAP_PROP_POS_MSEC),now_time-prev_time)
            smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
            cv2.imshow('frame',smallframe)
            key = cv2.waitKey(1)

        vw_out.write(frame)

        if stageChange:
            allRed = 1
            for i, w in enumerate(watchPoints):
                if w.isRed == 0:
                    allRed = 0
            print "stateChange,frame,%d,allRed,%d,time,%0.1f" % (frameNum,allRed,cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
            if allRed:
                cycleOutputAtFrameNum = frameNum + (10*30) # 10 seconds later

    if frameNum == cycleOutputAtFrameNum:
        print "Closing output file, opening new one"
        vw_out.release()
        out_fps = 10
        vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_size = (vid_width,vid_height)
        vw_out = cv2.VideoWriter()
        success = vw_out.open("%s_%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 

    frameNum += 1 

vw_out.release()
cap.release()
cv2.destroyAllWindows()

