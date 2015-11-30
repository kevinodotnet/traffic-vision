import numpy as np
import cv2
import pickle
import time
import calendar
import sys
import trafficvision as tv

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

frameskip = 3
startskip = 0 #30*30# 400
watchPoints = []
watchRadius = 5

cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mouse_click)
cv2.moveWindow('frame',100,100)

#with open("a-file.pickle",'rb') as f:
#    frame = pickle.load(f)
#    cv2.imshow('frame',frame)
#    cv2.imwrite('test.png',frame)
#    exit(0)

if True:
    # Wellington Harmer
    wp = tv.WatchPoint()
    wp.x = 1015
    wp.y = 410
    watchPoints.append(wp)
    wp = tv.WatchPoint()
    wp.x = 1595
    wp.y = 338
    watchPoints.append(wp)

    # IPD, Byron
    wp = tv.WatchPoint()
    wp.x = 428
    wp.y = 193
    #watchPoints.append(wp)
    wp = tv.WatchPoint()
    wp.x = 900
    wp.y = 197
    #watchPoints.append(wp)

frameNum=0

global_frame = 0

#cap = cv2.VideoCapture('/Users/kevino/Downloads/leiper-traffic/00000.MTS.mp4')
cap = cv2.VideoCapture(in_file)

frameNum = 0

print "init video writer..."
fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
out_fps = 10
vid_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
vid_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
out_size = (vid_width,vid_height)
fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v') # note the lower case
vw_out = cv2.VideoWriter()
success = vw_out.open("%s_%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 
print "... ready"
print success

cycleOutputAtFrameNum = 99999999

while(True):

    ret, frame = cap.read()

    if ret == False:
        print "END of video"
        break;

    if frameNum == -1:
        stageChange = tv.processframe(frameNum,fileTag,frame,cap,watchPoints)
        smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        cv2.imshow('frame',smallframe)
        key = cv2.waitKey()

    if frameNum < startskip:
        if frameNum % 100 == 0:
            print "skipping, frames left %d //  frame %d time %d " % ((startskip-frameNum),frameNum,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
        frameNum += 1 
        continue

    if frameNum % frameskip != 0:
        #no_op
        tmp_a = 0
    else:
        stageChange = tv.processframe(frameNum,fileTag,frame,cap,watchPoints)
        if frameNum > 0 and frameNum % 30 == 0:
            now_time = calendar.timegm(time.gmtime())
            processing_fps = frameNum/(now_time-start_time)
            #print "processing fps: %0.1f" % processing_fps
            smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
            cv2.imshow('frame',smallframe)
            #cv2.imshow('frame',frame)
        vw_out.write(frame)
        if stageChange:
            allRed = 1
            for i, w in enumerate(watchPoints):
                if w.isRed == 0:
                    allRed = 0
            print "stateChange,frame,%d,allRed,%d,time,%0.1f" % (frameNum,allRed,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000)
            if allRed:
                cycleOutputAtFrameNum = frameNum + (10*30) # 10 seconds later

    if frameNum == cycleOutputAtFrameNum:
        print "Closing output file, opening new one"
        vw_out.release()
        fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        out_fps = 10
        vid_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        vid_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
        out_size = (vid_width,vid_height)
        fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v') # note the lower case
        vw_out = cv2.VideoWriter()
        success = vw_out.open("%s_%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 

    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        print "PAUSING..."
        key = cv2.waitKey() & 0xFF
    if key == ord('q'):
        break

    frameNum += 1 

vw_out.release()
cap.release()
cv2.destroyAllWindows()

#key = cv2.waitKey() & 0xFF
#area = frame[xx-25:yy-25,xx+25:yy+25]
  #frame[400:400,450:450] = area

#    cv2.rectangle(frame,(100,100),(150,150),(0,255,0))
#    cv2.rectangle(frame,(300,300),(350,350),(0,0,255))

    #pix = frame[xx,yy] print pix
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('frame',gray)
# When everything done, release the capture

#         if False:
#             opacity = 0.5
#             overlay = frame.copy()
#             cv2.circle(overlay,(w.x,w.y),watchRadius,(255,0,0,128),-1)
#             cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
# 
