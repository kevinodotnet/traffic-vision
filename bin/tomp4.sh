#!/bin/bash

in=$1
out=`echo $in | sed 's/MTS$//' | sed 's/mts$//'`"mp4"
out=`echo $in | sed 's/avi$//' | sed 's/mts$//'`"mp4"

echo $in
echo $out

#echo /Applications/HandBrakeCLI --width 1920 --height 1080 -i $in -o $out 
#/Applications/HandBrakeCLI --width 1280 --height 720 -i $in -o $out 
/Applications/HandBrakeCLI -i $in -o $out 

