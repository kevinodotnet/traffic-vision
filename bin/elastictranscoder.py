import boto3
import sys
import re
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=2)

client = boto3.client('elastictranscoder')

# full S3 bucket URL, example: s3://s3.kevino.ca/traffic-vision/20151126-leiper-westwellington-harmer
action = sys.argv[1]

# all actions require the default pipeline
pipeline = None
resp = client.list_pipelines()
pipelines = resp['Pipelines']
for p in pipelines:
    if p['Name'] == 'default-pipeline':
        pipeline = p
if pipeline == None:
    print "Could not find default pipeline"
    exit(0)

if action == 'transcode':
    inkey = sys.argv[2]
    # for now we are cheating, and bucket is stripped because it is defined in AWS pipeline
    inkey = re.sub(r'^s3://[^/]+/','',inkey)
    outkey = re.sub(r'\....$','.mp4',inkey)

    presetId = '1351620000001-000010' # mp4, System preset generic 720p
    jobIn = { 'Key': inkey }
    jobOut = { 'Key': outkey, 'PresetId': presetId }
    job = client.create_job(PipelineId = pipeline['Id'],Input = jobIn,Output = jobOut)
    print ""
    pp.pprint(job)
    print ""
    exit(0)

if action == 'status':
    status = sys.argv[2]

    getmore = 1
    page_token = ''
    while getmore == 1:
        getmore = 0

        if status == 'all':
            print "Getting all jobs in default-pipelin"
            if page_token == '':
                jobs = client.list_jobs_by_pipeline(PipelineId = pipeline['Id'])
            else:
                jobs = client.list_jobs_by_pipeline(PipelineId = pipeline['Id'],PageToken = page_token)
        else:
            print "Getting jobs in status %s" % status
            if page_token == '':
                jobs = client.list_jobs_by_status(Status = status)
            else:
                jobs = client.list_jobs_by_status(Status = status, PageToken = page_token)

        #pp.pprint(jobs)
        if 'NextPageToken' in jobs:
            getmore = 1
            page_token = jobs['NextPageToken']

        for job in jobs['Jobs']:
            submitted = datetime.datetime.fromtimestamp(job['Timing']['SubmitTimeMillis']/1000.0)
            extra = ''
            if job['Status'] == 'Error':
                extra = job['Output']['StatusDetail']
            print "%s %s %s %s %s" % (submitted,job['Id'], job['Status'],job['Input']['Key'],extra)
            #pp.pprint(job)
    exit(0)

print "Unknown action: '%s'" % action

# s3 = boto3.resource('s3')
# for bucket in s3.buckets.all():
#     print(bucket.name)

