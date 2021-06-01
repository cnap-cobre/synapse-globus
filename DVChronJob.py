import os
import requests
from pathlib import Path
import datetime
from dataverse import xferjob
from dataverse import upload
from dataverse import dataset
from typing import List
from typing import Dict
import globus
import db
import json
import usr
import jsonpickle
import time
import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s->%(funcName)s:(%(lineno)d) %(threadName)s %(message)s')
logFile = 'synapse_dataverse_service.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=False)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(my_handler)
log.addHandler(logging.StreamHandler())

creds_path = 'synapse_chron.creds'


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
    job_dirs = next(os.walk(conf['GLOBUS_TRANSFERS_TO_DATAVERSE_PATH']))[1]
    for d in job_dirs:
        if not d in manifests:
            j: Job = download_manifest(
                conf['SYNAPSE_SERVER'], d, conf['ACTIVE_MANIFEST_DIR'])
            if j != None:
                manifests[j.job_id] = j

    # Check to see if any jobs are done transferring.
    store: db.DB = db.DB(creds_path)


    # #This logic is used to retrieve stats from a given dataset
    # #For use in analytics / piestar applications.
    # dataset_id = 17
    # stats: Dict = dataset.getDatasetInfo(conf['DATAVERSE_BASE_URL'], dataset_id, store)
    # temp_output: str = json.dumps(stats, indent=4, sort_keys=True, default=str)
    # with open("exampleStats.json", 'w') as f:
    #     f.write(temp_output)
    # #End dataset stat info...



    api_keys: List[str] = []
    j: xferjob.Job

    for j in manifests.values():

        if j.job_status == xferjob.JobStatus.COMPLETED:
            continue

        res = globus.svr_transfer_status(
            creds_path, j.globus_task_id)
        print(str(res))

        # Post status update.
        update: usr.JobUpdate = usr.JobUpdate.fromGlobusTaskObj(
            j.globus_id, j.job_id, len(j.files), 1, res)
        post_status_update(conf['SYNAPSE_SERVER'], update)

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
            import_files(j, conf, apikey)
            # jobstarttime = datetime.datetime.now()
            # for fd in j.files:
            #     if fd.status_code == xferjob.FileStatus.IMPORTED:
            #         continue
            #     filepath = (conf['GLOBUS_DEST_DIR'] + "/" +
            #                 j.job_id+"/"+fd.path).replace("//", "/")
            #     starttime = datetime.datetime.now()
            #     fd.import_result = upload.onefile(server=conf['DATAVERSE_BASE_URL'],
            #                                       api_key=apikey,
            #                                       dataset_id=j.dataset_id,
            #                                       filepath=filepath,
            #                                       desc=fd.desc,
            #                                       cats=fd.tags)
            #     if (fd.import_result['status'] == 'OK' or
            #             (fd.import_result['status'] == 'ERROR' and 'This file already exists' in fd.import_result['message'])):
            #         fd.import_duration = datetime.datetime.now() - starttime
            #         fd.status_code = xferjob.FileStatus.IMPORTED
            #         fd.time_imported = datetime.datetime.now()
            #     else:
            #         fd.status_code = xferjob.FileStatus.IMPORT_ERR
            #         print("Error Importing file: "+fd.import_result['message'])
            #     j.todisk(conf['ACTIVE_MANIFEST_DIR'])
            # j.total_import_time = datetime.datetime.now() - jobstarttime
            # j.todisk(conf['ACTIVE_MANIFEST_DIR'])
            # print("Done!")


def import_files(j: xferjob.Job, conf: Dict[str, str], apikey: str):
    status: usr.JobUpdate = usr.JobUpdate(
        j.globus_id, j.job_id, 55, 'Importing into Dataverse...')
    status.finished_globus = True
    cnt_done: int = 0
    errs: List[str] = []
    # We might be resuming after an interruption. Let's check.
    fd: xferjob.FileData
    for fd in j.files:
        if fd.status_code == xferjob.FileStatus.IMPORTED:
            cnt_done += 1
    status.percent_done = usr.calcProgress(2, cnt_done / len(j.files))
    post_status_update(conf['SYNAPSE_SERVER'], status)
    jobstarttime = datetime.datetime.now()
    for fd in j.files:
        if fd.status_code == xferjob.FileStatus.IMPORTED:
            continue
        filepath = (conf['GLOBUS_TRANSFERS_TO_DATAVERSE_PATH'] + "/" +
                    j.job_id+"/"+fd.path).replace("//", "/")
        starttime = datetime.datetime.now()
        try:
            fd.import_result = upload.onefile(server=conf['DATAVERSE_BASE_URL'],
                                              api_key=apikey,
                                              dataset_id=j.dataset_id,
                                              filepath=filepath,
                                              desc=fd.desc,
                                              cats=fd.tags)

        except Exception as ex2:
            fd.import_result = {'status': 'ERROR', 'message': str(ex2)}

        if (fd.import_result['status'] == 'OK' or
                (fd.import_result['status'] == 'ERROR' and 'This file already exists' in fd.import_result['message'])):
            fd.import_duration = datetime.datetime.now() - starttime
            fd.status_code = xferjob.FileStatus.IMPORTED
            fd.time_imported = datetime.datetime.now()
        else:
            fd.status_code = xferjob.FileStatus.IMPORT_ERR
            fd.status_details = str(fd.import_result)
            log.warning("Error Importing file: "+fd.import_result['message'])
            status.error = True
            status.status_msg = "Error Importing " + \
                fd.path+": "+fd.import_result['message']
        j.todisk(conf['ACTIVE_MANIFEST_DIR'])
        cnt_done += 1
        status.percent_done = usr.calcProgress(2, cnt_done / len(j.files))
        post_status_update(conf['SYNAPSE_SERVER'], status)
    j.job_status = xferjob.JobStatus.COMPLETED
    j.total_import_time = datetime.datetime.now() - jobstarttime
    j.todisk(conf['ACTIVE_MANIFEST_DIR'])
    j.todisk(conf['ARCHIVED_MANIFEST_DIR'])
    status.percent_done = 100
    status.status_msg = 'Job completed ' + datetime.datetime.now().ctime()
    post_status_update(conf['SYNAPSE_SERVER'], status)
    print("Done!")


def post_status_update(server_uri: str, status: usr.JobUpdate):
    log.info(status.job_id + ' '+str(status.percent_done)+' '+status.status_msg)
    data: str = jsonpickle.encode(status)
    url = '%s/updateFromDV' % (server_uri)
    r = requests.post(url, data)
    print(str(r))


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


def clean_up_xfer():
    """  After a period of time (a week?) clean up a job.
        - delete xfer_download data. & Directory
        - remove globus share
        - Move manifest to archive.
    """
    pass


def download_manifest(server_uri: str, job_id: str, active_manifest_dir: str):
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


# v: str = input("Press Enter to execute Chron Job loop. Type exit to quit.")
while True:
    # v = input("Press Enter to execute Chron Job loop. Type exit to quit.")
    # if v.lower() != 'exit':
    start: datetime.datetime = datetime.datetime.now()
    execute()
    endtime: datetime.datetime = datetime.datetime.now()
    log.debug("Sec to execute loop: "+str((endtime - start).total_seconds()))
    time.sleep(5)
    # else:
    #     exit()
