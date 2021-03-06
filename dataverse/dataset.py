import json
import requests
from typing import Dict
import db


class AuthError(Exception):
    pass


def getList(server, apikey):
    existing_datasets = []
    alreadyCollected = []
    # Get datasets this user is associated with.
    # https://groups.google.com/forum/#!msg/dataverse-community/jZRBVGpNLcg/HxfJC-HyAwAJ

    roles_to_include = [1, 6, 7]  # 1=Admin, 6=Contributor, 7=Curator
    for role in roles_to_include:
        url = server+"/api/mydata/retrieve?key="+apikey+"&role_ids=" + \
            str(role)+"&dvobject_types=Dataset&published_states=Published&published_states=Unpublished&published_states=Draft&published_states=In+Review&published_states=Deaccessioned"
        r = requests.get(url)
        print(r.text)
        print(r.json)
        print("")
        j = json.loads(r.text)
        if j['success']:
            for item in j['data']['items']:
                if item['entity_id'] not in alreadyCollected:
                    print(item['name'] + " " + item['type'])
                    tmpds = {}
                    tmpds['name'] = item['name']
                    tmpds['entity_id'] = item['entity_id']
                    existing_datasets.append(tmpds)
                    alreadyCollected.append(item['entity_id'])
        else:
            if 'Please login' in j['error_message']:
                raise AuthError(j['error_message'])
            elif 'nothing was found for this role' in j['error_message']:
                pass
            else:
                raise Exception(
                    'Error Getting Dataset list: '+j['error_message'])
    return existing_datasets


def getStats(server, dataset_id):
    result = {}
    ops = {'total_views': 'viewsTotal',
           'total_downloads': 'downloadsTotal',
           'citations': 'citations',
           'unique_views': 'viewsUnique',
           'unique_downloads': 'downloadsUnique'
           }
    base_url = f'{server}/api/datasets/{dataset_id}/makeDataCount/'
    for key, value in ops.items():
        url = base_url+value
        print('Url: '+url)
        with requests.get(url) as r:
            print(r.text)
            print(r.json)
            print("")
            j = json.loads(r.text)
            if j['status'] != 'OK':
                raise Exception("dataverse url "+url +
                                " resulted in rsponse of "+r.text)
            result[key] = 0
            if value in j['data']:
                result[key] = j['data'][value]
    return result


def getDatasetInfo(dvsvr: str, dataset_id: int, store: db.DB) -> Dict:
    stats: Dict = getStats(dvsvr, dataset_id)
    stats['id'] = dataset_id
    url: str = f'{dvsvr}/api/datasets/{dataset_id}'
    with requests.get(url) as r:
        print(r.text)
        print(r.json)
        print("")
        j = json.loads(r.text)
        if j['status'] != 'OK':
            raise Exception("dataverse url "+url +
                            " resulted in rsponse of "+r.text)
        stats['persistentUrl'] = j['data']['persistentUrl']
        stats['url'] = f'{dvsvr}/dataset.xhtml?id={dataset_id}'
        for field in j['data']['latestVersion']['metadataBlocks']['citation']['fields']:
            if field['typeName'] == 'title':
                stats['title'] = field['value']
                break

    stats['total_bytes'] = store.execute(
        store.get_bytes_of_dataset, dataset_id=dataset_id)
    return stats


def makeNew(server, apiKey, title, author, contact, description, subject):
    print("To DO! (http://guides.dataverse.org/en/latest/api/native-api.html#create-dataset-command)")
