import json
import datetime
import hashlib
import uuid
class FileData:
    path = ''
    size = 0
    mru = 0
    desc = ''
    tags = []
    globus_path = ''
    
    def __init__(self,filepath:str,filesize:int,filemru:int,filedesc:str,tag_data):
        self.path = filepath
        self.size = filesize
        self.mru = filemru
        self.desc = filedesc
        self.tags = tag_data
      
    def toJSON(self):
        formatted = self.toDict()
        return json.dumps(formatted)

    def toDict(self):
        return {'path':self.path,'size':self.size,'mru':self.mru,'desc':self.desc,'tags':self.tags}

    @staticmethod
    def fromDict(dd):
        return FileData(dd['path'],dd['size'],dd['mru'],dd['desc'],dd['tags'])

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