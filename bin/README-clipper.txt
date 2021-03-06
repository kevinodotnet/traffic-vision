

# use Handbrake to convert the videos.
tomp4.sh

# setup CV environment
source /usr/local/bin/virtualenvwrapper.sh
workon cv
# deactivate

# run clipper
d=20160919-gettler
mkdir -p ../var/$d/out
python clipper.py -o ../var/$d/out/$d-clip -i ../var/$d/*mp4

# upload MOV output to S3
aws s3 sync --acl public-read ../var/$d/out s3://s3.kevino.ca/traffic-vision/$d/

# transcode
deactivate
base=s3://s3.kevino.ca/traffic-vision/$d/
clips=`aws s3 ls $base | awk '{ print $4 }'`
for i in $clips; do echo python elastictranscoder.py transcode "$base$i"; done

#check status
python elastictranscoder.py status all

# delete original MOV from s3, they are now MP4s anyway
key="traffic-vision/$d/"; clips=`aws s3 ls s3://s3.kevino.ca/$key | grep ".mov$" | awk '{print $4}'`; 
for i in $clips; do echo aws s3 rm s3://s3.kevino.ca/$key$i; done

# on prodweb, insert a new video definition

insert into tv_point (lat,lon,title,streetview) values (null,null,'Bank and Riverside','');


insert into tv_video (point,recorded) values ((select max(id) from tv_point),'2017-09-12');

# get SQL to insert the clips
python video-clip-insert.py s3.kevino.ca traffic-vision/$d/ 5

