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
    tags = []
    globus_path:List[str] = []
    selected_globus_path:str
    #3/13/2020 - Either Globus/windows or browers do not take into account DST. So if the time
    #difference is 3600 seconds exactly. then we will make this a runner up option, if we can't find it
    #anywhere else.
    globus_path_DST_offset:List[str] = []
    
    def __init__(self,filepath:str,filesize:int,filemru:int,filedesc:str,tag_data,globus_path:List[str] = [],dst_offset_path:List[str] = [],selected_gloubs_path:str=''):
        self.path = filepath
        self.size = filesize
        self.mru = filemru
        self.desc = filedesc
        self.tags = tag_data
        self.globus_path = globus_path
        self.globus_path_DST_offset = dst_offset_path
        self.selected_globus_path = selected_gloubs_path
      
    def toJSON(self):
        formatted = self.toDict()
        return json.dumps(formatted)

    def toDict(self):
        return {'path':self.path,'size':self.size,'mru':self.mru,'desc':self.desc,'tags':self.tags,'gpath':self.globus_path,'dstpath':self.globus_path_DST_offset,'selected_globus_path':self.selected_globus_path}

    @staticmethod
    def fromDict(dd):
        return FileData(dd['path'],dd['size'],dd['mru'],dd['desc'],dd['tags'],dd['gpath'],dd['dstpath'],dd['selected_globus_path'])

    @staticmethod
    def fromJSON(data):
        dd = json.loads(data)
        return FileData.fromDict(dd)



class Job:
    dv_user_id = 0
    globus_id = ''
    globus_usr_name = ''
    dataset_id = ''
    files = []
    job_id = ''
    srcEndPoint = ''
    globus_task_id = ''

    def __init__(self, dataverse_user_id, globus_user_id, dataverse_dataset_id,job_id,globus_usr_name:str,srcEndPoint:str,globus_task_id:str):
        self.dv_user_id = dataverse_user_id
        self.globus_id = globus_user_id
        self.globus_usr_name = globus_usr_name
        self.dataset_id = dataverse_dataset_id
        self.job_id = job_id
        self.srcEndPoint = srcEndPoint
        self.globus_task_id = globus_task_id

    def toJSON(self):
        return json.dumps(self.toDict())
    
    def toDict(self):
        file_list = []
        for fd in self.files:
            file_list.append(fd.toDict())
        return {'dvusrid':self.dv_user_id,'gid':self.globus_id,'gusr':self.globus_usr_name,'dsid':self.dataset_id,'jobid':self.job_id,'srcEndPoint':self.srcEndPoint,'gtask_id':self.globus_task_id,'filedata':file_list}

    def todisk(self, directory:str):
        dirpath = Path(directory)
        dirpath.mkdir(parents=True,exist_ok=True)
        mdpath = dirpath  / (self.job_id+'.json')
        data = self.toJSON()
        with open(mdpath,'w') as f:
            f.write(data)

    @staticmethod
    def fromDict(dd):
        j = Job(dd['dvusrid'],dd['gid'],dd['dsid'],dd['jobid'],dd['gusr'],dd['srcEndPoint'],dd['gtask_id'])
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