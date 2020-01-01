import os
import json

class settings():
    LAB_ID = 'LAB_ID'
    DV_KEY = 'DV_KEY'
    GLOBUS_USER = 'GLOBUS_USER'
    GLOBUS_ID = 'GLOBUS_ID'
    SRC_ENDPOINT = 'SRC_ENDPOINT'
    DATASET_ID = 'DATASET_ID'

def defaultVals():
    return {settings.LAB_ID:'0',settings.DV_KEY:'',settings.SRC_ENDPOINT:'',settings.DATASET_ID:'0'}


def _getVars():
    v = settings()

    return [attr for attr in dir(v) if not callable(getattr(settings,attr)) and not attr.startswith("__")]

def updateDisk(path:str, session):
    output = {}
    v = _getVars()
    for key in v:
        if key in session:
            output[key] = session[key]
    op = os.path.join(path,session[settings.GLOBUS_ID]+".json")
    fo = open(op,'w')
    fo.write(json.dumps(output))
    fo.close()

def load(path:str, session):
    #Set default values.
    default_vals = defaultVals()
    for key,value in default_vals.items():
        session[key] = value

    if not os.path.exists(path):
        os.mkdir(path)
    op = os.path.join(path,session[settings.GLOBUS_ID]+".json")
    if os.path.exists(op):
        try:
            fr = open(op,'r')
            vals = json.loads(fr.read())
            for key,val in vals.items():
                session[key] = val
            fr.close()
        except:
            pass