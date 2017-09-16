
# Notes:
#    http://www.amphioxus.org/content/real-time-speed-estimation-cars

import numpy as np
import cv2

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('../var/20160919-gettler/20160919_222530_shawn.gettler.mp4')

resize=1
show = None

refFrame = None

frames = 0


while(True):

    ret, frame = cap.read()

    frames += 1

    if show is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        show = np.zeros_like(gray)

    # grab a frame, monochrome
    frame = cv2.resize(frame, (0,0), fx=resize, fy=resize)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h = frame.shape[0]
    w = frame.shape[1]

#    gray[0:145,0:w] = 0
#    gray[170:h,0:w] = 0
#    gray[h,0:w] = 0

    # blur one
    # blur = cv2.GaussianBlur(gray, (21, 21), 0)

    if frames == 10:
        print "reference frame!"
        refFrame = gray
        print "w:%d h:%d" % (w,h)
        #show[0:h,w:(w*2)] = refFrame

    if frames == 10:
        cv2.waitKey(10)

    if frames > 10:
        delta = cv2.absdiff(refFrame, gray)
        delta = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        delta = cv2.dilate(delta, None, iterations=2)

        #show[h:(h*2),0:w] = delta

        (im2,cnts,z) = cv2.findContours(delta.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

        #contourFrame = gray.copy()
        contourFrame = frame
        if (len(cnts) > 0 and cv2.contourArea(cnts[0]) > 100):
            cv2.drawContours(contourFrame, cnts, -1, 1, 3)
        #show[h:(h*2),w:(w*2)] = contourFrame
        cv2.imshow('frame',contourFrame)
        cv2.imwrite("save/frame%09d.png" % frames,contourFrame)

    #show[0:h,0:w] = gray
    refFrame = gray

    key = cv2.waitKey(1) 
    # print "%d (key:%d)" % (frames,key)
    if key & 0xFF == ord('q'):
        break;
    if key & 0xFF == ord('f'):
        print "reference frame"
        refFrame = gray
        #show[0:h,w:(w*2)] = refFrame

cap.release()
cv2.destroyAllWindows()

