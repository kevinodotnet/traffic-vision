
import numpy as np
import cv2
import pickle
import time
import calendar
import sys
import json
import os
import logging
import os.path
import pprint

log = None

pp = pprint.PrettyPrinter(indent=2)

def jdefault(o):
    return o.__dict__

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
            log.info("%d :: %d :: (red:%d) bgr: %s" % (frameNum,i,pixelAt[2],pixelAt))
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

class VideoJob:

    # location of red lights that are watched
    watchPoints = []

    # list of fully resolve input files
    inFiles = []

    # output files will bhe "output_[framenum]"
    outputPrefix = "output_"

    # none NONE for "do motion mask"
    motionMask = None
    motionKernel = None
    motionBacksub = None

    # Current video reader and index into inFiles that it is reading from
    capIndex = None
    cap = None
    frameNum = -1 # global across all infiles
    frameSkip = 3 # frames to skip between reads before returning a frame for processing
    outFPS = 10 # FPS of output file (best result is "INPUT_FPS/frameSkip" (ie: 30/3 = 10)
    localFrameNum = -1 # relative to current infile

    # seconds of runtime of previous clips, so 'time' in top-left grows across everything
    clipTotalTimeOffset = 0
    last_CAP_PROP_POS_MSEC = 0

    clipEndOffset = 10 
    inputFPS = 30

    # as lights go to/from red, a snapshot of the current WatchPoints and frame data is added to this list.
    stateChanges = []

    # current video being written
    vw_out = None
    clipFilename = None
    clipFirstFrame = None
    # details of current output clip
    clips = []

    frame = None
    frame2 = None

    def closeVideoWriter(self):
        log.info('Closing old video writer...')
        self.vw_out.release()
        self.clips.append({
            "firstFrame" : self.clipFirstFrame,
            "lastFrame" : self.frameNum,
            "file" : self.clipFilename
        })

    def openVideoWriter(self):
        if self.vw_out != None:
            self.closeVideoWriter()

        self.clipFirstFrame = self.frameNum
        vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_size = (vid_width,vid_height)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.vw_out = cv2.VideoWriter()
        self.clipFilename = '%s_%.09d.mov' % (self.outputPrefix,self.frameNum)
        log.info('Opening new video writer: %s' % self.clipFilename)
        success = self.vw_out.open(self.clipFilename,fourcc,self.outFPS,out_size,True) 
        # TODO: handle failure
        return

    def writeFrame (self,frame):
        if self.vw_out == None:
            self.openVideoWriter()
        self.vw_out.write(frame)
        
    def readFrame (self):

        if self.cap == None:
            self.capIndex = 0
            log.info('Initializing video reader: %s' % self.inFiles[self.capIndex].name)
            self.cap = cv2.VideoCapture(self.inFiles[self.capIndex].name)

        ret, frame = self.cap.read()
        if ret == True:
            self.frameNum += 1
            self.localFrameNum += 1
            self.last_CAP_PROP_POS_MSEC = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            return (True,frame)

        log.info('No more frames left; capIndex: %d; moving to next file' % self.capIndex)
        self.clipTotalTimeOffset += self.last_CAP_PROP_POS_MSEC/1000
        log.info('clipTotalTimeOffset: %d' % self.clipTotalTimeOffset)
        self.cap.release()

        # capIndex is changed, so call self again and next frame should pop out
        self.capIndex += 1
        if (self.capIndex >= len(self.inFiles)):
            log.info('No more inFiles to read from')
            return (False,None)

        log.info('Initializing video reader: %s' % self.inFiles[self.capIndex].name)
        self.cap = cv2.VideoCapture(self.inFiles[self.capIndex].name)
        self.localFrameNum = -1
        return self.readFrame()

    def saveStateChange(self):

        data = {}
        data['frame'] = self.frameNum;
        wp = []
        for i, w in enumerate(self.watchPoints):
            wp.append({ "index" : i, "x" : w.x, "y" : w.y, "isRed" : w.isRed })
        data['watchPoints'] = wp
        self.stateChanges.append(data)

    def backgroundFrameFinder(self):

        cv2.namedWindow('frame')
        cv2.moveWindow('frame',50,50)
        while True:

            ret, frame = self.readFrame()
            if ret == False:
                log.info('done reading input files')
                break;

            processframe(self.frameNum,frame,self.cap,self.watchPoints,self.clipTotalTimeOffset)
            showFrame(frame)

    def motion_based_background_image_finder(self):

        cv2.namedWindow('frame')
        cv2.namedWindow('mask')
        cv2.namedWindow('bgf')
        cv2.moveWindow('frame',10,10)
        cv2.moveWindow('mask',400,10)
        cv2.moveWindow('bgf',10,400)

        bgf = None

        while True:

            ret, frame = self.readFrame()
            if ret == False:
                log.info('done reading input files')
                break;

            frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
            if self.frameSkip > 0 and self.frameNum % self.frameSkip != 0:
                # we aren't using every input frame, so skip skip skip
                log.info('skipping frame')
                continue


            if self.motionKernel == None:
                self.motionKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
                self.motionBacksub = cv2.createBackgroundSubtractorMOG2()
                mask3 = np.zeros_like(frame)
                #for x in range(0, 1):
                self.motionBacksub.apply(mask3, None, 0.005)

            if bgf == None:
                bgf = np.zeros_like(frame)

            mask = self.motionBacksub.apply(frame, None, 0.005)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.motionKernel)
            mask = cv2.bitwise_not(mask)

            for x in range(len(mask)):
                for y in range(len(mask[x])):
                    cell = mask[x][y]
                    if (cell > 0):
                        bgfcell = bgf[x][y]
                        framecell = frame[x][y]
                        #print "(%d:%d) %d " % (x,y,cell)
                        if (bgfcell[0] == 0 and bgfcell[1] == 0 and bgfcell[2] == 0):
                            bgfcell[0] = framecell[0]
                            bgfcell[1] = framecell[1]
                            bgfcell[2] = framecell[2]

            #cv2.imshow('frame',frame)
            #cv2.imshow('mask',mask)
            cv2.imshow('bgf',bgf)
            cv2.waitKey(1)

            #print frame.shape
            self.writeFrame(frame)

        # end of WhileTrue:
        cv2.imwrite(self.outputPrefix,bgf)

        log.info('closing last video writer')

    def motion_picker_onto_background_mouse_click(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            delta=30
            print "click at x:%d y:%d" % (x,y)

            #cv2.rectangle(self.frame,(x-delta,y-delta),(x+delta,y+delta),(0,255,0),3)

            subset = self.frame[(y-delta):(y+delta),(x-delta):(x+delta)]
            self.frame2[(y-delta):(y+delta),(x-delta):(x+delta)] = subset

            #cv2.circle(self.frame,(x,y),radius,(255,0,0),-1)
            #cv2.circle(self.frame2,(x,y),radius,(255,0,0),-1)
            cv2.imshow('frame',self.frame)
            cv2.imshow('frame2',self.frame2)

    def motion_picker_onto_background(self,backgroundFile):

        cv2.namedWindow('frame');
        cv2.moveWindow('frame',0,0)
        cv2.setMouseCallback('frame', self.motion_picker_onto_background_mouse_click)
        cv2.namedWindow('frame2');
        cv2.moveWindow('frame2',500,20)

        log.info('Starting job')

        self.motionKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        self.motionBacksub = cv2.createBackgroundSubtractorMOG2()

        while True:

            ret, frame = self.readFrame()
            if ret == False:
                log.info('done reading input files')
                break;

            if self.frameSkip > 0 and self.frameNum % self.frameSkip != 0:
                # we aren't using every input frame, so skip skip skip
                log.info('skipping frame')
                continue

            frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 

            self.frame = frame 
            self.frame2 = cv2.imread(backgroundFile)

            cv2.imshow('frame',self.frame)
            cv2.imshow('frame2',self.frame2)
            cv2.waitKey(0)

            outfile = '%s_%.09d.png' % (self.outputPrefix,self.frameNum)
            cv2.imwrite(outfile,self.frame2)

            #background = cv2.imread(backgroundFile)
            #np.copyto(background,self.frame,casting='equiv',where=self.frame)
            #cv2.imshow('frame2',background)
            #cv2.waitKey(0)

#            if self.frameNum >= cycleOutputAtFrameNum:
#                cycleOutputAtFrameNum = self.frameNum + framesPerClip
#                self.openVideoWriter()

        # end of WhileTrue:
        log.info('closing last video writer')
        self.closeVideoWriter()

    def clipper(self,framesPerClip):

        log.info('Starting job')

        cycleOutputAtFrameNum = framesPerClip
        log.info('cycleOutputAtFrameNum: %d' % cycleOutputAtFrameNum)

        cv2.namedWindow('frame')
        cv2.moveWindow('frame',50,50)

        while True:

            ret, frame = self.readFrame()
            if ret == False:
                log.info('done reading input files')
                break;

            if self.frameSkip > 0 and self.frameNum % self.frameSkip != 0:
                # we aren't using every input frame, so skip skip skip
                #print frame
                #frame.copyTo(background,frame)
                #log.info('skipping frame')
                continue

            if self.motionMask:
                if self.motionKernel == None:
                    self.motionKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
                    self.motionBacksub = cv2.createBackgroundSubtractorMOG2()
                mask = self.motionBacksub.apply(frame, None, 0.01)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.motionKernel)

                mask3 = np.zeros_like(frame)
                mask3[:,:,0] = mask
                mask3[:,:,1] = mask
                mask3[:,:,2] = mask

                print frame.shape
                print mask3.shape
                frame = cv2.bitwise_and(frame,mask3)

            processframe(self.frameNum,frame,self.cap,self.watchPoints,self.clipTotalTimeOffset)
            showFrame(frame)
            #key = cv2.waitKey(0)
            #print frame.shape
            self.writeFrame(frame)

            if self.frameNum >= cycleOutputAtFrameNum:
                cycleOutputAtFrameNum = self.frameNum + framesPerClip
                log.info('cycleOutputAtFrameNum: %d' % cycleOutputAtFrameNum)
                self.openVideoWriter()

        # end of WhileTrue:
        log.info('closing last video writer')
        self.closeVideoWriter()

    def runJob(self):

        log.info('Starting job')

        cycleOutputAtFrameNum = 999999999999

        cv2.namedWindow('frame')
        cv2.moveWindow('frame',50,50)

        while True:

            ret, frame = self.readFrame()
            if ret == False:
                log.info('done reading input files')
                break;
                exit(0)

            if self.frameSkip > 0 and self.frameNum % self.frameSkip != 0:
                # we aren't using every input frame, so skip skip skip
                continue

            stageChange = processframe(self.frameNum,frame,self.cap,self.watchPoints,self.clipTotalTimeOffset)

            if self.crosshairs == 1:
                for i, w in enumerate(self.watchPoints):
                    cv2.rectangle(frame,(w.x-20,w.y),(w.x+20,w.y),(0,0,255),-1)
                    cv2.rectangle(frame,(w.x,w.y-20),(w.x,w.y+20),(0,0,255),-1)

            if stageChange:
                self.saveStateChange()

                allRed = 1
                for i, w in enumerate(self.watchPoints):
                    if w.isRed == 0:
                        allRed = 0
                log.info("stateChange,frame,%d,allRed,%d,time,%0.1f" % (self.frameNum,allRed,self.cap.get(cv2.CAP_PROP_POS_MSEC)/1000))
                for i, w in enumerate(self.watchPoints):
                    log.info(w)
                if allRed:
                    cycleOutputAtFrameNum = self.frameNum + (self.clipEndOffset*self.inputFPS)

            self.writeFrame(frame)

            showFrame(frame)

            if self.frameNum >= cycleOutputAtFrameNum:
                cycleOutputAtFrameNum = 999999999999
                self.openVideoWriter()

        # end of WhileTrue:
        log.info('closing last video writer')
        self.closeVideoWriter()

        with open('%s_jobmetadata.pickle' % self.outputPrefix, 'wb') as f:
            savedata = {
                    "clips" : self.clips,
                    "stateChanges" : self.stateChanges,
                    "watchPoints" : self.watchPoints
                    }
            pickle.dump(savedata, f, pickle.HIGHEST_PROTOCOL)

def showFrame (frame):
    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
    cv2.imshow('frame',frame)
    key = cv2.waitKey(1)

def unittest (conffile):

    cv2.namedWindow('frame')
    cv2.moveWindow('frame',100,100)

    log.info("reading json file: %s" % conffile)

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
        log.info("unexpected end of file")
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


def logger ():
    global log
    if log != None:
        return log
    lgr = logging.getLogger(__name__)
    lgr.setLevel(logging.DEBUG)

    frmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s.%(funcName)s %(message)s")

    #fh = logging.FileHandler('tv-%d.log' % now)
    #fh.setLevel(logging.DEBUG)
    #fh.setFormatter(frmt)
    #lgr.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(frmt)
    lgr.addHandler(sh)

    log = lgr;
    return log

def paint (frameNum,frame,cap,clipTimeOffset):

    vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    seconds = clipTimeOffset+(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = "%d:%02d:%02.1f" % (h, m, s)

    cv2.rectangle(frame,(0,0),(vid_width,100),(0,0,0),-1)
    cv2.putText(frame, "#%d %s" % (frameNum,time), (50,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255,255), 4)
    #cv2.putText(frame, "#%d" % (frameNum), (50,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255,255), 4)

def processframe (frameNum,frame,cap,watchPoints,clipTimeOffset):

    stageChange = 0


    paint(frameNum,frame,cap,clipTimeOffset)

    for i, w in enumerate(watchPoints):

        prevRed = w.isRed

        w.processframe(frame)

        same = (w.isRed == prevRed)
        if same == 0:
            stageChange = 1
            if w.isRed:
                w.redStart = cap.get(cv2.CAP_PROP_POS_MSEC)
            else:
                w.redStart = None
            log.info("WP(%d) state changed; frame:%d prevRed:%d isRed:%d :: %s" % (i,frameNum,prevRed,w.isRed,w))

        w.paint(frame,cap.get(cv2.CAP_PROP_POS_MSEC))

    return stageChange

log = logger()
