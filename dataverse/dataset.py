import json
import requests

def getList(server, apikey):
    existing_datasets = []
    alreadyCollected = []
    #Get datasets this user is associated with.
    #https://groups.google.com/forum/#!msg/dataverse-community/jZRBVGpNLcg/HxfJC-HyAwAJ

    roles_to_include = [1,6,7] #1=Admin, 6=Contributor, 7=Curator
    for role in roles_to_include:
        url = server+"/api/mydata/retrieve?key="+apikey+"&role_ids="+str(role)+"&dvobject_types=Dataset&published_states=Published&published_states=Unpublished&published_states=Draft&published_states=In+Review&published_states=Deaccessioned"
        r = requests.get(url)
        print(r.text)
        print(r.json)
        print("")
        j = json.loads(r.text)
        if j['success']:
            for item in j['data']['items']:
                if item['entity_id'] not in alreadyCollected:
                    print(item['name'] + " " +item['type'])
                    tmpds = {}
                    tmpds['name'] = item['name']
                    tmpds['entity_id'] = item['entity_id']
                    existing_datasets.append(tmpds)
                    alreadyCollected.append(item['entity_id'])
    return existing_datasets

def makeNew(server, apiKey, title, author, contact, description, subject):
    print("To DO! (http://guides.dataverse.org/en/latest/api/native-api.html#create-dataset-command)")