#!/bin/bash

in=$1
out=`echo $in | sed 's/MTS$//' | sed 's/mts$//'`"mp4"

echo $in
echo $out

/Applications/HandBrakeCLI -i $in -o $out 

