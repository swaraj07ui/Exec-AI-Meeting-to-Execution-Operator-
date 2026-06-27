import os
import yaml
import json
import subprocess

for folder in ['tables', 'agents', 'workflows']:
    if not os.path.exists(folder): continue
    for f in os.listdir(folder):
        if not f.endswith('.yaml'): continue
        path = os.path.join(folder, f)
        with open(path) as file:
            data = yaml.safe_load(file)
        
        json_path = os.path.join(folder, f.replace('.yaml', '.json'))
        with open(json_path, 'w') as jf:
            json.dump(data, jf)

        name = os.path.splitext(f)[0]
        
        resource_type = folder[:-1] # tables -> table
        print(f"Deploying {resource_type} {name}...")
        cmd = f"lemma {resource_type} create -f {json_path} {name}"
        subprocess.run(cmd, shell=True)
