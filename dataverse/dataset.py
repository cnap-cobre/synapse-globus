import json
import requests

def getList(server, apikey):
    existing_datasets = []
    #Get datasets this user is associated with.
    url = server+"/api/mydata/retrieve?key="+apikey+"&role_ids=6&dvobject_types=Dataset&published_states=Published&published_states=Unpublished&published_states=Draft&published_states=In+Review&published_states=Deaccessioned"
    r = requests.get(url)
    print(r.text)
    print(r.json)
    print("")
    j = json.loads(r.text)
    for item in j['data']['items']:
        print(item['name'] + " " +item['type'])
        tmpds = {}
        tmpds['name'] = item['name']
        tmpds['entity_id'] = item['entity_id']
        existing_datasets.append(tmpds)
    return existing_datasets

def makeNew(server, apiKey, title, author, contact, description, subject):
    print("To DO! (http://guides.dataverse.org/en/latest/api/native-api.html#create-dataset-command)")