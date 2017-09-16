

# export WORKON_HOME=$HOME/.virtualenvs
# source /usr/local/bin/virtualenvwrapper.sh

# to start:
# workon cv

# to end
# deactivate


from collections import deque
import numpy as np
import argparse
import imutils
import cv2
 
# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-v", "--video", help="path to the (optional) video file")
#ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
#args = vars(ap.parse_args())

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))

cap = cv2.VideoCapture("/Users/kevino/Desktop/VID_20160817_173050.mp4");

backsub = cv2.createBackgroundSubtractorMOG2()

first=1
framenum=100000

while(cap.isOpened()):

    ret, frame = cap.read()
    if ret == False:
        exit(0)

    #cv2.imshow('frame',frame)

    #grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grey = frame
    if first == 1:
        cv2.imshow('mask',grey)
        grey = np.zeros((480,704, 3), np.uint8)
        grey[:] = (255,255,255)
        cv2.moveWindow('mask',0,400)
        #cv2.moveWindow('frame',0,0)
        #print "startup; waiting for first keypress"
        #cv2.waitKey()
        first = 0

    fgmask = backsub.apply(grey, None, 0.01)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    cv2.imshow('mask',fgmask)
    cv2.waitKey(1)

    framenum = framenum + 1

    print framenum

    outfile = "out/frame_%d_mask.jpg" % framenum
    cv2.imwrite(outfile,fgmask)
    outfile = "out/frame_%d_orig.jpg" % framenum
    cv2.imwrite(outfile,grey)

    #break

#   print "waiting"
#    if cv2.waitKey(250) & 0xFF == ord('q'):
#        break

cap.release()
cv2.destrowAllWindows()

