"""Check every published artifact hash and original scientific-script identity."""
from pathlib import Path
import argparse,hashlib,json
REPO=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.parse_args()
expected=json.loads((REPO/'provenance/release_sha256.json').read_text())
for name,record in expected['files'].items():
    p=(REPO/name).resolve();assert p.is_relative_to(REPO)
    assert p.stat().st_size==record['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],name
for name,h in json.loads((REPO/'provenance/original_scripts.json').read_text()).items():
    assert hashlib.sha256((REPO/'experiments/original'/name).read_bytes()).hexdigest()==h
print(json.dumps(dict(verified_artifact_hashes=len(expected['files']),original_scientific_scripts_exact=True)))
