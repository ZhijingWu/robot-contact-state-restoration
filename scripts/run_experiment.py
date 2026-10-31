"""Run exact frozen scientific code inside a separate, non-overwriting workspace."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from fetch_upstream import verify
REPO=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--workspace',type=Path,required=True)
ap.add_argument('--upstream',type=Path,default=REPO/'.cache/ar2s')
ap.add_argument('--stage',choices=['smoke','confirm','repeat'],required=True)
a=ap.parse_args();root=a.workspace.resolve();up=a.upstream.resolve();verify(up)
assert root!=REPO and not root.is_relative_to(REPO/'data'),'Choose a scratch workspace outside recorded data'
stage=root/'outputs/jiang-yip-native-validation/JIANG_RAW_RESULTS'/a.stage
assert not stage.exists(),'Refusing to overwrite an experiment stage'
code=root/'work/native';code.mkdir(parents=True,exist_ok=True)
hashes=json.loads((REPO/'provenance/original_scripts.json').read_text())
for name,expected in hashes.items():
    src=REPO/'experiments/original'/name
    assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
    dst=code/name
    if dst.exists():assert dst.read_bytes()==src.read_bytes()
    else:shutil.copy2(src,dst)
scene=code/'contact_scene'
if scene.exists():
    for p in (REPO/'data/scene').iterdir():assert (scene/p.name).read_bytes()==p.read_bytes()
else:shutil.copytree(REPO/'data/scene',scene)
source=root/'work/continuation/sources/ar2s'
if source.exists():verify(source)
else:shutil.copytree(up,source)
stage.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,str(code/'contact_experiment.py'),'--stage',a.stage],cwd=root,check=True)
