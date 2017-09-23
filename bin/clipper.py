import sys
import numpy as np
import cv2
import pickle
import time
import calendar
import logging
import json
import argparse
import pprint
import Queue

class ClipJob:

    secondsPerClip = 60
    cap = None
    inFiles = []
    outPrefix = ''
    outFps = 30
    frameNum = 0
    localFrameNum = 0
    clipAt = 0

    videoWriter = None

    def processFrame (self, frame):
        if self.frameNum % 10 == 0:
            sys.stdout.write('%d ' % (self.clipAt-self.frameNum))
            sys.stdout.flush()
        cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        cv2.putText(frame, "#%d" % (self.frameNum), (10,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255,255), 4)
        return frame

    def openVideoWriter(self):
        out_size = (self.vid_width,self.vid_height)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.videoWriter = cv2.VideoWriter()
        outFileName = "%s_%.09d.mov" % (self.outPrefix,self.frameNum)
        print "opening %s" % outFileName
        self.videoWriter.open(outFileName,fourcc,self.outFps,out_size,True) 

    def closeVideoWriter(self):
        self.videoWriter.release()
        self.videoWriter = None

    def process (self,inFiles,outPrefix,secondsPerClip):
        self.inFiles = inFiles
        self.outPrefix = outPrefix
        self.secondsPerClip = secondsPerClip

        ret, frame, msec = self.readFrame()
        self.outFps = self.cap.get(cv2.CAP_PROP_FPS)
        self.vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.openVideoWriter()

        clipEvery = self.outFps * self.secondsPerClip
        self.clipAt = self.frameNum + clipEvery

        while ret:

            frame = self.processFrame(frame)
            self.videoWriter.write(frame)

            if self.frameNum >= self.clipAt:
                self.closeVideoWriter()
                self.openVideoWriter()
                self.clipAt = self.frameNum + clipEvery

            ret, frame, msec = self.readFrame()

    def readFrame (self):

        if self.cap == None:
            self.capIndex = 0
            self.cap = cv2.VideoCapture(self.inFiles[self.capIndex].name)

        ret, frame = self.cap.read()
        if ret == True:
            self.frameNum += 1
            self.localFrameNum += 1
            return (True,frame,self.cap.get(cv2.CAP_PROP_POS_MSEC))

        self.cap.release()

        self.capIndex += 1
        if (self.capIndex >= len(self.inFiles)):
            return (False,None)

        self.cap = cv2.VideoCapture(self.inFiles[self.capIndex].name)
        self.localFrameNum = -1
        return self.readFrame()

pp = pprint.PrettyPrinter(indent=2)
parser = argparse.ArgumentParser(description='Clip video files into individual X second clips')
parser.add_argument('-i',metavar='filename',type=file,action='append',help='Input movie file(s) with OS globbing',nargs=argparse.REMAINDER)
parser.add_argument('-o',metavar='output/path/prefix',help='basename of output file(s)')
args = parser.parse_args()

inFiles = []
for x in args.i:
    if isinstance(x,list):
        for xx in x:
            inFiles.append(xx)
    else:
        inFiles.append(x)

clipJob = ClipJob()
clipJob.process(inFiles,args.o,60)
