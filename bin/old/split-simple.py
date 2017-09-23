
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
 
parser = argparse.ArgumentParser()
parser.add_argument('-o',metavar='output/path/prefix',help='basename of output file(s)')
parser.add_argument('-i',metavar='filename',help='Input movie file')
args = parser.parse_args()

cv2.namedWindow('frame')
cv2.moveWindow('frame',50,50)

cap = cv2.VideoCapture(args.i)

frameNum=0
while(cap.isOpened()):

    ret, frame = cap.read()
    if ret == False:
        exit(0)

    frameNum = frameNum+1

    if frameNum%3 == 0:
        print "%d skip" % frameNum
        continue

    print "%d process" % frameNum

    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
    cv2.imshow('frame',frame)
    key = cv2.waitKey(1)

    #outfile = "out/frame_%d_mask.jpg" % framenum
    #cv2.imwrite(outfile,fgmask)
    #outfile = "out/frame_%d_orig.jpg" % framenum
    #cv2.imwrite(outfile,grey)

cap.release()
cv2.destrowAllWindows()

