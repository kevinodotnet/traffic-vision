
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
            if pix[2] > 192 and (pixFLOAT[1] > pixFLOAT[0]) and bgRatio > 0.45:
                # even if R component is high, big ratio means more likely to be amber
                self.isRed = 0
            return "(%d,%d) %s ratio: %.2f" % (self.x,self.y,pix,bgRatio)

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
            for i in range(0,len(t['red'])):
                wp = watchPoints[i]
                debug = wp.processframe(frame)
                print "frameNum:%d passed:na index:%d detectedRed:%d debug >>> %s" % (frameNum,i,wp.isRed,debug)
                wp.paint(frame,cap.get(cv2.CAP_PROP_POS_MSEC))

        t['failed'] = 0
        for i in range(0,len(t['red'])):
            wp = watchPoints[i]
            red = t['red'][i]
            debug = wp.processframe(frame)
            passed = red == wp.isRed
            print "frameNum:%d passed:%d index:%d shouldBeRed:%d detectedRed:%d debug >>> %s" % (frameNum,passed,i,red,wp.isRed,debug)
            wp.paint(frame,cap.get(cv2.CAP_PROP_POS_MSEC))
            if passed == 0:
                t['failed'] = 1
     
        paint(frameNum,"failed:%d" % t['failed'],frame,cap)
        smallframe = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        t['frame'] = smallframe
        #cv2.imshow('frame',smallframe)
        #key = cv2.waitKey(1)
        #if failed == 1:
        #    key = cv2.waitKey()

    print "DONE PARSING..."
    while True:
        failCount = 0
        for t in conf['tests']:
            if t['failed'] == 1:
                failCount += 1
                cv2.imshow('frame',t['frame'])
                key = cv2.waitKey(500)
        print "DONE PARSING; failCount: %d" % failCount
        if failCount == 0:
            exit(0)

def paint (frameNum,tag,frame,cap):

    vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.rectangle(frame,(0,0),(vid_width,100),(0,0,0),-1)
    cv2.putText(frame, "time:%0.1f frame:%d file:%s" % ((cap.get(cv2.CAP_PROP_POS_MSEC)/1000),frameNum,tag), 
            (50,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255,255), 4)


def processframe (frameNum,fileTag,frame,cap,watchPoints):

    stageChange = 0

    paint(frameNum,fileTag,frame,cap)

    for i, w in enumerate(watchPoints):

        prevRed = w.isRed

        w.processframe(frame)

        w.paint(frame,cap.get(cv2.CAP_PROP_POS_MSEC))

        same = (w.isRed == prevRed)
        if same == 0:
            if w.isRed:
                w.redStart = cap.get(cv2.CAP_PROP_POS_MSEC)
            else:
                wasRedFor = cap.get(cv2.CAP_PROP_POS_MSEC) - w.redStart
                print "RED TO GREEN detected; wasRedFor: %d" % wasRedFor

            print "offset:%d prevRed:%d nowRed:%d same:%d" % (i,prevRed,w.isRed,same)
            stageChange = 1


    return stageChange

