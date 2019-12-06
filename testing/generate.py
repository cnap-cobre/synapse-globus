#Generates a list of non-sense files for testing bulk/large data xfers to dataverse.
import os
import random
import uuid
def gen(root_dir, max_sub_dir_depth, max_num_sub_dirs, num_files, max_file_size_bytes):
    result = ''
    available_dirs = [root_dir]
    
    while len(available_dirs) < max_num_sub_dirs:
        subdir = root_dir
        depth = random.randint(0,max_sub_dir_depth)
        for _z in range(0,depth):
            subdir = os.path.join(subdir,str(uuid.uuid4()))
            os.mkdir(subdir)
            available_dirs.append(subdir)
    print("Avaliable Dirs: ("+str(len(available_dirs))+")")
    for d in available_dirs:
        print(d)

    for _x in range(num_files):
        size = random.randint(1,max_file_size_bytes)
        filename = str(uuid.uuid4()) + '.' + str(random.randint(100,999))
        dir = available_dirs[random.randint(0,len(available_dirs)-1)]
        # print(dir)
        filepath = os.path.join(dir,filename).strip()
        # print(filepath+', '+str(size))
        line = '\t'.join((filepath,str(size),str(random.randint(0,1))))
        result = '\n'.join((result,line))
    f = open('c:\\temp\\DummyFileBatch.txt','w')
    f.write(result)
    f.close()
    print('Done!')





