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

parser = argparse.ArgumentParser()
parser.add_argument('-o',metavar='output/path/prefix',help='basename of output file(s)')
parser.add_argument('-i',metavar='filename',type=file,action='append',help='Input movie file(s) with OS globbing',nargs=argparse.REMAINDER)
parser.add_argument('--outfps',metavar='10',type=int,default=10,help='FPS of output file')
parser.add_argument('--inskip',metavar='3',type=int,default=3,help='Frames to skip while reading input file') # TODO: just calculate based on INPUT_FRAMERATE/OUTFPS
args = parser.parse_args()

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
videoJob.outputPrefix = args.o
videoJob.backgroundFrameFinder()

