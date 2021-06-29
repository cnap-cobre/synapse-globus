import concurrent.futures
import requests
import os
import json
import time
from dataverse import xferjob
from pathlib import Path
import upload

out = []
CONNECTIONS = 100
TIMEOUT = 30

tlds = open('../data/sample_1k.txt').read().splitlines()
urls = ['http://{}'.format(x) for x in tlds[1:]]


def files(server, api_key, job: xferjob.Job, rootPath: Path):
    url:str = 
    for fd in job.files:
        if fd.path[0] == '/':
            fd.path = fd.path[1:]
        filePath = rootPath / fd.path
        onefile(server, api_key, job.dataset_id, filePath, fd.desc, fd.tags)
        #generate a list of files to be processed:
        url_dataset_id = '%s/api/datasets/%s/add?key=%s' % (server, job.dataset_id, api_key)



def load_url(server:str, api_key:str, fd:xferjob.FileData):
    res = upload.onefile(server,api_key,dataset_id,fd.)
    ans = requests.head(url, timeout=timeout)
    return ans.status_code

def uploadBatch(server, api_key, dataset_id, files):
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(upload.onefile, server,api_key, dataset_id,filepath,desc,cats) for url in urls)
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
            except Exception as exc:
                data = str(type(exc))
            finally:
                out.append(data)

                print(str(len(out)),end="\r")

        time2 = time.time()

    print(f'Took {time2-time1:.2f} s')