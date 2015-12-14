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

parser = argparse.ArgumentParser(description='Process video file of intersections')
parser.add_argument('-i',metavar='filename')
args = parser.parse_args()

with open(args.i, 'rb') as f:
    data = pickle.load(f)
    #print data
    if False:
        print ""
        print ""
        print "State Changes"
        print ""
        p = None
        for c in data['stateChanges']:
            print c
            d = c
            #d = json.loads(c)
            if p != None:
                frameDelta = d['frame'] - p['frame'];
                print "%d\t%.02f" % (frameDelta,frameDelta/30)
            p = d
        #exit(0)
        print ""
        print "Watch Points"
        print ""
        for c in data['watchPoints']:
            print c
        print ""
        print "Clips"
        print ""
        print ""
        print ""
    for c in data['clips']:
        print "%.03f\t%d\t%d\t%s" % ((c['lastFrame']-c['firstFrame'])/30,c['firstFrame'],c['lastFrame'],c['file'])
