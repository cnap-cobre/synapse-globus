import globus_sdk
import os
from pathlib import Path
def available_endpoints(tc:globus_sdk.TransferClient):
    result = {}
    filters = ["recently-used","my-gcp-endpoints","my-endpoints","administered-by-me","shared-with-me"]

    for filter in filters:
        tmp = tc.endpoint_search(filter_scope=filter)
        for ep in tmp:
            result[ep["id"]] = ep

    print("Endpoints Available to me:")
    for ep in result.values():
        print("[{}] {}".format(ep["id"], ep["display_name"], ep["description"], ep["canonical_name"], ep["keywords"]))
    return result

def check(tc:globus_sdk.TransferClient, files):
    """Tries to find the path in the globus
    endpoints that match the supplies file
    names, size and last modified attributes"""
    tc.endpoint_search(filter_scope="shared-with-me")


def does_share_exist(tc:globus_sdk.TransferClient,globus_usr:str):
    return os.path.exists(globus_usr)

def new_share(tc:globus_sdk.TransferClient,globus_usr:str):
    newEP = {
        'DATA_TYPE': 'shared_endpoint',
        'display_name': globus_usr,
        'host_endpoint': 'asdfafsdafsadfasdf',
        'host_path': '/'+globus_usr,
        'description': globus_usr,
        'organization': 'Kansas State University - Dataverse'
    }
    tc.create_shared_endpoint(newEP)

def transfer(tc:globus_sdk.TransferClient,srcEP, destEP,srcPathDir,destPathDir):
    srcPathDir = Path(str(srcPathDir).replace(":",""))
    destPathDir = Path(str(destPathDir).replace(":",""))

    
    tdata = globus_sdk.TransferData(tc,srcEP,destEP,label='Synapse generated, from Dataverse',sync_level='mtime',preserve_timestamp=True)
    tdata.add_item(srcPathDir,destPathDir,recursive=True)
    tresult = tc.submit_transfer(tdata)
    print('task_id='+tresult['task_id'])
    return tresult

