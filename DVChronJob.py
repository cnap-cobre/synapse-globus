import os
import requests
from pathlib import Path
from datetime import datetime
from dataverse import xferjob
from dataverse import upload
import globus
import db

download_dir = "c:/temp/globus_xfers/xfers"
server = "http://localhost:5000"
active_manifest_dir = "c:/temp/globus_xfers/active_manifests"
archived_manifest_dir = "c:/temp/globus_xfers/archived_manifests"
creds_path = 'c:/temp/synapse.creds'


def execute():
    # Load our current manifest list.
    manifests = {}
    filenames = next(os.walk(active_manifest_dir))[2]
    for filename in filenames:
        filepath = os.path.join(active_manifest_dir, filename)
        job: xferjob.Job = xferjob.Job.from_disk_by_filepath(filepath)
        manifests[job.job_id] = job

    # Check to see if there are new jobs we need to add.
    job_dirs = next(os.walk(download_dir))[1]
    for d in job_dirs:
        if not d in manifests:
            j: Job = download_manifest(server, d, active_manifest_dir)
            if j != None:
                manifests[j.job_id] = j

    # Check to see if any jobs are done transferring.
    j:xferjob.Job
    for j in manifests.values():
        res = globus.svr_transfer_status(
            creds_path, j.globus_task_id)
        print(str(res))
        if res['status'] == 'SUCCEEDED':
            # Import into dataverse.
            apikey:str = lookup_api_key(j.dv_user_id)
            

    #


def lookup_api_key(encoded_key: str) -> str:
    store: db.DB = db.DB(usr='dvnuser', passcode='dvnsecret')
    keys = store.get_dv_api_keys()
    # hash = encodedkey[:-4]
    # checksum = encodedkey[-3:]
    candidate: str = ''
    for key in keys:
        if xferjob.getID(key) == encoded_key:
            if len(candidate) > 1:
                # We already have a key. THIS SHOULDN'T HAPPEN!!!
                # Let's Fail Horribly!
                raise Exception(
                    "Found multiple apikeys with identical hashes + checksum!!: "+encoded_key)
            candidate = key
    return candidate


def import_file(fd: xferjob.FileData, job: xferjob.Job):

    upload.onefile(server='asdf', api_key='asdf', dataset_id=job.dataset_id,
                   filepath=path, desc=fd.desc, cats=fd.tags)


def download_manifest(server_uri: str, job_id: str, active_manifest_dir: str) -> xferjob.Job:
    url = '%s/pending' % (server_uri)
    url = url + '?jid='+job_id
    data: str = ''
    with requests.get(url) as raw:
        data = raw.text
    if len(data) < 1:
        # This means we're not authenticated or an invalid job id was given.
        print("Invalid Data.")
        return None
    dirpath = Path(active_manifest_dir)
    dirpath.mkdir(parents=True, exist_ok=True)
    mdpath = dirpath / (job_id+'.json')
    with open(mdpath, 'w') as f:
        f.write(data)

    job: xferjob.Job = xferjob.Job.fromdisk(job_id, active_manifest_dir)
    return job


execute()
