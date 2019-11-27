import sys
import os
from dataverse import dataset
from dataverse import upload
from dataverse import metadata
print(sys.argv)
# sys.argv[1]

def execute(debug:bool):
    beocat=1
    labType=-1
    dvkey='9419e587-3b9b-46d6-ae41-1940d075e081'
    ds=None
    desc=None
    tags=None
    files=[]
    for arg in sys.argv:
        if debug and (arg == 'run' or arg == '--no-debugger' or arg == '--no-reload' or '__main__.py' in arg):
            _noop = 5
        elif arg.startswith('lab='):
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

    if len(files) == 0:
        files_raw = input("Please specify one or more files / directories to upload.")
        files = files_raw.split(" ")
        print("split list: ")
        for f3 in files:
            print(f3)

    listOfFiles = list()
    for f in files:
        if os.path.isdir(f):
            for (dirpath, _dirnames, filenames) in os.walk(f):
                listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        else:
            if not os.path.exists(f):
                print("")
                print("The Following Path Does not exist: "+f)
                return

            listOfFiles.append(f)
    
    print("file List:")
    for f2 in listOfFiles:
        print(f2)

    md = metadata.Metadata()
    extractors = md.get_extractors()

    if labType < 0:
        largest_num = 0
        print("Choose Lab Type:")
        for ei in extractors.values():
            print(str(ei.id_num()) + ". " +ei.display_name())
            if ei.id_num() > largest_num: largest_num = ei.id_num()
        print('')
        labType=int(input("Input Lab Type Number (0-"+str(largest_num)+"): "))
    
   
    metadata_extractor = extractors[labType]
    qs = metadata_extractor.get_init_questions()
    answers = {}
    for question in qs:
        answers[question] = input(question)
    metadata_extractor.set_init_questions(answers)

    

    if dvkey is None:
        dvkey = input("Input Dataverse token:")

    base_dv_url = 'https://demo.dataverse.org'
    existing_datasets = dataset.getList(base_dv_url,dvkey)
  


    if ds is None:
        print("Please specify a dataset to add to:")
        print("0. (New DataSet)")
        for ds in existing_datasets:
            print(str(existing_datasets.index(ds)+1) + ". " + ds['name'])
        iselected = int(input("Please input the number of the dataset you wish to add this data to: "))
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
        tags = tagsraw.split(",")
    

    print("beocat: "+str(beocat))
    print("lab: "+str(labType))
    print("dvKey: "+dvkey)
    print("DS: "+str(ds))
    print("Desc: "+desc)
    print("Tags:")
    for t in tags:
        print("    "+t)
    print("files:")
    for f in listOfFiles:
        print("    uploading "+f+'...',end='')

        extra_metadata = metadata_extractor.extract(f)

        tags2 = list(tags)
        for em in extra_metadata.keys():
            tags2.append(em +" " +extra_metadata[em])
            
        upload.onefile(base_dv_url,dvkey,ds,f,desc,tags2)
        print("    done.")
    print("Upload finished!")


