import dataverse

base_url = 'https://demo.dataverse.org'

def upload(dvkey, datasetID, files, desc, tags, dv='Synapse'):
    for f in files:
        dataverse.upload.onefile(base_url,dvkey,datasetID,files,desc,tags)