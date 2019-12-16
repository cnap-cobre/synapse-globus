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

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))

# app = Flask(__name__)
app = CustomFlask(__name__)
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
        if 'gid' not in session:
            auth2 = globus_sdk.AccessTokenAuthorizer(session['tokens']['auth.globus.org']['access_token'])
            client = globus_sdk.AuthClient(authorizer=auth2)
            info = client.oauth2_userinfo()
            session['gid'] = info['sub']
            session['guser'] = info['preferred_username']
            print(info.data)
        return func(tc)
        #globus.available_endpoints(transfer_client)
    except globus_sdk.exc.TransferAPIError as e:
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
    endpoints = globusDo(globus.available_endpoints,tc)
    if 'Response' in str(type(endpoints)):
        return endpoints
    elif 'logged in' in str(endpoints):
        return redirect('/upload')
    #tmp = [{'a':'AAA','b':'BBB'},{'a':'aaa','b':'bbb'},{'a':'EEE','f':'fff'}]

    md = metadata.Metadata()
    labs = md.get_extractors()
    guser = session['guser']
    dvkey = ''
    if 'dvkey' in session:
        dvkey = session['dvkey']
        dvkey = "*" + dvkey[-4:]
    return render_template('upload.html',endpoints=endpoints,labs=labs, guser=guser,dvkey=dvkey)

@app.route("/upload",methods=['POST'])
def upload():
    files_to_upload = []

    settings = {}
    settings['labid'] = request.form['labid']
    settings['dvkey'] = request.form['dvkey']
    settings['gid'] = session['guser']
    settings['mruEndpointID'] = request.form['selected_endpoint']
    session['dvkey'] = request.form['dvkey']

    for v in request.form:
        if 'file_list' in v:
            file_data = json.loads(request.form[v])
            
            files_to_upload.append(file_elements)
        print("%s : %s" % (v,request.form[v]))
        if 'fileToUpload' in v:
             fileAttrList = v.split(",")
    uname=request.form['file1']  
    passwrd=request.form['pass']  
    # if uname=="ayush" and passwrd=="google":  
    return "Welcome %s" %uname  

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