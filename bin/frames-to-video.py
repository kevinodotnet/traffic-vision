
# export WORKON_HOME=$HOME/.virtualenvs
# source /usr/local/bin/virtualenvwrapper.sh
# workon cv

from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import os.path

framenum=100000
framenum=100002

backgroundNum=108255
#backgroundNum=100166

backgroundFile = "out/frame_%d_orig.jpg" % backgroundNum
backgroundFrame = cv2.imread(backgroundFile,0)

cv2.imshow('orig',backgroundFrame)
cv2.imshow('mask',backgroundFrame)
cv2.moveWindow('orig',0,0)
cv2.moveWindow('mask',0,400)

while True:

    framenum=framenum+1
    print framenum

    maskfile = "out/frame_%d_mask.jpg" % framenum
    finalFile = "out/frame_%d_final.jpg" % framenum
    if os.path.isfile(maskfile) == False:
        break

    mask = cv2.imread(maskfile,0)
    final = cv2.bitwise_or(backgroundFrame,mask)
    cv2.imwrite(finalFile,final)

    #cv2.imshow('orig',orig)
    #cv2.imshow('mask',mask)
    #cv2.imshow('mask',final)

print "DONE"

