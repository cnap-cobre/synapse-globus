# https://stackoverflow.com/questions/33533148/how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel#33533514
from __future__ import annotations

import json
import datetime
import hashlib
import uuid
from pathlib import Path
from typing import List


class FileData:
    path = ''
    size = 0
    mru = 0
    desc = ''
    tags: List[str] = []
    globus_path: List[str] = []
    selected_globus_path: str
    # 3/13/2020 - Either Globus/windows or browers do not take into account DST. So if the time
    # difference is 3600 seconds exactly. then we will make this a runner up option, if we can't find it
    # anywhere else.
    globus_path_DST_offset: List[str] = []
    time_added = ''

    def __init__(self, filepath: str, filesize: int, filemru: int, filedesc: str, tag_data, globus_path: List[str] = [], dst_offset_path: List[str] = [], selected_gloubs_path: str = '', time_added: str = ''):
        self.path = filepath
        self.size = filesize
        self.mru = filemru
        self.desc = filedesc
        self.tags = tag_data
        self.globus_path = globus_path
        self.globus_path_DST_offset = dst_offset_path
        self.selected_globus_path = selected_gloubs_path
        self.time_added = time_added

    def toJSON(self):
        formatted = self.toDict()
        return json.dumps(formatted)

    def toDict(self):
        return {'path': self.path,
                'size': self.size,
                'mru': self.mru,
                'desc': self.desc,
                'tags': self.tags,
                'gpath': self.globus_path,
                'dstpath': self.globus_path_DST_offset,
                'selected_globus_path': self.selected_globus_path,
                'time_added': self.time_added}

    @staticmethod
    def fromDict(dd):
        return FileData(filepath=dd['path'],
                        filesize=dd['size'],
                        filemru=dd['mru'],
                        filedesc=dd['desc'],
                        tag_data=dd['tags'],
                        globus_path=dd['gpath'],
                        dst_offset_path=dd['dstpath'],
                        selected_gloubs_path=dd['selected_globus_path'],
                        time_added=dd['time_added'])

    @staticmethod
    def fromJSON(data):
        dd = json.loads(data)
        return FileData.fromDict(dd)


class Job:
    dv_user_id = 0
    globus_id = ''
    globus_usr_name = ''
    dataset_id = ''
    files: List[FileData] = []
    job_id = ''
    srcEndPoint = ''
    dest_endpoint = ''
    globus_task_id = ''
    job_size_bytes: int = 0

    def __init__(self, dataverse_user_id, globus_user_id, dataverse_dataset_id, job_id, globus_usr_name: str, srcEndPoint: str, globus_task_id: str = '', job_size_bytes: int = 0, dest_endpoint: str = ''):
        self.dv_user_id = dataverse_user_id
        self.globus_id = globus_user_id
        self.globus_usr_name = globus_usr_name
        self.dataset_id = dataverse_dataset_id
        self.job_id = job_id
        self.srcEndPoint = srcEndPoint
        self.globus_task_id = globus_task_id
        self.job_size_bytes = job_size_bytes
        self.dest_endpoint = dest_endpoint
        self.files = []

    def toJSON(self):
        return json.dumps(self.toDict(), indent=4, sort_keys=True)

    def toDict(self):
        file_list = []
        for fd in self.files:
            file_list.append(fd.toDict())
        return {'dvusrid': self.dv_user_id,
                'gid': self.globus_id,
                'gusr': self.globus_usr_name,
                'dsid': self.dataset_id,
                'jobid': self.job_id,
                'srcEndPoint': self.srcEndPoint,
                'gtask_id': self.globus_task_id,
                'job_size': self.job_size_bytes,
                'dest_endpoint': self.dest_endpoint,
                'filedata': file_list}

    def todisk(self, directory: str):
        dirpath = Path(directory)
        dirpath.mkdir(parents=True, exist_ok=True)
        mdpath = dirpath / (self.job_id+'.json')
        data = self.toJSON()
        with open(mdpath, 'w') as f:
            f.write(data)

    @staticmethod
    def fromdisk(job_id: str, directory: str) -> Job:
        dirpath = Path(directory)
        mdpath = dirpath / (job_id+'.json')
        with open(mdpath, 'r') as f:
            raw: str = f.read()
        d = json.loads(raw)
        return Job.fromDict(d)

    @staticmethod
    def fromDict(dd):
        j = Job(dataverse_user_id=dd['dvusrid'],
                globus_user_id=dd['gid'],
                dataverse_dataset_id=dd['dsid'],
                job_id=dd['jobid'],
                globus_usr_name=dd['gusr'],
                srcEndPoint=dd['srcEndPoint'],
                globus_task_id=dd['gtask_id'],
                job_size_bytes=dd['job_size'],
                dest_endpoint=dd['dest_endpoint'])

        for f in dd['filedata']:
            fo = FileData.fromDict(f)
            j.files.append(fo)
        return j

    @staticmethod
    def fromJSON(data):
        dd = json.loads(data)
        return Job.fromDict(dd)


def getID(dv_apiKey):
    tmp = hashlib.md5(dv_apiKey.encode('utf-8')).hexdigest()
    return tmp + '_' + dv_apiKey[:3]

# def getFilename():
#     return 'dvxfer_'+datetime.datetime.now().strftime('%Y%m%d')+'_'+str(uuid.uuid4())
