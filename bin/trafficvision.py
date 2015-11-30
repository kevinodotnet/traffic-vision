
import numpy as np
import cv2
import pickle
import time
import calendar
import sys
import json
import os

class WatchPoint:
    y = 0
    x = 0
    isRed = 0
    redStart = 0
    def __str__(self):
        return "WatchPoint(x:%d,y:%d,red:%s)" % (self.x,self.y,self.isRed)


    def paint(self,frame,clipMSEC):

        col = (255,0,0)
        if self.isRed:
            col = (0,0,255)

        cv2.rectangle(frame,(self.x-20,100),(self.x+20,self.y-10),col,-1)
        if self.isRed:
            redFor = clipMSEC - self.redStart
            cv2.rectangle(frame,(self.x+20,self.y-120),(self.x+300,self.y-10),(0,0,0),-1)
            cv2.putText(frame, "%0.1f" % (redFor/1000), 
                    (self.x+30,self.y-30), cv2.FONT_HERSHEY_DUPLEX, 3, (0,0,255,255), 4)

    def processframe(self,frame):

        if True:
            pix = frame[self.y,self.x]
            pixFLOAT = frame[self.y,self.x].astype(np.float64)
            bgRatio = abs((pixFLOAT[0] / pixFLOAT[1]) - 1)
            print "(%d,%d) %s ratio: %.2f" % (self.x,self.y,pix,bgRatio)
            self.isRed = 0
            if pix[2] > 192 and bgRatio < 0.25:
                # red is strong, blue/green in close enough balance to not be confused with 'amber'
                self.isRed = 1
            if pix[0] > 192 and pix[1] > 192 and pix[2] > 192: 
                # almost white, so must be 'red light on' with max intensity
                self.isRed = 1
            if pix[0] < 128 and pix[1] < 128 and pix[2] > 192: 
                # red is just strong
                self.isRed = 1

        if False:
            pixelAt = frame[y,x]
            print "%d :: %d :: (red:%d) bgr: %s" % (frameNum,i,pixelAt[2],pixelAt)
            pixelAtRed = pixelAt[2]
            if pixelAtRed > 256*0.75:
                isRed = 1
            else:
                isRed = 0

        if False:
            # old "in red range" check
            a = frame[y-5:y+5, x-5:x+5]
            offset = i * 50;
            redlow = (0,0,128)
            redhigh = (255,255,255)
            bigger_orig = cv2.resize(a, (0,0), fx=5, fy=5) 
            output = cv2.bitwise_and(a, a, mask = mask)
            bigger_mask = cv2.resize(output, (0,0), fx=5, fy=5) 
            frame[offset:offset+50,0:50] = bigger_mask
            frame[offset:offset+50,50:100] = bigger_orig
            mask = cv2.inRange(a,redlow,redhigh)
            if np.count_nonzero(mask) > 0:
                isRed = 1
            else:
                isRed = 0

def unittest (conffile):

    cv2.namedWindow('frame')
    cv2.moveWindow('frame',100,100)

    print "reading json file: %s" % conffile

    f = open(conffile,'r')
    conf = json.loads(f.read())

    mp4file = "%s/%s" % (os.path.dirname(conffile),conf['video'])

    watchPoints = []

    for w in conf['watchpoints']:
        wp = WatchPoint()
        wp.x = w['x'];
        wp.y = w['y'];
        watchPoints.append(wp)

    cap = cv2.VideoCapture(mp4file)
    frameNum = 0
    ret, frame = cap.read()
    if ret == False:
        print "unexpected end of file"
        exit(-1)

    for t in conf['tests']:

        print ""
        print "test: %s" % t
        print ""

        print "scanning to frame %d" % t['frame']
        while frameNum < t['frame']:
            ret, frame = cap.read()
            frameNum += 1
            if ret == False:
                print "unexpected end of file"
                exit(-1)

        smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        cv2.imshow('frame',smallframe)

        for i in range(0,len(t['red'])):
            wp = watchPoints[i]
            red = t['red'][i]
            wp.processframe(frame)
            passed = red == wp.isRed
            print "passed:%d index:%d shouldBeRed:%d detectedRed:%d" % (passed,i,red,wp.isRed)
            if passed == 0:
                wp.paint(frame,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
                smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
                cv2.imshow('frame',smallframe)
                key = cv2.waitKey()

    cap.release()


def processframe (frameNum,fileTag,frame,cap,watchPoints):

    print "frame %d time %d " % (frameNum,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
    stageChange = 0

    vid_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    cv2.rectangle(frame,(0,0),(vid_width,100),(0,0,0),-1)
    cv2.putText(frame, "time:%0.1f frame:%d file:%s" % ((cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)/1000),frameNum,fileTag), 
            (50,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255,255), 4)

    for i, w in enumerate(watchPoints):

        prevRed = w.isRed

        w.processframe(frame)

        w.paint(frame,cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))

        same = (w.isRed == prevRed)
        if same == 0:
            if w.isRed:
                w.redStart = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
            else:
                wasRedFor = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC) - w.redStart
                print "RED TO GREEN detected; wasRedFor: %d" % wasRedFor

            print "offset:%d prevRed:%d nowRed:%d same:%d" % (i,prevRed,w.isRed,same)
            stageChange = 1


    return stageChange

