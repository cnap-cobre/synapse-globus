from __future__ import annotations
from typing import List
from typing import FrameType
import logging
import traceback
import enum
import datetime
import jsonpickle
import os
from pathlib import Path
from inspect import currentframe, getframeinfo

log = logging.getLogger('ksu.synapse')


class LOG_TYPE(enum.Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10


file_delim: str = '\n=========================\n'


class Entry():
    def __init__(self):
        self.job_id: str = ''
        self.date_time: datetime.datetime
        self.severity: LOG_TYPE = LOG_TYPE.DEBUG
        self.location: str = ''
        self.msg: str = ''
        self.stacktrace: str = ''
        self.details: str = ''

    def pickle(self) -> str:
        return jsonpickle.encode(self)

    def tostr(self) -> str:
        header: List[str] = [
            str(self.date_time),
            'job='+self.job_id,
            self.location,
            str(self.severity),
        ]
        msg: List[str] = [
            self.msg,
            self.details,
            self.stacktrace,
            '======================='
        ]
        return ' '.join(header) + '\n'.join(msg)

    def todisk(self, dir: str):
        dirpath = Path(dir)
        dirpath.mkdir(parents=True, exist_ok=True)
        mdpath = dirpath / (self.job_id+'.json')
        #data = self.toJSON()
        data = jsonpickle.encode(self, indent=4) + file_delim
        with open(mdpath, 'a') as f:
            f.write(data)


def from_exception(job_id: str, ex: Exception, severity: LOG_TYPE = LOG_TYPE.ERROR, additional_details: str = '') -> Entry:
    e: Entry = Entry()
    e.job_id = job_id
    e.date_time = datetime.datetime.now()
    e.severity = severity

    cf: FrameType = currentframe()
    fi = getframeinfo(cf.f_back)

    e.location = fi.filename+':'+str(fi.lineno)
    e.msg = str(ex)
    e.stacktrace = ''.join(
        traceback.TracebackException.from_exception(ex).format())
    e.details = additional_details
    return e


def from_txt(job_id: str, msg: str, details: str = '', severity: LOG_TYPE = LOG_TYPE.INFO) -> Entry:
    e: Entry = Entry()
    e.job_id = job_id
    e.date_time = datetime.datetime.now()
    e.severity = severity

    cf: FrameType = currentframe()
    fi = getframeinfo(cf.f_back)

    e.location = fi.filename+':'+str(fi.lineno)
    e.msg = msg
    e.details = details
    return e
