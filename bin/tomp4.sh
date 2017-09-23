#!/bin/bash

in=$1
out=`echo $in | sed 's/MTS$//' | sed 's/mts$//'`"mp4"
#out=`echo $in | sed 's/avi$//' | sed 's/mts$//'`"mp4"

echo $in
echo $out

/Applications/HandBrakeCLI --rate 30 --width 1024 --height 576 -i $in -o $out 

