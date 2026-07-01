import os
import yaml
import json
import shutil
import subprocess

POD_ID = "019f1c6e-e4d2-73ee-861d-501747ec50d6"
BUNDLE_DIR = "my_bundle/meeting-exec-pod"

bundle = {
  "format_version": 2,
  "name": "meeting-exec-pod",
  "description": "Turns meeting transcripts into tracked action items with AI agents",
  "contents": {
      "tables": [],
      "agents": [],
      "workflows": [],
      "functions": [],
      "apps": []
  }
}

# ── Tables, Agents, Workflows (YAML) ──────────────────────────────────────────
for folder in ['tables', 'agents', 'workflows']:
    if not os.path.exists(folder): continue
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.yaml'): continue
        path = os.path.join(folder, f)
        with open(path, encoding='utf-8') as file:
            data = yaml.safe_load(file)

            # Fix type 'string' → 'text' for tables (Lemma API requirement)
            if folder == 'tables' and 'columns' in data:
                for col in data['columns']:
                    if col.get('type') == 'string':
                        col['type'] = 'text'

            bundle["contents"][folder].append(data)
        print(f"  OK {folder}/{f}")

# ── Functions (Python) ─────────────────────────────────────────────────────────
# Lemma expects functions as { "name": ..., "source": "<python code>" }
if os.path.exists('functions'):
    for f in sorted(os.listdir('functions')):
        if not f.endswith('.py'): continue
        path = os.path.join('functions', f)
        with open(path, encoding='utf-8') as file:
            source = file.read()
        name = os.path.splitext(f)[0]
        bundle["contents"]["functions"].append({
            "name": name,
            "source": source
        })
        print(f"  OK functions/{f}")

# ── Apps (HTML) ────────────────────────────────────────────────────────────────
# Copy app files into the bundle directory and reference them
os.makedirs(f"{BUNDLE_DIR}/apps", exist_ok=True)
if os.path.exists('apps'):
    for f in sorted(os.listdir('apps')):
        if not f.endswith('.html'): continue
        name = os.path.splitext(f)[0]
        # Copy the file into bundle
        shutil.copy(os.path.join('apps', f), f"{BUNDLE_DIR}/apps/{f}")
        bundle["contents"]["apps"].append({
            "name": name,
            "file": f"apps/{f}"
        })
        print(f"  OK apps/{f}")

# ── Write bundle pod.json ──────────────────────────────────────────────────────
os.makedirs(BUNDLE_DIR, exist_ok=True)
pod_json_path = f"{BUNDLE_DIR}/pod.json"
with open(pod_json_path, "w", encoding='utf-8') as jf:
    json.dump(bundle, jf, indent=2)

print(f"\n[OK] Bundle written to {pod_json_path}")
print(f"   Tables:    {len(bundle['contents']['tables'])}")
print(f"   Agents:    {len(bundle['contents']['agents'])}")
print(f"   Workflows: {len(bundle['contents']['workflows'])}")
print(f"   Functions: {len(bundle['contents']['functions'])}")
print(f"   Apps:      {len(bundle['contents']['apps'])}")

# ── Deploy ────────────────────────────────────────────────────────────────────
print(f"\n[DEPLOY] Deploying to pod {POD_ID}...")
cmd = f'lemma pod import {BUNDLE_DIR} --pod {POD_ID}'
subprocess.run(cmd, shell=True)
