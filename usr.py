import os
import json
from pathlib import Path

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

def defaultVals():
    return {settings.LAB_ID:'0',settings.DV_KEY:'',settings.SRC_ENDPOINT:'',settings.DATASET_ID:'0',settings.DV_KEY_MASKED:'',settings.GLOBUS_ENDPOINTS:{}}


def _getVars():
    v = settings()

    return [attr for attr in dir(v) if not callable(getattr(settings,attr)) and not attr.startswith("__")]

def updateDisk(path:Path, session):
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
    fo = open(op,'w')
    fo.write(json.dumps(output))
    fo.close()

def load(path:Path, session):
    #Set default values.
    default_vals = defaultVals()
    for key,value in default_vals.items():
        session[key] = value

    if not os.path.exists(path):
        os.mkdir(path)
    op = path / (session[settings.GLOBUS_ID]+".json")
    if op.exists:
        try:
            fr = open(op,'r')
            vals = json.loads(fr.read())
            for key,val in vals.items():
                session[key] = val
            fr.close()
        except:
            pass