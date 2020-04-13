import requests

def get_manifest(job_id:str):
    server = "localhost:5000"
    pending_key = 'abcd'
    url = '%s/pending' % (server)
    url = url + 'key='+
    url = url + 'jid='+job_id
    with requests.get(url) as r:
        