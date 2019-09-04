import json
import os
from shutil import copyfile

os.mkdir('json')
for root, dirs, files in os.walk('.'):
    for name in files:
        if name.endswith((".json")):
            src_file_path = os.path.join(root,name)
            convo_name = root.split('\\')[-1]
            des_file_path = '.\\json\\' + convo_name + '.json'
            

            copyfile(src_file_path, des_file_path)