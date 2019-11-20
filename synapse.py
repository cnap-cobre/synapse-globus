import sys
import requests
import pyDataverse
import json
print(sys.argv)
# sys.argv[1]

def execute():
    beocat=1
    labType=0
    dvkey='9419e587-3b9b-46d6-ae41-1940d075e081'
    ds=None
    desc=None
    tags=None
    files=[]
    for arg in sys.argv:
        if arg.startswith('lab='):
            labType = arg[4:]
        elif arg.startswith('dvkey='):
            dvkey = arg[6:]
        elif arg.startswith("ds="):
            ds=arg[3:]
        elif arg.startswith('desc='):
            desc=arg[5:]
        elif arg.startswith('tags='):
            tags=arg[5:]
        else:
            files.append(arg)

    if labType is None:
        print("Choose Lab Type:")
        print("1. Travis")
        print("0. None Of the Above")
        labType=input("Input Lab Type Number (0-1): ")

    if dvkey is None:
        dvkey = input("Input Dataverse token:")

    base_dv_url = 'https://demo.dataverse.org/'
    existing_datasets = []
    #Get datasets this user is associated with.
    url = base_dv_url+"api/mydata/retrieve?key="+dvkey+"&role_ids=6&dvobject_types=Dataset&published_states=Published&published_states=Unpublished&published_states=Draft&published_states=In+Review&published_states=Deaccessioned"
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



    if ds is None:
        print("Please specify a dataset to add to:")
        print("0. (New DataSet)")
        for ds in existing_datasets:
            print(str(existing_datasets.index(ds)+1) + ". " + ds['name'])
        iselected = int(input("Please input the number of the dataset you wish to add this data to:"))
        print("You selected " + str(iselected) + " " +existing_datasets[iselected-1]['name'])

        if iselected == 0:
            #New Dataset.
            print("ToDo: implement new dataset.")
        else:
            ds = existing_datasets[iselected-1]['entity_id']

    if desc is None:
        desc = input("Please input a search-able description of the data: ")

    if tags is None:
        tagsraw = input("Please Supply a comma delmited list of descriptive tags for the data: ")


    if files is None:
        
    print("beocat: "+str(beocat))
    print("lab: "+labType)
    print("dvKey: "+dvkey)
    print("DS: "+ds)
    print("Desc: "+desc)
    print("Tags: "+tags)
    print("files:")
    for f in files:
        print("    "+f)


