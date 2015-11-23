import numpy as np
import cv2
import pickle
import time
import calendar
import sys

in_file = sys.argv[1]
out_file = sys.argv[2]
file_tag = sys.argv[3]

start_time = calendar.timegm(time.gmtime())

# /Applications/HandBrakeCLI -i 00000.MTS  --start-at duration:30 --stop-at duration:30 -o 1.mp4   -w 1080
# /Applications/HandBrakeCLI -i 00000.MTS  -o 1.mp4 -w 1080

def mouse_click(event, x, y, flags, param):
    global watchPoints
    global watchRadius
    if event == cv2.EVENT_LBUTTONDOWN:
        wp = WatchPoint()
        wp.x = x
        wp.y = y
        watchPoints.append(wp)
        print wp
        cv2.circle(frame,(x,y),watchRadius,(255,0,0),-1)
        cv2.imshow('frame',frame)

class WatchPoint:
    y = 0
    x = 0
    isRed = 0
    redStart = 0
    def __str__(self):
        return "WatchPoint(x:%d,y:%d,red:%s)" % (self.x,self.y,self.isRed)

frameskip = 3
startskip = 0# 400
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

fix_x = 0
fix_y = 0
if True:
    wp = WatchPoint()
    wp.x = 430+fix_x
    wp.y = 190+fix_y
    watchPoints.append(wp)
    wp = WatchPoint()
    wp.x = 900+fix_x
    wp.y = 197+fix_y
    watchPoints.append(wp)

frameNum=0

global_frame = 0

def processframe(frameNum,frame,cap,watchPoints):

    print "frame %d time %d " % (frameNum,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
    stageChange = 0

    vid_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    cv2.rectangle(frame,(0,vid_height-50),(vid_width,vid_height),(0,0,0),-1)
    cv2.putText(frame, "Time: %0.1f Frame: %d File: %s" % ((cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000),frameNum,file_tag), (15,vid_height-25), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255,255))

    for i, w in enumerate(watchPoints):
        a = frame[w.y-5:w.y+5, w.x-5:w.x+5]
        offset = i * 2 * 10;
        #frame[offset:offset+50,0:50] = a

        if True:
            redlow = (0,0,240)
            redhigh = (128,128,255)
            mask = cv2.inRange(a,redlow,redhigh)
            prevRed = w.isRed
            if np.count_nonzero(mask) > 0:
                w.isRed = 1
            else:
                w.isRed = 0
            same = (w.isRed == prevRed)
            if same == 0:
                if w.isRed:
                    w.redStart = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
                print "offset:%d prevRed:%d nowRed:%d same:%d" % (i,prevRed,w.isRed,same)
                stageChange = 1

            output = cv2.bitwise_and(a, a, mask = mask)
            frame[offset:offset+10,0:10] = output
            frame[offset:offset+10,10:20] = a

            col = (0,0,255)
            if w.isRed:
                col = (0,0,255)
            else:
                col = (255,0,0)
            cv2.rectangle(frame,(w.x-10,0),(w.x+10,w.y-10),col,-1)
            if w.isRed:
                redFor = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) - w.redStart
                cv2.rectangle(frame,(w.x-10,w.y-40),(w.x+80,w.y-10),(0,0,0),-1)
                cv2.putText(frame, "%0.1f" % (redFor/1000), (w.x+15,w.y-15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,255,255))

        if False:
            opacity = 0.5
            overlay = frame.copy()
            cv2.circle(overlay,(w.x,w.y),watchRadius,(255,0,0,128),-1)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

    return stageChange

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
success = vw_out.open("%s-%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 
print "... ready"
print success

cycleOutputAtFrameNum = 99999999

while(True):

    ret, frame = cap.read()

    if ret == False:
        print "END of video"
        break;

#    if frameNum == 0:
#        stageChange = processframe(frameNum,frame,cap,watchPoints)
#        cv2.imshow('frame',frame)
#        vw_out.write(frame)
#        key = cv2.waitKey()

#    if frameNum < startskip:
#        if frameNum % 100 == 0:
#            print "skipping, frames left %d //  frame %d time %d " % ((startskip-frameNum),frameNum,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
#        frameNum += 1 
#        continue

    if frameNum % frameskip != 0:
        #no_op
        tmp_a = 0
    else:
        stageChange = processframe(frameNum,frame,cap,watchPoints)
        if frameNum > 0 and frameNum % 30 == 0:
            now_time = calendar.timegm(time.gmtime())
            processing_fps = frameNum/(now_time-start_time)
            print "processing fps: %0.1f" % processing_fps
            cv2.imshow('frame',frame)
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
        success = vw_out.open("%s-%.09d.mov" % (out_file,frameNum),fourcc,out_fps,out_size,True) 

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
