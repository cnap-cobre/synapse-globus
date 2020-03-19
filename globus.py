import globus_sdk
import os
from pathlib import Path
import copy
from enum import Enum
import sys
import json
import datetime
from dataverse import xferjob
from typing import List, Dict

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

def nativeAPPGenerateRefreshToken(credential_path:str):
    fr = open(credential_path,'r+')
    vals = json.loads(fr.read())
    native_client_id = vals['GLOBUS_NATIVE_APP_CLIENT_ID']
   
    #https://globus-sdk-python.readthedocs.io/en/stable/tutorial/#advanced-2-refresh-tokens-never-login-again
    # you must have a client ID
    client = globus_sdk.NativeAppAuthClient(native_client_id)
    client.oauth2_start_flow(refresh_tokens=True)

    print('Please go to this URL and login: {0}'
    .format(client.oauth2_get_authorize_url()))

    get_input = getattr(__builtins__, 'raw_input', input)
    auth_code = get_input('Please enter the code here: ').strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # let's get stuff for the Globus Transfer service
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    # the refresh token and access token, often abbr. as RT and AT
    transfer_rt = globus_transfer_data['refresh_token']
    print(transfer_rt)
    vals['GLOBUS_NATIVE_APP_REFRESH_TOKEN'] = transfer_rt
    fr.write(json.dumps(vals))
    fr.close()

    return transfer_rt

# def nativeAPPLogin(native_client_id:str, ):
    # #https://globus-sdk-python.readthedocs.io/en/stable/tutorial/#advanced-2-refresh-tokens-never-login-again
    # # you must have a client ID
    # client = globus_sdk.NativeAppAuthClient(native_client_id)
    # client.oauth2_start_flow(refresh_tokens=True)

    # print('Please go to this URL and login: {0}'
    # .format(client.oauth2_get_authorize_url()))

    # get_input = getattr(__builtins__, 'raw_input', input)
    # auth_code = get_input('Please enter the code here: ').strip()
    # token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # # let's get stuff for the Globus Transfer service
    # globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    # # the refresh token and access token, often abbr. as RT and AT
    # transfer_rt = globus_transfer_data['refresh_token']
    # transfer_at = globus_transfer_data['access_token']
    # expires_at_s = globus_transfer_data['expires_at_seconds']

    # # Now we've got the data we need, but what do we do?
    # # That "GlobusAuthorizer" from before is about to come to the rescue

    # authorizer = globus_sdk.RefreshTokenAuthorizer(
    #     transfer_rt, client, access_token=transfer_at, expires_at=expires_at_s)

    # # and try using `tc` to make TransferClient calls. Everything should just
    # # work -- for days and days, months and months, even years
    # tc = globus_sdk.TransferClient(authorizer=authorizer)

def getNativeTransferClient(native_client_id,refresh_token):
    client = globus_sdk.NativeAppAuthClient(native_client_id)
    authorizer = globus_sdk.RefreshTokenAuthorizer(refresh_token,client)
    tc = globus_sdk.TransferClient(authorizer=authorizer)
    return tc


def does_share_exist(tc:globus_sdk.TransferClient,globus_usr:str):
    return os.path.exists(globus_usr)

def setupXfer(credspath:str, globus_usr:str, globus_usr_id:str, dv_endpoint_id:str, dirName:str):
    
    fr = open(credspath,'r')
    vals = json.loads(fr.read())
    synapseUser = vals['DATAVERSE_GLOBUS_LOCAL_USER']
    synapsePass = vals['DATAVERSE_GLOBUS_LOCAL_PASSWORD']
    native_client_id = vals['GLOBUS_NATIVE_APP_CLIENT_ID']
    refresh_token = vals['GLOBUS_NATIVE_APP_REFRESH_TOKEN']
    fr.close()
    
    tc = getNativeTransferClient(native_client_id,refresh_token)
    activateEndpoint(tc,dv_endpoint_id,synapseUser,synapsePass)
    createDir(tc,dv_endpoint_id,dirName)
    newShareResult = new_share(tc,dv_endpoint_id,globus_usr,dirName)
    shareEID = newShareResult['id']
    grant_permission(tc,shareEID,globus_usr_id,dirName)
    return shareEID


def createDir(tc:globus_sdk.TransferClient,dv_endpoint_id:str, dirName:str):
    tr =  tc.operation_mkdir(dv_endpoint_id,'/~/'+dirName)
    print('Create Dir Result:')
    print(str(tr))
    return tr

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
    print('Create Share Result:')
    print(str(tr))
    return tr
    

def grant_permission(tc:globus_sdk.TransferClient,sharedEndpointID:str,globus_usr_id:str,dirName:str):
    # https://docs.globus.org/api/transfer/acl/
    newACL = {
        'DATA_TYPE': 'access',
        'principal_type': 'identity',
        'principal': globus_usr_id,
        'path': '/~/'+dirName+'/',
        'permissions': 'rw'
    }
    tr = tc.add_endpoint_acl_rule(sharedEndpointID,newACL)
    print('Grant Permission Result:')
    print(tr)
    return tr

def del_permission(tc:globus_sdk.TransferClient,sharedEndpointID:str,ACL_ID:str):
    tr = tc.delete_endpoint_acl_rule(sharedEndpointID,ACL_ID)
    print('Delete permission result:')
    print(str(tr))
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

def find_globus_path_for_files(tc:globus_sdk.TransferClient,files:xferjob.Job):
    filesRemaining:List[xferjob.FileData] = files.files.copy()
    


    res = find_file(tc,files.srcEndPoint,'',filesRemaining,False)

    paths_found:Dict[str,int] = {}
    dst_paths_found:Dict[str,int] = {}


    
    print('Could not the specified files...')
    fd:xferjob.FileData
    for fd in files.files:
        for path in fd.globus_path:
            if path in paths_found:
                paths_found[path] += 1
            else:
                paths_found[path] = 1
        for dst_path in fd.globus_path_DST_offset:
            if dst_path in dst_paths_found:
                dst_paths_found[dst_path] += 1
            else:
                dst_paths_found[dst_path] = 1
    if len(paths_found) < 1 and len(dst_paths_found) < 1:
        return "ERROR: Could not find at least one of the files you dragged in the selected Globus Source Endpoint. Are you sure it is there?"
    

    res = (paths_found,dst_paths_found)
    return res
    # if len(paths_found) > 0:
    #     return paths_found

    # #we've attached globus IDs to all the files now.
    # return "Success!"
   

def are_files_same(globus_path:str,globus_file,web_file:xferjob.FileData):
    #TODO: need to take into account file path?!
    fileName = web_file.path
    if web_file.path[0] == '/':
        fileName = web_file.path[1:]
    else:
        #Does the relative path we have with the browser file
        #exist in the abs path we find in globus?
        if web_file.path in globus_path+fileName:
            hh = 'Woohoo!'

    if globus_file['type'] != 'file': return False
    if globus_file['name'] == fileName:
                #Check file size & last modified!
                g = 6
                header = fileName+' at '+globus_path+': '
                print(header+'Name Matches!')

                globus_bytes = globus_file['size']
                if globus_bytes == web_file.size:
                    #file name and size match. let's check last modified...
                    print(header+'FileSize Matches @ ' + str(web_file.size))
                else:
                    print(header+'Abandoning because globus file size of '+globus_bytes+'<> web browser val of '+web_file.size)
                    return False
                dt = datetime.datetime.fromisoformat(globus_file['last_modified'])
                timestamp = dt.timestamp()
                found_last_modified = str(timestamp)[:-2] #Strip .0 from float
                #browser last modified includes milliseconds; globus doesn't give us that.
                selected_last_modified = str(web_file.mru)[:-3]
                if abs(int(found_last_modified)-int(selected_last_modified)) < 2:
                    #OK, we found a file with the same name, and within two seconds of
                    #last modified field.
                    #This is the directory!
                    print(header+'last modified matches! considered a match.')
                    return True
                elif abs(int(found_last_modified)-int(selected_last_modified)) == 3600:
                    #3/13/2020 - Either Globus/windows or browers do not take into account DST. So if the time
                    #difference is 3600 seconds exactly. then we will make this a runner up option, if we can't find it
                    #anywhere else.
                    if not globus_path in web_file.globus_path_DST_offset:
                        web_file.globus_path_DST_offset.append(globus_path)
                    print(header+'Found a diff of 1 hour exactly between web and globus last modified. Maybe a DST issue. marking as runner up.')
                else:
                    print(header+'Abandoning - Last modified globus of '+found_last_modified+' <> browser last modified of '+str(web_file.mru))
    return False


def do_files_exist_in_dir(dir:globus_sdk.transfer.response.IterableTransferResponse,files:xferjob.Job):
    return False

def find_file(tc:globus_sdk.TransferClient,srcEP:str, relativeDir:str,filesRemaining:List[xferjob.FileData],quit_when_found=True):
    if relativeDir == '':
        relativeDir = "/~/"
    dlr = tc.operation_ls(srcEP,path=relativeDir)
    print(dlr['DATA'])
    todo = []
    for element in dlr['DATA']:
        if element['type'] == 'dir':
            todo.append(element)
        elif element['type'] == 'file':
            for fd in filesRemaining:
                if are_files_same(relativeDir,element,fd) == True:
                    dressed_path = relativeDir+fd.path.rsplit('/',1)[1]
                    if not dressed_path in fd.globus_path:
                        fd.globus_path.append(dressed_path)
                    filesRemaining.remove(fd)
                    if quit_when_found == True:
                        if len(filesRemaining) == 0: return True
            # if element['name'] == fileName:
            #     #Check file size & last modified!
            #     g = 6
            #     header = fileName+' at '+relativeDir+': '
            #     print(header+'Name Matches!')

            #     globus_bytes = element['size']
            #     if globus_bytes == fileSize:
            #         #file name and size match. let's check last modified...
            #         print(header+'FileSize Matches @ ' + str(fileSize))
            #     else:
            #         print(header+'Abandoning because globus file size of '+globus_bytes+'<> web browser val of '+fileSize)
            #         continue
            #     dt = datetime.datetime.fromisoformat(element['last_modified'])
            #     timestamp = dt.timestamp()
            #     found_last_modified = str(timestamp)[:-2] #Strip .0 from float
            #     #browser last modified includes milliseconds; globus doesn't give us that.
            #     selected_last_modified = str(fileMRU)[:-3]
            #     if abs(int(found_last_modified)-int(selected_last_modified)) < 2:
            #         #OK, we found a file with the same name, and within two seconds of
            #         #last modified field.
            #         #This is the directory!
            #         print(header+'last modified matches! considered a match.')
            #         return dlr
            #     else:
            #         print(header+'Abandoning - Last modified globus of '+found_last_modified+' <> browser last modified of '+fileMRU)
    #Now that we've gone over all the files, let's delve the dirs.
    for dir_element in todo:
        newDir = relativeDir+dir_element['name']+'/'
        print('Delving '+newDir)
        result = find_file(tc,srcEP,newDir,filesRemaining)
        if quit_when_found == True:
            if result != None:
                return result
    return None


def transfer(tc:globus_sdk.TransferClient,srcEP, destEP,srcPathDir,destPathDir):
    srcPathDir = Path(str(srcPathDir).replace(":",""))
    destPathDir = Path(str(destPathDir).replace(":",""))

    
    tdata = globus_sdk.TransferData(tc,srcEP,destEP,label='Synapse generated, from Dataverse',sync_level='mtime',preserve_timestamp=True)
    tdata.add_item(srcPathDir,destPathDir,recursive=True)
    tresult = tc.submit_transfer(tdata)
    print('task_id='+tresult['task_id'])
    return tresult

def transferjob(tc:globus_sdk,job:xferjob.Job,destEP:str):
    tdata = globus_sdk.TransferData(tc,job.srcEndPoint,destEP,label='Synapse generated, from Dataverse',sync_level='mtime',preserve_timestamp=True)
    f:xferjob.FileData
    for f in job.files:
        tdata.add_item(f.globus_path,f.path)
    tresult = tc.submit_transfer(tdata)
    print('task_id='+tresult['task_id'])
    
    return tresult

