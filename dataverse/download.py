import os
import json
import requests
from pathlib import Path
def onefile(server, api_key,fileID,filePath:Path):
    url = '%s/api/access/datafile/%s/' % (server,fileID)
    with requests.get(url, stream=True,headers={'X-Dataverse-key':api_key}) as r:
        r.raise_for_status()
        with open(filePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return filePath

def files(server, api_key,fileIDs:list,destZipPath:Path):
    url = '%s/api/access/datafiles/' % (server)
    s = ','
    url = url + s.join(fileIDs)
    print('Url: '+url)
    with requests.get(url, stream=True,headers={'X-Dataverse-key':api_key}) as r:
        r.raise_for_status()
        with open(destZipPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return destZipPath