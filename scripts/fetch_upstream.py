"""Acquire pinned external dependencies without redistributing or executing them."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,json,time,urllib.request,urllib.error
REPO=Path(__file__).resolve().parents[1]
def verify(root):
    d=json.loads((REPO/'provenance/upstream_files.json').read_text())
    for item in d['files']:
        p=root/item['path'];assert p.is_file(),item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path']
    return d
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dest',type=Path,default=REPO/'.cache/ar2s')
    ap.add_argument('--verify-only',action='store_true')
    a=ap.parse_args();dest=a.dest.resolve()
    inventory=json.loads((REPO/'provenance/upstream_files.json').read_text())
    def acquire(item):
        p=(dest/item['path']).resolve();assert p.is_relative_to(dest)
        if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];return
        if a.verify_only:raise FileNotFoundError(item['path'])
        req=urllib.request.Request(item['url'],headers={'User-Agent':'RobotContactReproduction/1.0'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req,timeout=45) as r:b=r.read()
                break
            except (urllib.error.URLError,TimeoutError,OSError):
                if attempt==2:raise
                time.sleep(attempt+1)
        assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],item['path']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    list(ThreadPoolExecutor(max_workers=6).map(acquire,inventory['files']))
    verify(dest)
    print(json.dumps(dict(verified_files=len(inventory['files']),commit=inventory['commit'],downloaded_code_executed=False)))
