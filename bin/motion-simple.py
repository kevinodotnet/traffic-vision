#!/usr/bin/python

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
import cv2
import pickle
import numpy

#
# http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
#
 
# initialize the camera and grab a reference to the raw camera capture

w=640
h=480

h=640
w=480
s=2

w=w/s
h=h/s
camera = PiCamera()
camera.resolution = (w,h)
camera.brightness = 60
#camera.framerate = 32
camera.rotation = 90
rawCapture = PiRGBArray(camera, size=(w,h))
#rawCapture = PiRGBArray(camera)
 
# allow the camera to warmup
time.sleep(0.1)

prevFrame = None
 
# capture frames from the camera
images = [] 
count = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

  image = frame.array

  gray = cv2.cvtColor(frame.array, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  if prevFrame is None:
    prevFrame = gray
    rawCapture.truncate(0)
    continue

  show = False
  frameDelta = cv2.absdiff(prevFrame, gray)
  thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
  thresh = cv2.dilate(thresh, None, iterations=2)
  (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  print cnts
  for c in cnts:
    print "%d" % cv2.contourArea(c)
    if cv2.contourArea(c) < 5: #args["min_area"]:
      continue
    (x, y, w, h) = cv2.boundingRect(c)
    show = True
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

  count = count + 1
  prevFrame = gray
  if show:
    filename = 'out/%s_%d.jpg' % (time.strftime("%Y%m%d_%H%M%S", time.gmtime()),count)
    print '%d filename %s' % (count,filename)
    #cv2.imwrite(filename, image)
    images.append([filename,image])
    #cv2.imshow("Frame", image)
    #cv2.imshow("2", thresh)

  if len(images) >= 10:
    break
  key = cv2.waitKey(1) & 0xFF
  if key == ord("q"):
    break

  #file = open(filename, 'w')
  #pickle.dump(image, file)
  #file.close()
 
  # clear the stream in preparation for the next frame
  rawCapture.truncate(0)

count = 0
for rec in images:
  (filename,image) = rec
  print "writing %s" % filename
  cv2.imwrite(filename, image)
  
  
  # if the `q` key was pressed, break from the loop
