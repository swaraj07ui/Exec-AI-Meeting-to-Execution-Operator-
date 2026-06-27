import os
import yaml
import json
import subprocess

bundle = {
  "format_version": 2,
  "name": "meeting-exec-pod",
  "contents": {
      "tables": [],
      "agents": [],
      "workflows": [],
      "functions": [],
      "apps": []
  }
}

for folder in ['tables', 'agents', 'workflows', 'functions', 'apps']:
    if not os.path.exists(folder): continue
    for f in os.listdir(folder):
        if not f.endswith('.yaml'): continue
        path = os.path.join(folder, f)
        with open(path) as file:
            data = yaml.safe_load(file)
            
            # fix type 'string' to 'text' for tables
            if folder == 'tables' and 'columns' in data:
                for col in data['columns']:
                    if col.get('type') == 'string':
                        col['type'] = 'text'
                        
            bundle["contents"][folder].append(data)

# Put bundle in a subfolder as expected by lemma pod import
os.makedirs("my_bundle/meeting-exec-pod", exist_ok=True)
with open("my_bundle/meeting-exec-pod/pod.json", "w") as jf:
    json.dump(bundle, jf, indent=2)

print("Deploying bundle via lemma pod import...")
cmd = 'lemma pod import my_bundle/meeting-exec-pod'
subprocess.run(cmd, shell=True)
