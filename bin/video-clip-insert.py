import boto3
import sys
import re
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=2)

client = boto3.client('s3')

bucket = sys.argv[1]
prefix = sys.argv[2]
paginator = client.get_paginator('list_objects')

for page in paginator.paginate(Bucket=bucket,Prefix=prefix):
    for o in page['Contents']:
        if re.search('mp4',o['Key']):
            url = "http://%s/%s" % (bucket,o['Key'])
            print url

