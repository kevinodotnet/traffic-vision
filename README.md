# traffic-vision
Python/OpenCV software to split traffic intersection video into individual clips; www GUI to crowdsource counting and observations

Code that processed the video that is currently up for data capture over at http://app.kevino.ca/traffic-video/

# Procedure

Convert the input videos to a format that OpenCV can deal with. Below multiple MTS files taken directly
from a video camera SD card are converted to MP4 using the HandbrakeCLI application (osx)

    for i in *MTS; do 
        ~/code/traffic-vision/bin/tomp4.sh $i; 
    done


