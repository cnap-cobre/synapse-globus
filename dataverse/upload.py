import os
import json
import requests  # http://docs.python-requests.org/en/master/
from dataverse import xferjob
from pathlib import Path


def files(server, api_key, job: xferjob.Job, rootPath: Path):
    for fd in job.files:
        if fd.path[0] == '/':
            fd.path = fd.path[1:]
        filePath = rootPath / fd.path
        onefile(server, api_key, job.dataset_id, filePath, fd.desc, fd.tags)


def onefile(server, api_key, dataset_id, filepath, desc, cats):
    # # --------------------------------------------------
    # # Update the 4 params below to run this code
    # # --------------------------------------------------
    # dataverse_server = 'https://your dataverse server' # no trailing slash
    # api_key = 'api key'
    # dataset_id = 1  # database id of the dataset
    # persistentId = 'doi:10.5072/FK2/6XACVA' # doi or hdl of the dataset

    # --------------------------------------------------
    # Prepare "file"
    # --------------------------------------------------
    f = open(filepath, 'rb')
    file_content = f.read()
    files = {'file': (os.path.basename(filepath), file_content)}

    # --------------------------------------------------
    # Using a "jsonData" parameter, add optional description + file tags
    # --------------------------------------------------
    params = dict(description=desc,
                  categories=cats)

    params_as_json_string = json.dumps(params)

    payload = dict(jsonData=params_as_json_string)

    # --------------------------------------------------
    # Add file using the Dataset's id
    # --------------------------------------------------
    url_dataset_id = '%s/api/datasets/%s/add?key=%s' % (
        server, dataset_id, api_key)

    # -------------------
    # Make the request
    # -------------------
    # print('-' * 40)
    # print('making request: %s' % url_dataset_id)
    r = requests.post(url_dataset_id, data=payload, files=files)

    # -------------------
    # Print the response
    # -------------------
    # print('-' * 40)
    # print(r.json())
    # print(r.status_code)
    # return r.json()
    # # --------------------------------------------------
    # # Add file using the Dataset's persistentId (e.g. doi, hdl, etc)
    # # --------------------------------------------------
    # url_persistent_id = '%s/api/datasets/:persistentId/add?persistentId=%s&key=%s' % (dataverse_server, persistentId, api_key)

    # # -------------------
    # # Update the file content to avoid a duplicate file error
    # # -------------------
    # file_content = 'content2: %s' % datetime.now()
    # files = {'file': ('sample_file2.txt', file_content)}

    # # -------------------
    # # Make the request
    # # -------------------
    # print '-' * 40
    # print 'making request: %s' % url_persistent_id
    # r = requests.post(url_persistent_id, data=payload, files=files)

    # # -------------------
    # # Print the response
    # # -------------------
    # print '-' * 40
    # print r.json()
    # print r.status_code
