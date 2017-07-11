import boto3
import sys
import re
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=2)

client = boto3.client('s3')

bucket = sys.argv[1]
prefix = sys.argv[2]
videoid = sys.argv[3]
paginator = client.get_paginator('list_objects')

# print "bucket %s prefix %s video %s" % (bucket,prefix,videoid)

for page in paginator.paginate(Bucket=bucket,Prefix=prefix):
    for o in page['Contents']:
        if re.search('mp4',o['Key']):
            url = "http://%s/%s" % (bucket,o['Key'])
            print " insert into tv_videoclip (video,url) values (%s,'%s'); " % (videoid,url)

