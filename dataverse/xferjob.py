# https://stackoverflow.com/questions/33533148/how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel#33533514
from __future__ import annotations

import json
import datetime
import hashlib
import uuid
from pathlib import Path
from typing import List
from typing import Dict
import enum


class FileStatus(enum.Enum):
    # File has been transferred to the dataverse server
    # and is awaiting import.
    PENDING_IMPORT = 100

    # File has started being imported into Dataverse.
    IMPORTING = 200

    # File has been imported into dataverse.
    IMPORTED = 300

    # An unrecoverable occurred during import see value of status_msg
    IMPORT_ERR = 400

    # def __eq__(self, other):
    #     return self.value == other.value


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
    time_imported: datetime.datetime
    import_duration: datetime.timedelta = datetime.timedelta(-1)
    import_result: Dict[str, str] = {}

    # IMPORTING: File has started being imported into Dataverse.
    # IMPORTED: Final state. The file has successfully be imported into Dataverse.
    # IMPORT_ERR: An unrecoverable error occurred while importing.
    status_code: FileStatus = FileStatus.PENDING_IMPORT

    def __init__(self, filepath: str, filesize: int, filemru: int, filedesc: str, tag_data, globus_path: List[str] = [], dst_offset_path: List[str] = [], selected_gloubs_path: str = ''):
        self.path = filepath
        self.size = filesize
        self.mru = filemru
        self.desc = filedesc
        self.tags = tag_data
        self.globus_path = globus_path
        self.globus_path_DST_offset = dst_offset_path
        self.selected_globus_path = selected_gloubs_path
        self.time_imported = datetime.datetime.min

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
                'time_imported': self.time_imported,
                'status_code': self.status_code.name,
                'import_duration': self.import_duration,
                'import_result': self.import_result
                }

    @staticmethod
    def fromDict(dd):
        fd: FileData = FileData(filepath=dd['path'],
                                filesize=dd['size'],
                                filemru=dd['mru'],
                                filedesc=dd['desc'],
                                tag_data=dd['tags'],
                                globus_path=dd['gpath'],
                                dst_offset_path=dd['dstpath'],
                                selected_gloubs_path=dd['selected_globus_path']
                                )
        if 'import_duration' in dd:
            fd.import_duration = dd['import_duration']
        if 'import_result' in dd:
            fd.import_result = dd['import_result']
        if 'time_imported' in dd:
            fd.time_imported = dd['time_imported']
        if 'status_code' in dd:
            fd.status_code = FileStatus[dd['status_code']]
        return fd

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
    msglog: List[str] = []
    notified: bool = False
    total_import_time: datetime.timedelta = datetime.timedelta(-1)
    job_status:str = ''
    last_updated:str = ''
    percent_done:int = 0

    def __init__(self, dataverse_user_id, globus_user_id, dataverse_dataset_id, job_id, globus_usr_name: str, srcEndPoint: str, globus_task_id: str = '', job_size_bytes: int = 0, dest_endpoint: str = '', log: List[str] = []):
        self.dv_user_id = dataverse_user_id
        self.globus_id = globus_user_id
        self.globus_usr_name = globus_usr_name
        self.dataset_id = dataverse_dataset_id
        self.job_id = job_id
        self.srcEndPoint = srcEndPoint
        self.globus_task_id = globus_task_id
        self.job_size_bytes = job_size_bytes
        self.dest_endpoint = dest_endpoint
        self.msglog = log
        self.files = []
        self.total_import_time = datetime.timedelta(-1)

    def log(self, msg: str):
        self.msglog.append(str(datetime.datetime.now())+' '+msg)

    def loglist(self, msgs: List[str]):
        self.msglog += msgs

    def toJSON(self):
        return json.dumps(self.toDict(), indent=4, sort_keys=True, default=str)

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
                'log': self.msglog,
                'notified': self.notified,
                'total_import_time': self.total_import_time,
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
        return Job.from_disk_by_filepath(str(mdpath))

    @staticmethod
    def from_disk_by_filepath(filepath: str) -> Job:
        with open(filepath, 'r') as f:
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
                dest_endpoint=dd['dest_endpoint'],
                log=dd['log']
                )
        if 'total_import_time' in dd:
            j.total_import_time = dd['total_import_time']
        if 'notified' in dd:
            j.notified = dd['notified']

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
    return tmp + '_' + dv_apiKey[-3:]

# def getFilename():
#     return 'dvxfer_'+datetime.datetime.now().strftime('%Y%m%d')+'_'+str(uuid.uuid4())
