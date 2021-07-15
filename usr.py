from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict
import datetime
import jsonpickle
from dataverse import xferjob


class JobHistory():

    def __init__(self, globus_id: str):
        # Synapse Job ID
        self.job_id: str = ''
        self.globus_id: str = globus_id
        self.src_name: str = ''
        self.dest_name: str = ''
        self.time_started: datetime.datetime
        self.time_ended: datetime.datetime
        self.bytes_xferred: int = 0
        self.total_bytes: int = 0
        self.files_xferred: int = 0
        self.total_files: int = 0
        # self.percent_done: int = 0
        # self.status_msg: str = ''
        # self.error: bool = False
        # src/dest_type: 0=Generic Globus Endpoint, 1=Dataverse, 2=Beocat
        self.src_type: xferjob.EndPointType = xferjob.EndPointType.GLOBUS_EP
        self.dest_type: xferjob.EndPointType = xferjob.EndPointType.DATAVERSE
        self.globus_task_id: str = ''
        self.last_update: JobUpdate = JobUpdate(globus_id)


class JobUpdate():

    def __init__(self, globus_id: str, job_id: str = '', percent_done: int = 0, msg: str = ''):
        # Used to identify which progress bar to update.
        self.job_id: str = job_id
        # Used to identify which active session(s) this update should be routed to.
        self.globus_id: str = globus_id
        self.percent_done: int = percent_done
        self.status_msg: str = msg
        self.error: bool = False
        self.warning: bool = False
        self.step: int = 0
        self.finished_globus: bool = False

    @staticmethod
    # Step: 0 = Init & placed on queue. 1, 2
    def fromGlobusTaskObj(globus_id: str, job_id: str, total_files: int, step: int, res: Dict) -> JobUpdate:
        # print("FROM GLOBUS TASK OBJ:",str(res))
        xfered: int = res['data']['files_transferred']
        skipped: int = res['data']['files_skipped']
        bps: int = res['data']['effective_bytes_per_second']
        mbps: float = float(bps / 1024 / 1024)
        cntdone: int = xfered+skipped
        prog: int = 5
        if total_files > 0:
            prog = calcProgress(step, cntdone/total_files)

        update: JobUpdate = JobUpdate(globus_id, job_id, prog)
        update.step = step

        update.status_msg = 'Step '+str(step+1)+' of 3: '

        if res['data']['status'] == 'SUCCEEDED':
            if step == 2:
                dt = datetime.datetime.fromisoformat(
                    res['data']['completion_time']).astimezone()
                update.status_msg = 'Transfer completed '+str(dt)+'. '
            else:
                update.status_msg += 'Globus Transfer Complete. '
            update.finished_globus = True
        elif res['data']['status'] == 'ACTIVE':
            update.status_msg += 'Transferring via Globus. '
        elif res['data']['status'] == 'INACTIVE':
            update.status_msg += 'Need to refresh Globus credentials. '
            update.warning = True
        elif res['data']['status'] == 'FAILED':
            update.status_msg += 'Globus Transfer Failed. See Logs. '
            update.error = True
        update.status_msg += str(xfered)+' copied, '+str(skipped) + \
            " skipped "+str(round(mbps, 3))+' MB/sec'

        return update


def calcProgress(step: int, stepPercent: float) -> int:
    if step == 0:
        return 5
    if step == 1:
        return 5+int(stepPercent * 100 * .5)
    if step == 2:
        return 55+int(stepPercent * 100 * .45)
    raise NotImplementedError("Haven't implemented step "+str(step))


class Settings2():

    def __init__(self, globus_id: str):
        self.globus_id = globus_id
        self.globus_usr: str = ''
        self.lab_id: str = ''
        self.dv_key: str = ''
        self.src_endpoint: str = ''
        self.dataset_id: str = '0'
        self.job_history: Dict[str, JobHistory] = {}
        # Dict[job_id]

    @property
    def dv_key_masked(self) -> str:
        res: str = "*" + self.dv_key[-4:]
        if len(res) == 1:
            return ''
        return res

    def save(self, dir: str):
        dirpath = Path(dir)
        dirpath.mkdir(parents=True, exist_ok=True)
        mdpath = dirpath / (self.globus_id+'.json')
        data = jsonpickle.encode(value=self, indent=4)
        with open(mdpath, 'w') as f:
            f.write(data)

    @staticmethod
    def load(dir: str, globus_id: str) -> Settings2:
        if not os.path.exists(dir):
            os.mkdir(dir)
        op = Path(dir) / (globus_id+".json")
        if op.exists():
            with open(op, 'r') as f:
                raw: str = f.read()
            return jsonpickle.decode(raw)
        else:
            return Settings2(globus_id)


class settings():
    LAB_ID = 'LAB_ID'
    DV_KEY = 'DV_KEY'
    GLOBUS_USER = 'GLOBUS_USER'
    GLOBUS_ID = 'GLOBUS_ID'
    SRC_ENDPOINT = 'SRC_ENDPOINT'
    DATASET_ID = 'DATASET_ID'
    DV_KEY_MASKED = 'DV_KEY_MASKED'
    DV_FILE_ID = 'DV_FILE_ID'
    DV_DATASET_ID = 'DV_DATASET_ID'
    GLOBUS_ENDPOINTS = 'GLOBUS_ENDPOINTS'

    # Dict[job_id,JobHistory]
    JOB_HISTORY: Dict[str, JobHistory] = {}


def defaultVals():
    return {settings.LAB_ID: '0', settings.DV_KEY: '', settings.SRC_ENDPOINT: '', settings.DATASET_ID: '0', settings.DV_KEY_MASKED: '', settings.GLOBUS_ENDPOINTS: {}}


def _getVars():
    v = settings()

    return [attr for attr in dir(v) if not callable(getattr(settings, attr)) and not attr.startswith("__")]


def updateDisk(path: Path, session):
    output = {}
    v = _getVars()
    for key in v:
        if key == settings.DV_FILE_ID:
            continue
        elif key == settings.DV_DATASET_ID:
            continue
        elif key == settings.GLOBUS_ENDPOINTS:
            continue
        elif key in session:
            output[key] = session[key]
    op = path / (session[settings.GLOBUS_ID]+".json")
    fo = open(op, 'w')
    fo.write(json.dumps(output))
    fo.close()


def load(path: Path, session):
    # Set default values.
    default_vals = defaultVals()
    for key, value in default_vals.items():
        session[key] = value

    if not os.path.exists(path):
        os.mkdir(path)
    op = path / (session[settings.GLOBUS_ID]+".json")
    if op.exists:
        try:
            fr = open(op, 'r')
            vals = json.loads(fr.read())
            for key, val in vals.items():
                session[key] = val
            fr.close()
        except:
            pass
