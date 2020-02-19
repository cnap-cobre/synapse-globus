import globus_sdk
import os
from pathlib import Path
import copy
from enum import Enum
import sys

class GResultType(Enum):
    SUCCESS = 1
    REDIRECT = 2
    NOT_LOGGED_IN = 3
    ERROR = 4
    NOT_COMPLETE = 5

class GResult:
    result_type:GResultType = GResultType.NOT_COMPLETE
    obj = None
    err = None
    msg = None

    def __init__(self, result_type:GResultType,result_obj = None, err = None, msg = None):
        self.result_type = result_type
        self.obj = result_obj
        self.err = err
        self.msg = msg
    

class GO:
    tc:globus_sdk.TransferClient = None
    use_client_credentials = True
    def __init__(self, use_client_credentials:bool):
        self.use_client_credentials = use_client_credentials
        
def getGlobusObj(session):
    res = GResult
    if not session.get('is_authenticated'):
        res.result_type = GResultType.NOT_LOGGED_IN
        return res
    authorizer = globus_sdk.AccessTokenAuthorizer(
       session['tokens']['transfer.api.globus.org']['access_token'])
    transfer_client = globus_sdk.TransferClient(authorizer=authorizer)
    return transfer_client


# def globusDo(func, tc:globus_sdk.TransferClient, **kwargs):
#     if tc is None:
#         tc = getGlobusObj()
#     try:
#         if (usr.settings.GLOBUS_ID not in session) or (len(session[usr.settings.GLOBUS_ID]) < 5):
#             auth2 = globus_sdk.AccessTokenAuthorizer(session['tokens']['auth.globus.org']['access_token'])
#             client = globus_sdk.AuthClient(authorizer=auth2)
#             info = client.oauth2_userinfo()
#             session[usr.settings.GLOBUS_ID] = info['sub']
#             session[usr.settings.GLOBUS_USER] = info['preferred_username']
#             print(info.data)
#         return func(tc,kwargs)
#         #globus.available_endpoints(transfer_client)
#     except (globus_sdk.exc.TransferAPIError, KeyError) as e:
#         if 'Token is not active' in str(e):
#             return redirect(url_for('globus_login'))
#         return "There was an error getting available Globus end points: "+str(e)



def available_endpoints(tc:globus_sdk.TransferClient, *args):
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

def setupXfer(tc:globus_sdk.TransferClient,globus_usr:str, dv_endpoint_id:str, dirName:str):
    createDir(tc,dv_endpoint_id,dirName)
    shareEID = new_share(tc,dv_endpoint_id,globus_usr,dirName)
    grant_permission(tc,shareEID,globus_usr,dirName)
    return shareEID


def createDir(tc:globus_sdk.TransferClient,dv_endpoint_id:str, dirName:str):
    return tc.operation_mkdir(dv_endpoint_id,'/~/'+dirName)

def new_share(tc:globus_sdk.TransferClient,dv_endpoint_id:str,globus_usr:str, dirName:str):
    newEP = {
        'DATA_TYPE': 'shared_endpoint',
        'display_name': globus_usr,
        'host_endpoint': dv_endpoint_id,
        'host_path': '/~/'+dirName+'/',
        'description': globus_usr,
        'organization': 'Kansas State University - Dataverse'
    }
    tr = tc.create_shared_endpoint(newEP)
    print(str(tr))
    return tr
    

def grant_permission(tc:globus_sdk.TransferClient,sharedEndpointID:str,globus_usr:str,dirName:str):
    newACL = {
        'DATA_TYPE': 'access',
        'principal_type': 'identity',
        'principal': globus_usr,
        'path': '/~/'+dirName+'/',
        'permissions': 'rw'
    }
    tr = tc.add_endpoint_acl_rule(sharedEndpointID,newACL)
    return tr

def del_permission(tc:globus_sdk.TransferClient,sharedEndpointID:str,ACL_ID:str):
    tr = tc.delete_endpoint_acl_rule(sharedEndpointID,ACL_ID)
    return tr


def getActivationRequirements(tc:globus_sdk.TransferClient, globus_endpoint_id):
    tr = tc.endpoint_get_activation_requirements(globus_endpoint_id)
    print(tr)
    return tr

def autoActivate(tc:globus_sdk.TransferClient, globus_endpoint_id):
    tr = tc.endpoint_autoactivate(globus_endpoint_id)
    print(tr)
    return tr

def activateEndpoint(tc:globus_sdk.TransferClient,globus_endpoint_id:str,usr:str,pc:str):
    initial_response = autoActivate(tc,globus_endpoint_id)
    req3 = []
    for at in initial_response['DATA']:
        if at['type'] == 'myproxy':
            if at['name'] == 'passphrase':
                at['value'] = pc
            if at['name'] == 'username':
                at['value'] = usr
            req3.append(at)
    #https://docs.globus.org/api/transfer/endpoint_activation/#activation_requirements_document
    #If adjusting this document, please read  the above page carefully. The current documentation
    #as of 2/19/2020 is incorrect at least with how we have the Dataverse Globus enpoint configured.
    #The documentation says to get the activation requirements, add in the correct values, and send.
    #Instead, I've had to add the following fields as described in the example activation document
    #found in the above link, NOT simply using the activation_requirements doc queried from the
    #endpoint.
    req2 = {
        'DATA_TYPE': 'activation_requirements',
        'expires_in': 0,
        'expire_time': None,
        'auto_activation_supported': True,
        'activated': False,
        'length': len(req3),
        'oauth_server': None,
        'DATA': req3
    }
    try:
        tr = tc.endpoint_activate(globus_endpoint_id,req2)
        print(tr)
        return tr
    except:
        print(sys.exc_info())
        return sys.exc_info()


def transfer(tc:globus_sdk.TransferClient,srcEP, destEP,srcPathDir,destPathDir):
    srcPathDir = Path(str(srcPathDir).replace(":",""))
    destPathDir = Path(str(destPathDir).replace(":",""))

    
    tdata = globus_sdk.TransferData(tc,srcEP,destEP,label='Synapse generated, from Dataverse',sync_level='mtime',preserve_timestamp=True)
    tdata.add_item(srcPathDir,destPathDir,recursive=True)
    tresult = tc.submit_transfer(tdata)
    print('task_id='+tresult['task_id'])
    return tresult

