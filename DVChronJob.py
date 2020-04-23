import os
import requests
from pathlib import Path
import datetime
from dataverse import xferjob
from dataverse import upload
from typing import List
from typing import Dict
import globus
import db
import json

download_dir = "c:/temp/globus_xfers/xfers"
server = ""
active_manifest_dir = "c:/temp/globus_xfers/active_manifests"
archived_manifest_dir = "c:/temp/globus_xfers/archived_manifests"
creds_path = 'c:/temp/synapse_chron.creds'


def execute():

    conf: Dict[str, str] = {}
    with open(creds_path, 'r') as f:
        raw = f.read()
    conf = json.loads(raw)

    # Load our current manifest list.
    manifests = {}
    filenames = next(os.walk(conf['ACTIVE_MANIFEST_DIR']))[2]
    for filename in filenames:
        filepath = os.path.join(conf['ACTIVE_MANIFEST_DIR'], filename)
        job: xferjob.Job = xferjob.Job.from_disk_by_filepath(filepath)
        manifests[job.job_id] = job

    # Check to see if there are new jobs we need to add.
    job_dirs = next(os.walk(conf['GLOBUS_DEST_DIR']))[1]
    for d in job_dirs:
        if not d in manifests:
            j: Job = download_manifest(server, d, conf['ACTIVE_MANIFEST_DIR'])
            if j != None:
                manifests[j.job_id] = j

    # Check to see if any jobs are done transferring.
    store: db.DB = db.DB(creds_path)
    api_keys: List[str] = []
    j: xferjob.Job

    for j in manifests.values():
        res = globus.svr_transfer_status(
            creds_path, j.globus_task_id)
        print(str(res))
        if res['status'] == 'SUCCEEDED':
            # We need to import. If we don't already have a
            # api key list. Let's grab it from the db.
            if len(api_keys) == 0:
                api_keys = store.execute(store.get_dv_api_keys)
            # Import into dataverse.
            print(api_keys)
            apikey: str = lookup_api_key(api_keys, j.dv_user_id)
            if apikey == '':
                raise Exception("Cannot find apikey for jobid "+j.job_id)
            fd: xferjob.fileData = None
            jobstarttime = datetime.datetime.now()
            for fd in j.files:
                if fd.status_code == xferjob.FileStatus.IMPORTED:
                    continue
                filepath = (conf['GLOBUS_DEST_DIR'] + "/" +
                            j.job_id+"/"+fd.path).replace("//", "/")
                starttime = datetime.datetime.now()
                fd.import_result = upload.onefile(server=conf['DATAVERSE_BASE_URL'],
                                                  api_key=apikey,
                                                  dataset_id=j.dataset_id,
                                                  filepath=filepath,
                                                  desc=fd.desc,
                                                  cats=fd.tags)
                if (fd.import_result['status'] == 'OK' or
                        (fd.import_result['status'] == 'ERROR' and 'This file already exists' in fd.import_result['message'])):
                    fd.import_duration = datetime.datetime.now() - starttime
                    fd.status_code = xferjob.FileStatus.IMPORTED
                    fd.time_imported = datetime.datetime.now()
                else:
                    fd.status_code = xferjob.FileStatus.IMPORT_ERR
                    print("Error Importing file: "+fd.import_result['message'])
                j.todisk(conf['ACTIVE_MANIFEST_DIR'])
            j.total_import_time = datetime.datetime.now() - jobstarttime
            j.todisk(conf['ACTIVE_MANIFEST_DIR'])
            print("Done!")
    #


def lookup_api_key(keys: List[str], encoded_key: str) -> str:

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
