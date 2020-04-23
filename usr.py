import os
import json
from pathlib import Path
from typing import Dict
import datetime
import jsonpickle


class JobHistory():
    # Synapse Job ID
    job_id: str = ''
    src_name: str = ''
    dest_name: str = ''
    time_started: datetime.datetime
    time_ended: datetime.datetime
    bytes_xferred: int = 0
    files_xferred: int = 0
    percent_done: int = 0
    status_msg: str = ''


class settings2():
    globus_id: str
    globus_usr: str
    lab_id: str
    dv_key: str
    src_endpoint: str
    dv_key_masked: str
    dataset_id: str

    # Dict[job_id]
    job_history: Dict[str, str] = {}

    def save(self, dir: str):
        dirpath = Path(dir)
        dirpath.mkdir(parents=True, exist_ok=True)
        mdpath = dirpath / (self.globus_id+'.json')
        data = jsonpickle.encode(value=self, indent=4)
        with open(mdpath, 'w') as f:
            f.write(data)

    @staticmethod
    def load(dir: str, globus_id: str) -> settings2:
        dirpath = Path(dir)
        mdpath = dirpath / (globus_id+'.json')
        with open(mdpath, 'r') as f:
            raw: str = f.read()
        return jsonpickle.decode(raw)


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
