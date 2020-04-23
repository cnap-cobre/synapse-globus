from flask import Flask, url_for, session, redirect, request, render_template, Response, stream_with_context
from datetime import datetime
import re
import os
import globus_sdk
import synapse
import json
import globus
from dataverse import xferjob
from dataverse import metadata
from dataverse import dataset
from dataverse import upload
from dataverse import download
from pathlib import Path
import usr
import zipfile
import time
import uuid
import hashlib
import jsonpickle
# import redis


class CustomFlask(Flask):

    def __init__(self, *args, **kwargs):
        super(CustomFlask, self).__init__(*args, **kwargs)
        self.msgs_for_client = {}

    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_start_string='%%',
        variable_end_string='%%',
    ))


# app = Flask(__name__)
app = CustomFlask(__name__)
app._static_folder = 'static'
app._static_url_path = ''
app.config.from_pyfile('app.conf')
# red = redis.StrictRedis()

# Run the app if called via script
if __name__ == '__main__':
    app.run()


def getGlobusObj():
    if not session.get('is_authenticated'):
        return redirect(url_for('globus_login'))
    authorizer = globus_sdk.AccessTokenAuthorizer(
        session['tokens']['transfer.api.globus.org']['access_token'])
    transfer_client = globus_sdk.TransferClient(authorizer=authorizer)
    return transfer_client


def globusDo(func, tc: globus_sdk.TransferClient, **kwargs):
    if tc is None:
        tc = getGlobusObj()
    try:
        if (usr.settings.GLOBUS_ID not in session) or (len(session[usr.settings.GLOBUS_ID]) < 5):
            auth2 = globus_sdk.AccessTokenAuthorizer(
                session['tokens']['auth.globus.org']['access_token'])
            client = globus_sdk.AuthClient(authorizer=auth2)
            info = client.oauth2_userinfo()
            session[usr.settings.GLOBUS_ID] = info['sub']
            session[usr.settings.GLOBUS_USER] = info['preferred_username']
            print(info.data)
        return func(tc, kwargs)
        # globus.available_endpoints(transfer_client)
    except (globus_sdk.exc.TransferAPIError, KeyError) as e:
        if 'Token is not active' in str(e):
            return redirect(url_for('globus_login'))
        return "There was an error getting available Globus end points: "+str(e)

    # print('Effective Identity "{}" has Full Name "{}" and Email "{}"'
    #     .format(info["sub"], info["name"], info["email"]))
    # return "You are successfully logged in!"


@app.route('/')
def index():

    # Script logic (testing)
    # synapse.execute(True,False)
    # generate.gen('c:\\temp\\dvdata',4,10,5000,1024*1024)

    return redirect('/upload')

    # transfer_client = getGlobusObj()

    # print("Endpoints Available:")
    # try:
    #     globus.available_endpoints(transfer_client)
    # except globus_sdk.exc.TransferAPIError as e:
    #     if 'Token is not active' in str(e):
    #         return redirect(url_for('globus_login'))
    #     return "There was an error getting available Globus end points: "+str(e)

    # auth2 = globus_sdk.AccessTokenAuthorizer(session['tokens']['auth.globus.org']['access_token'])
    # client = globus_sdk.AuthClient(authorizer=auth2)
    # info = client.oauth2_userinfo()
    # print(info.data)
    # # print('Effective Identity "{}" has Full Name "{}" and Email "{}"'
    # #     .format(info["sub"], info["name"], info["email"]))
    # return "You are successfully logged in!"


@app.route('/globus_login')
def globus_login():
    """
    Login via Globus Auth.
    May be invoked in one of two scenarios:

      1. Login is starting, no state in Globus Auth yet
      2. Returning to application during login, already have short-lived
         code from Globus Auth to exchange for tokens, encoded in a query
         param
    """
    # the redirect URI, as a complete URI (not relative path)
    redirect_uri = url_for('globus_login', _external=True)

    client = load_app_client()
    client.oauth2_start_flow(redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    # Redirect out to Globus Auth
    if 'code' not in request.args:
        auth_uri = client.oauth2_get_authorize_url()
        return redirect(auth_uri)
    # If we do have a "code" param, we're coming back from Globus Auth
    # and can start the process of exchanging an auth code for a token.
    else:
        code = request.args.get('code')
        try:
            tokens = client.oauth2_exchange_code_for_tokens(code)
        except globus_sdk.exc.AuthAPIError as aapie:
            # Seems to be a transient error with Globus. Resolve
            # by reloading a few times.
            print('fwe2 Transient Globus Error: '+str(aapie)+'. Retrying...')
            return redirect(url_for('globus_login'))

        # store the resulting tokens in the session
        session.update(
            tokens=tokens.by_resource_server,
            is_authenticated=True,
            # id=info["sub"],
            # name=info["name"],
            # email=info["email"]
        )

        return redirect(url_for('index'))


@app.route('/globus_logout')
def logout():
    """
    - Revoke the tokens with Globus Auth.
    - Destroy the session state.
    - Redirect the user to the Globus Auth logout page.
    """
    client = load_app_client()

    # Revoke the tokens with Globus Auth
    for token in (token_info['access_token']
                  for token_info in session['tokens'].values()):
        client.oauth2_revoke_token(token)

    # Destroy the session state
    session.clear()

    # the return redirection location to give to Globus AUth
    redirect_uri = url_for('index', _external=True)

    # build the logout URI with query params
    # there is no tool to help build this (yet!)
    globus_logout_url = (
        'https://auth.globus.org/v2/web/logout' +
        '?client={}'.format(app.config['APP_CLIENT_ID']) +
        '&redirect_uri={}'.format(redirect_uri) +
        '&redirect_name=Globus Example App')

    # Redirect the user to the Globus Auth logout page
    return redirect(globus_logout_url)


@app.route("/upload")
def uploadGET():
    # session['data'] = {'percent_done':0}

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        app.msgs_for_client[session['session_id']] = 0

    # Get a list of available globus endpoints.
    tc = getGlobusObj()
    if 'Response' in str(type(tc)):
        return tc
    endpoints = globusDo(globus.available_endpoints, tc)
    if 'Response' in str(type(endpoints)):
        return endpoints
    elif 'logged in' in str(endpoints):
        return redirect('/upload')
    # tmp = [{'a':'AAA','b':'BBB'},{'a':'aaa','b':'bbb'},{'a':'EEE','f':'fff'}]

    # load MRU settings if existant.
    usr.load(Path(app.config['USER_SETTINGS_PATH']), session)

    dvkey = ''
    if len(session[usr.settings.DV_KEY]) < 4:
        return redirect('/setdvkey?msg=Please_enter_a_valid_Dataverse_key')
    dvkey = session[usr.settings.DV_KEY]
    dvkey_masked = "*" + session[usr.settings.DV_KEY][-4:]
    session[usr.settings.DV_KEY_MASKED] = "*" + \
        session[usr.settings.DV_KEY][-4:]

    md = metadata.Metadata()
    labs = md.get_extractors()
    datasets = []
    try:
        datasets = dataset.getList(app.config['BASE_DV_URL'], dvkey)
    except dataset.AuthError as _ae:
        return redirect('/setdvkey?msg=Invalid_key')
    datasets.insert(0, {'name': 'New Dataset...', 'entity_id': '0'})

    return render_template('upload.html', endpoints=endpoints, mruEndpointID=session[usr.settings.SRC_ENDPOINT], labs=labs, mruLab=session[usr.settings.LAB_ID], guser=session[usr.settings.GLOBUS_USER], dvkey=dvkey_masked, datasets=datasets, mruDataset=session[usr.settings.DATASET_ID])


@app.route('/updatedvkey', methods=['POST'])
def updateDVKey():
    key = request.form['dvkey']
    if "*" + session[usr.settings.DV_KEY][-4:] != key:
        session[usr.settings.DV_KEY] = request.form['dvkey']
        usr.updateDisk(Path(app.config['USER_SETTINGS_PATH']), session)
    return redirect('/upload',)


@app.route('/setdvkey')
def setDVKey():
    msg = ''
    if 'msg' in request.args:
        msg = request.args.get('msg')
    dvkey = ''
    if len(session[usr.settings.DV_KEY]) > 4:
        dvkey = "*" + session[usr.settings.DV_KEY][-4:]
    return render_template('setdvkey.html', guser=session[usr.settings.GLOBUS_USER], dvkey=dvkey, status_msg=msg)


@app.route("/upload", methods=['POST'])
def uploadPOST():
    # files_to_upload = []

    session['percent_done'] = 1
    session['data'] = {'percent_done': 0}

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        # Since the session variable only gets updated per full page refresh (via cookies)
        # We need an update mechanism that updates more frequently for our server side updates
        # During upload. So we store our ID via the app.msgs_for_client variable.
        app.msgs_for_client[session['session_id']] = 0

    # session[usr.settings.DV_KEY] = request.form['dvkey']
    # session[usr.settings.GLOBUS_USER] = session['guser']

    srcEP = request.form['selected_endpoint']

    session[usr.settings.SRC_ENDPOINT] = srcEP
    session[usr.settings.LAB_ID] = request.form['lab_type']
    session[usr.settings.DATASET_ID] = request.form['dataset_id']

    # save MRU settings
    usr.updateDisk(Path(app.config['USER_SETTINGS_PATH']), session)

    # 4/8/2020: Pull up our manifest file we started populating after the drag'n'drop
    # event in order to map the relative browser path of the files with the Globus
    # abs path.
    job = xferjob.Job.fromdisk(session['job_id'], app.config['PENDING_PATH'])

    desc = request.form['description']
    tags = request.form['tags'].split(',')
    tags = [item.strip() for item in tags]

    # Handle metadata
    md = metadata.Metadata()
    extractors = md.get_extractors()
    metadata_extractor = extractors[int(session[usr.settings.LAB_ID])]
    # qs = metadata_extractor.get_init_questions()
    # answers = {}
    # for question in qs:
    #     answers[question] = input(question)
    # metadata_extractor.set_init_questions(answers)

    fd: xferjob.FileData
    for fd in job.files:
        fn = os.path.basename(fd.path)
        extra_metadata = metadata_extractor.extract(fn)
        tags2 = list(tags)
        filedesc = desc+" "
        if extra_metadata is not None:
            for em in extra_metadata.keys():
                tags2.append(em + " "+(str(extra_metadata[em])))
                filedesc += em + " "+(str(extra_metadata[em]))+", "
        fd.desc = filedesc.strip()
        fd.tags = tags2
        fd.selected_globus_path = request.form['src_endpoint_path']+fd.path
        fd.selected_globus_path = fd.selected_globus_path.replace('//', '/')
    job.todisk(app.config['PENDING_PATH'])

    # # #See if can find path relative to Globus
    # # file_data = job.files[0]
    # # file_name_to_find = file_data.path
    # # relative_root = ''
    # # if file_data.path[0] == '/':
    # #     relativeRoot = ''
    # #     file_name_to_find = file_data.path[1:]

    # # Now we need to find the globus (absolute) path of the files
    # # Dragged 'n dropped.
    # tc = getGlobusObj()
    # if 'Response' in str(type(tc)):
    #     return tc
    # find_result = 'Not Ran'
    # try:
    #     # job.srcEndPoint,relativeRoot,file_name_to_find,file_data.mru,file_data.size)
    #     find_result = globus.find_globus_path_for_files(tc, job)
    # except Exception as e:
    #     find_result = str(e)
    #     if 'AuthenticationFailed' in str(e):
    #         return redirect('/upload')

    # if 'Response' in str(type(find_result)):
    #     return find_result
    # elif 'logged in' in str(find_result):
    #     return redirect('/upload')

    # # Ideally, we get touple(list_of_matching_globus_paths,list_of_matching_globus_paths_1hour_off)
    # if len(find_result[0]) > 1:
    #     app.msgs_for_client[session['session_id']] = idx/cnt

    # OK, we should have a globus path attached to our files.
    # Set's setup the transfer.
    job.dest_endpoint = globus.setupXfer(app.config['SENSITIVE_INFO'], job.globus_usr_name,
                                         job.globus_id, app.config['DATAVERSE_GLOBUS_ENDPOINT_ID'], job.job_id)

    # fd:xferjob.FileData
    # for fd in jobs.files:
    #     fd.selected_globus_path =

    job.todisk(app.config['PENDING_PATH'])

    # Let's kickoff the transfer.
    tc = getGlobusObj()
    if 'Response' in str(type(tc)):
        return tc
    try:
        task_id = globus.transferjob(
            tc, job, job.dest_endpoint)
        job.globus_task_id = task_id
    except Exception as e:
        find_result = str(e)
        if 'AuthenticationFailed' in str(e):
            return redirect('/upload')

    if 'TransferResponse' in str(type(task_id)):
        if task_id['code'] == 'Accepted':
            job.globus_task_id = task_id['task_id']
        else:
            return "Could not successfully submit task: "+str(task_id)
    elif 'Response' in str(type(task_id)):
        return task_id
    elif 'logged in' in str(task_id):
        return redirect('/upload')

    # Let's re-save the job to capture the task_id
    job.todisk(app.config['PENDING_PATH'])
    # dirpath = Path(app.config['PENDING_PATH'])
    # dirpath.mkdir(parents=True,exist_ok=True)
    # mdpath = dirpath  / (job.job_id+'.json')
    # f = open(mdpath,'w')
    # f.write(mdcontent)
    # f.close()

    if app.config['UPLOAD_VIA_DV']:
        rootPath = Path('c:/temp/dvdata')
        server = app.config['BASE_DV_URL']
        api_key = session[usr.settings.DV_KEY]
        idx = 0
        cnt = len(job.files)
        for fd in job.files:
            if fd.path[0] == '/':
                fd.path = fd.path[1:]
                filePath = rootPath / fd.path
                upload.onefile(
                    server, api_key, job.dataset_id, filePath, fd.desc, fd.tags)
                idx += 1
                # session['percent_done'] = idx/cnt
                # session.modified = True
                # session['data']['percent_done'] = idx/cnt
                # red.publish('percent_done',str(idx/cnt))
                app.msgs_for_client[session['session_id']] = idx/cnt
                print('SYSTEM SAYS: ' +
                      str(app.msgs_for_client[session['session_id']]))

        # upload.files(app.config['BASE_DV_URL'],session[usr.settings.DV_KEY],job,Path('c:/temp/dvdata'))
        print("Upload finished!")
    return redirect('/upload')

# TODO: Also limit by Dataverse IP address(es)?
@app.route("/pending")
def pending():
    if not 'jid' in request.args:
        return('')

    if not 'INITIALIZED' in app.config:
        load_app_client()

    if str(request.remote_addr) in app.config['IP_WHITE_LIST']:
        if 'jid' in request.args:
            jobid = request.args.get('jid')
            dirpath = Path(app.config['PENDING_PATH'])
            mdpath = dirpath / (jobid+'.json')
            data = ''
            if not os.path.isfile(mdpath):
                return(data)
            with open(mdpath, 'r') as f:
                data = f.read()
            return(data)


@app.route("/test")
def test():
    res = globus.svr_transfer_status(
        app.config['SENSITIVE_INFO'], '5929f75a-7dd5-11ea-96df-0afc9e7dd773')
    print(str(res))
    return(str(res))

#     dvEP = app.config['DATAVERSE_GLOBUS_ENDPOINT_ID']

#     # #get passcode from offline src.
#     # creds = ''
#     # try:
#     #     fr = open(app.config['SENSITIVE_INFO'],'r')
#     #     creds = fr.read()
#     #     fr.close()
#     # except:
#     #     return 'unable to retrieve dataverse local user credentials.'

#     # #Activate the dataverse endpoint to setup a share.
#     # try:
#     #     tc = getGlobusObj()
#     #     if 'Response' in str(type(tc)):
#     #         return tc
#     #     elif 'logged in' in str(tc):
#     #         return redirect('/sharetest')


#         # tr = globus.activateEndpoint(tc,globus_endpoint_id=dvEP,usr='synapse',pc=creds)

#     # except (globus_sdk.exc.TransferAPIError, KeyError) as e:
#     #     if 'Token is not active' in str(e):
#     #         return redirect(url_for('globus_login'))
#     #     return "There was an error activating the dataverse ep: "+str(e)


#     # res = globus.nativeAPPGenerateRefreshToken(app.config['SENSITIVE_INFO'])
#     # print(res)
#     # globus_usr = 'deepwell@ksu.edu'
#     # globus_usr_id = '0a960cd0-01fd-449d-a825-bb3c0d28c71b'
#     globus.setupXfer(app.config['SENSITIVE_INFO'],job.globus_usr_name,job.globus_id,app.config['DATAVERSE_GLOBUS_ENDPOINT_ID'],job.job_id)

#     return("Success")


#     # tr = globusDo(globus.getActivationRequirements,tc,globus_endpoint_id=app.config['DATAVERSE_GLOBUS_ENDPOINT_ID'])
#     # if 'Response' in str(type(tr)):
#     #     return tr
#     # elif 'logged in' in str(tr):
#     #     return redirect('/sharetest')


#     # return str(tr)

@app.route("/tobeocat")
def toBeocat():
    if 'fileId' in request.args:
        session[usr.settings.DV_FILE_ID] = request.args['fileId']
    elif 'dataSetId' in request.args:
        session[usr.settings.DV_DATASET_ID] = int(request.args['dataSetId'])

    destEndpoint = app.config['BEOCAT_GLOBUS_ENDPOINT_ID']

   # Get a list of available globus endpoints.
    tc = getGlobusObj()
    if 'Response' in str(type(tc)):
        return tc
    endpoints = globusDo(globus.available_endpoints, tc)
    if 'Response' in str(type(endpoints)):
        return endpoints
    elif 'logged in' in str(endpoints):
        return redirect('/tobeocat')
    # tmp = [{'a':'AAA','b':'BBB'},{'a':'aaa','b':'bbb'},{'a':'EEE','f':'fff'}]

    if endpoints[destEndpoint]['activated'] == False:
        # Endpoint isn't activated. Re-direct.
        return redirect('https://app.globus.org/file-manager?destination_id='+destEndpoint+'&origin_id='+app.config['MUSTER_GLOBUS_ENDPOINT_ID']+'&origin_path=%2F~%2F'+destEndpoint)
    # load MRU settings if existant.
    usr.load(Path(app.config['USER_SETTINGS_PATH']), session)

    # OK, now let's pull the data via the dataverse API, and put it on Globus.
    files = []
    files.append(session[usr.settings.DV_FILE_ID])
    zipPath = Path(app.config['PENDING_PATH']) / 'PENDING.zip'

    msg = 'Not yet ran.'

    try:
        download.files(app.config['BASE_DV_URL'],
                       session[usr.settings.DV_KEY], files, zipPath)
        with zipfile.ZipFile(zipPath, 'r') as zip_ref:
            zip_ref.extractall(Path(app.config['PENDING_PATH']))
        os.remove(zipPath)
    except BaseException as be:
        msg = 'Error Staging Files to Beocat: ' + str(be)
        print(msg)

    try:
        xfer_result = globus.transfer(
            tc, app.config['MUSTER_GLOBUS_ENDPOINT_ID'], destEndpoint, app.config['PENDING_PATH'], 'FromDataverse')
    except globus_sdk.exc.TransferAPIError as te:
        if '409' in str(te):  # Expired Credentials for the endpoint. Need to re-activate
            return redirect('https://app.globus.org/file-manager?destination_id='+destEndpoint+'&origin_id='+app.config['MUSTER_GLOBUS_ENDPOINT_ID']+'&origin_path=%2F~%2F'+destEndpoint)
    print(xfer_result)
    msg = str(xfer_result)
    return render_template('toBeocat.html', endpoints=endpoints, mruEndpointID=destEndpoint, guser=session[usr.settings.GLOBUS_USER], dvkey=session[usr.settings.DV_KEY], status_msg=msg)


# #More secure would be requestor to provide a filename + mru + filesize,
# #and webserver would find jobs with that matching file, and only return those.
# #Also restrict requests to dataverse server. IP. + debugging ip. / dyndns.
# @app.route("/pending")
# def pending():
#     # filelist = []
#     data = []
#     dir = Path(app.config['PENDING_PATH'])
#     for (dirpath,_dirnames,filenames) in os.walk(dir):
#         files = [Path(dirpath) / file for file in filenames]
#         for p in files:
#             with open(p,'r') as myfile:
#                 d = myfile.read()
#             job = xferjob.Job.fromJSON(d)
#             data.append(job.toDict())
#         # filelist += path
#     return json.dumps(data,indent=1)


def get_message(msg):
    '''this could be any function that blocks until data is ready'''
    #  print('PERCENT DONE: '+str(msg))
    time.sleep(1.0)
    # s = time.ctime(time.time())
    s = str(msg*100) + "%"
    if s == "0%":
        s = ""
    return s


@app.route('/stream')
def stream():
    def eventStream():
        while True:
            blah = 0
            # print('In stream.')
            if 'session_id' in session:
                if session['session_id'] in app.msgs_for_client:
                    blah = app.msgs_for_client[session['session_id']]
            # print('Val '+str(blah))
            # sessvar = session['percent_done']
            # wait for source data to be available, then push it
            yield 'data: {}\n\n'.format(get_message(blah))
    return Response(stream_with_context(eventStream()), mimetype="text/event-stream")


@app.route('/updateFromDV', methods=['POST'])
def update_from_dv():
    if str(request.remote_addr) in app.config['IP_WHITE_LIST']:
        job_update: usr.JobHistory = jsonpickle.decode(request.form['JOB'])
        

@app.route('/link', methods=['POST'])
def link():

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        # Since the session variable only gets updated per full page refresh (via cookies)
        # We need an update mechanism that updates more frequently for our server side updates
        # During upload. So we store our ID via the app.mss_for_client variable.
        app.msgs_for_client[session['session_id']] = 0

    srcEP = request.form['selected_endpoint']
    session[usr.settings.SRC_ENDPOINT] = srcEP

    file_data = json.loads(request.form['file_list'])
    job = xferjob.Job(dataverse_user_id=xferjob.getID(session[usr.settings.DV_KEY]),
                      globus_user_id=session[usr.settings.GLOBUS_ID],
                      dataverse_dataset_id=session[usr.settings.DATASET_ID],
                      job_id=str(uuid.uuid4()),
                      globus_usr_name=session[usr.settings.GLOBUS_USER],
                      srcEndPoint=srcEP)

    session['job_id'] = job.job_id
    max_size = 0
    for fe in file_data:
        # fn = fe['name']
        path = fe['path']
        mru = fe['mru']
        sz = fe['size']
        max_size += sz
        fd = xferjob.FileData(path, sz, mru, '', [])
        job.files.append(fd)
    print("Max Size: "+str(max_size))
    job.job_size_bytes = max_size
    job.todisk(app.config['PENDING_PATH'])

    # Now we need to find the globus (absolute) path of the files
    # Dragged 'n dropped.
    tc = getGlobusObj()
    if 'Response' in str(type(tc)):
        return tc
    find_result = 'Not Ran'
    try:
        # job.srcEndPoint,relativeRoot,file_name_to_find,file_data.mru,file_data.size)
        find_result = globus.find_globus_path_for_files(tc, job)
    except Exception as e:
        find_result = str(e)
        if 'AuthenticationFailed' in str(e):
            return redirect('/upload')

    job.todisk(app.config['PENDING_PATH'])

    if type(find_result) is str:
        msg = {'msg': find_result, 'paths': []}
    else:
        if len(find_result[0]) == 1:
            msg = {'msg': 'Globus Path Found! ',
                   'paths': list(find_result[0].keys())}
        elif len(find_result[0]) > 1:
            msg = {'msg': 'We found multiple paths from the selected endpoint that could contain the files you dropped. Please Select the correct one.',
                   'paths': list(find_result[0].keys())}
        elif len(find_result[1]) == 1:
            msg = {'msg': 'Globus Path Found ',
                   'paths': list(find_result[1].keys())}
        elif len(find_result[1]) > 1:
            msg = {'msg': 'We found multiple paths from the selected endpoint that could contain the files you dropped. Please Select the correct one.',
                   'paths': list(find_result[1].keys())}
        else:
            msg = {'msg': "We could not find the files provided on the selected Globus endpoint. Are the files you dropped on the selected endpoint?"}
    output = json.dumps(msg)
    print(output)
    return output


def load_app_client():
    with open(app.config['SENSITIVE_INFO'], 'r') as fr:
        vals = json.loads(fr.read())
    app.config['PENDING_KEY'] = vals['PENDING_KEY']
    app.config['IP_WHITE_LIST'] = vals['IP_WHITE_LIST']
    app.config['INITIALIZED'] = True
    return globus_sdk.ConfidentialAppAuthClient(vals['GLOBUS_WEB_APP_CLIENT_ID'], vals['GLOBUS_WEB_APP_CLIENT_SECRET'])
