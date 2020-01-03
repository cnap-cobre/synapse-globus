from flask import Flask, url_for, session, redirect, request, render_template
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
import usr

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))

# app = Flask(__name__)
app = CustomFlask(__name__)
app._static_folder = 'static'
app._static_url_path = ''
app.config.from_pyfile('app.conf')

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


def globusDo(func, tc:globus_sdk.TransferClient):
    if tc is None:
        tc = getGlobusObj()
    try:
        if (usr.settings.GLOBUS_ID not in session) or (len(session[usr.settings.GLOBUS_ID]) < 5):
            auth2 = globus_sdk.AccessTokenAuthorizer(session['tokens']['auth.globus.org']['access_token'])
            client = globus_sdk.AuthClient(authorizer=auth2)
            info = client.oauth2_userinfo()
            session[usr.settings.GLOBUS_ID] = info['sub']
            session[usr.settings.GLOBUS_USER] = info['preferred_username']
            print(info.data)
        return func(tc)
        #globus.available_endpoints(transfer_client)
    except (globus_sdk.exc.TransferAPIError, KeyError) as e:
        if 'Token is not active' in str(e):
            return redirect(url_for('globus_login'))
        return "There was an error getting available Globus end points: "+str(e)
    
    # print('Effective Identity "{}" has Full Name "{}" and Email "{}"'
    #     .format(info["sub"], info["name"], info["email"]))
    #return "You are successfully logged in!"

@app.route('/')
def index():

    #Script logic (testing)
    #synapse.execute(True,False)
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
        tokens = client.oauth2_exchange_code_for_tokens(code)

        # store the resulting tokens in the session
        session.update(
            tokens=tokens.by_resource_server,
            is_authenticated=True,
            #id=info["sub"],
            #name=info["name"],
            #email=info["email"]
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
  
    #Get a list of available globus endpoints.
    tc = getGlobusObj()
    if 'Response' in str(type(tc)):
        return tc
    endpoints = globusDo(globus.available_endpoints,tc)
    if 'Response' in str(type(endpoints)):
        return endpoints
    elif 'logged in' in str(endpoints):
        return redirect('/upload')
    #tmp = [{'a':'AAA','b':'BBB'},{'a':'aaa','b':'bbb'},{'a':'EEE','f':'fff'}]

    #load MRU settings if existant.
    usr.load(app.config['USER_SETTINGS_PATH'],session)

    dvkey = ''
    if len(session[usr.settings.DV_KEY]) < 4:
        return redirect('/setdvkey?msg=Please_enter_a_valid_Dataverse_key')
    dvkey = session[usr.settings.DV_KEY]
    dvkey_masked = "*" + session[usr.settings.DV_KEY][-4:]



    md = metadata.Metadata()
    labs = md.get_extractors()
    datasets = []
    try:
        datasets = dataset.getList(app.config['BASE_DV_URL'],dvkey)
    except dataset.AuthError as ae:
        return redirect('/setdvkey?msg=Invalid_key')
    datasets.insert(0,{'name':'New Dataset...','entity_id':'0'})

   
    return render_template('upload.html',endpoints=endpoints,mruEndpointID=session[usr.settings.SRC_ENDPOINT],labs=labs,mruLab=session[usr.settings.LAB_ID], guser=session[usr.settings.GLOBUS_USER],dvkey=dvkey_masked,datasets=datasets,mruDataset=session[usr.settings.DATASET_ID])

@app.route('/updatedvkey',methods=['POST'])
def updateDVKey():
    key = request.form['dvkey']
    if "*" + session[usr.settings.DV_KEY][-4:] != key:
        session[usr.settings.DV_KEY] = request.form['dvkey']
        usr.updateDisk(app.config['USER_SETTINGS_PATH'],session)
    return redirect('/upload',)

@app.route('/setdvkey')
def setDVKey():
    msg = ''
    if 'msg' in request.args:
        msg = request.args.get('msg')
    dvkey = ''
    if len(session[usr.settings.DV_KEY]) > 4:
        dvkey = "*" + session[usr.settings.DV_KEY][-4:]
    return render_template('setdvkey.html',guser=session[usr.settings.GLOBUS_USER],dvkey=dvkey,status_msg=msg)

    

@app.route("/upload",methods=['POST'])
def uploadPOST():
    files_to_upload = []

    # session[usr.settings.DV_KEY] = request.form['dvkey']
    # session[usr.settings.GLOBUS_USER] = session['guser']
    session[usr.settings.SRC_ENDPOINT] = request.form['selected_endpoint']
    session[usr.settings.LAB_ID] = request.form['lab_type']
    session[usr.settings.DATASET_ID] = request.form['dataset_id']
    
    #save MRU settings
    usr.updateDisk(app.config['USER_SETTINGS_PATH'],session)
    
    job = xferjob.Job(xferjob.getID(session[usr.settings.DV_KEY]),session[usr.settings.GLOBUS_ID],session[usr.settings.DATASET_ID],xferjob.getFilename())

    desc = request.form['description']
    tags = request.form['tags'].split(',')

    #Handle metadata
    md = metadata.Metadata()
    extractors = md.get_extractors()
    metadata_extractor = extractors[int(session[usr.settings.LAB_ID])]
    qs = metadata_extractor.get_init_questions()
    answers = {}
    # for question in qs:
    #     answers[question] = input(question)
    # metadata_extractor.set_init_questions(answers)

    for v in request.form:
        if 'file_list' in v:
            file_data = json.loads(request.form[v])
            for fe in file_data:
                fn = fe['name']
                path = fe['path']
                mru = fe['mru']
                sz = fe['size']

                extra_metadata = metadata_extractor.extract(fn)

                tags2 = list(tags)
                if extra_metadata is not None:
                    for em in extra_metadata.keys():
                        tags2.append(em +" "+(str(extra_metadata[em])))

                fd = xferjob.FileData(path,sz,mru,desc,tags2)
                job.files.append(fd)
            mdcontent = job.toJSON()
            mdpath = 'c:\\temp\\'+job.job_id
            f = open(mdpath,'w')
            f.write(mdcontent)
            f.close()

            if app.config['UPLOAD_VIA_DV']:
                upload.files(app.config['BASE_DV_URL'],session[usr.settings.DV_KEY],job)
                print("Upload finished!")

           
#More secure would be requestor to provide a filename + mru + filesize,
#and webserver would find jobs with that matching file, and only return those.
#Also restrict requests to dataverse server. IP. + debugging ip. / dyndns.
@app.route("/pending")
def pending():
    # filelist = []
    data = []
    dir = app.config['PENDING_PATH']
    for (dirpath,_dirnames,filenames) in os.walk(dir):
        files = [os.path.join(dirpath,file) for file in filenames]
        for path in files:
            with open(path,'r') as myfile:
                d = myfile.read()
            job = xferjob.Job.fromJSON(d)
            data.append(job.toDict())
        # filelist += path
    return json.dumps(data,indent=1)

def load_app_client():
    return globus_sdk.ConfidentialAppAuthClient(app.config['APP_CLIENT_ID'], app.config['APP_CLIENT_SECRET'])