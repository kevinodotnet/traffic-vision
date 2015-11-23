import boto3

# http://boto3.readthedocs.org/en/latest/reference/services/elastictranscoder.html

client = boto3.client('elastictranscoder')

pipeline = None

resp = client.list_pipelines()
pipelines = resp['Pipelines']
for p in pipelines:
    if p['Name'] == 'default-pipeline':
        pipeline = p

if pipeline == None:
    print "Could not find default pipeline"
    exit(0)

if True:
    jobs = client.list_jobs_by_pipeline(PipelineId = pipeline['Id'])
    jobs = client.list_jobs_by_status(Status = 'Error')
    for job in jobs['Jobs']:
        print "%s :: %s" % (job['Id'],job['Status'])
        if job['Status'] == 'Error':
            print job['Output']['StatusDetail']
            print ""
    exit(0)

presetId = '1351620000001-000010' # mp4, System preset generic 720p

for i in range(1002,1100):
    jobIn = { 'Key': 'tmp/leiper_traffic_video/20151113_islandpark_byron_%d.mov' % i}
    jobOut = { 'Key': 'tmp/leiper_traffic_video/20151113_islandpark_byron_%d.mp4' % i, 'PresetId': presetId }
    job = client.create_job(PipelineId = pipeline['Id'],Input = jobIn,Output = jobOut)
    print job

exit(0)


print jobIn
print jobOut

print job


# s3 = boto3.resource('s3')
# for bucket in s3.buckets.all():
#     print(bucket.name)

