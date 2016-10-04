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
parser.add_argument('-m','--motionMask',action='count')#,const=1,help='apply motion mask')
#parser.add_argument('-c',action='store_const', const=1, help='Display crosshairs in output frames')
parser.add_argument('--outfps',metavar='10',type=int,default=10,help='FPS of output file')
parser.add_argument('--inskip',metavar='3',type=int,default=3,help='Frames to skip while reading input file') # TODO: just calculate based on INPUT_FRAMERATE/OUTFPS
#parser.add_argument('-w',metavar='x:y',action='append',help='Watchpoint in x:y format')
parser.add_argument('-o',metavar='output/path/prefix',help='basename of output file(s)')
parser.add_argument('-i',metavar='filename',type=file,action='append',help='Input movie file(s) with OS globbing',nargs=argparse.REMAINDER)

args = parser.parse_args()

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
videoJob.outFPS = args.outfps
videoJob.frameSkip = args.inskip
#videoJob.watchPoints = watchPoints
videoJob.outputPrefix = args.o
videoJob.saveStateChange()
videoJob.motion_based_background_image_finder()
exit(0)

