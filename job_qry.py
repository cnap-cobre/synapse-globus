import os
import json
import jsonpickle
from dataverse import xferjob


creds_path = 'synapse_chron.creds'
conf = {}
with open(creds_path, 'r') as f:
    raw = f.read()
conf = json.loads(raw)

cnt_done:int = 0
cnt_err:int = 0
cnt_pending:int = 0

fileResults = {}
jobResults = {}

filenames = next(os.walk(conf['ACTIVE_MANIFEST_DIR']))[2]
for filename in filenames:
    filepath = os.path.join(conf['ACTIVE_MANIFEST_DIR'], filename)
    job: xferjob.Job = xferjob.Job.from_disk_by_filepath(filepath)
    if not job.job_status in jobResults:
        jobResults[job.job_status] = 0
    jobResults[job.job_status] +=1

    fd: xferjob.FileData
    for fd in job.files:
        if not fd.status_code in fileResults:
            fileResults[fd.status_code] = 0
        fileResults[fd.status_code] +=1
        if fd.status_code == xferjob.FileStatus.IMPORTED:
            cnt_done += 1
        elif fd.status_code == xferjob.FileStatus.IMPORT_ERR:
            cnt_err += 1
        else:
            cnt_pending +=1
    
    for key,value in fileResults.items():
        print(key,value)

    for key,value in jobResults.items():
        print(key,value)
