#!/usr/bin/env python3
"""Deterministic, public-source-only Skill distribution. --check never writes."""
import argparse,hashlib,io,json,stat,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agent-access'
NAME='aims-lens-agent-access-0.1.0.zip'
def sha(data):return hashlib.sha256(data).hexdigest()

def artifacts():
    source=[BASE/'setup.py']+sorted(p for p in (BASE/'skills/aims-lens').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    if any(p.is_symlink() for p in source):raise ValueError('linked source')
    entries={p.relative_to(BASE).as_posix():p.read_bytes() for p in source}
    for name in ('LICENSE','NOTICE','CONTENT_LICENSE.md'):
        entries[name]=(ROOT/name).read_text(encoding='utf-8').encode()
    manifest=''.join(sha(value)+'  '+name+'\n' for name,value in sorted(entries.items())).encode()
    entries['MANIFEST.sha256']=manifest
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,value in sorted(entries.items()):
            info=zipfile.ZipInfo('aims-lens-skills/'+name,date_time=(2026,10,21,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16;archive.writestr(info,value)
    bundle=out.getvalue()
    code=(BASE/'bootstrap/download.py.in').read_text().replace('@BUNDLE@',NAME).replace('@SHA256@',sha(bundle))
    result={'downloads/'+NAME:bundle,'PACKAGE.sha256':manifest}
    for name in ('install.sh','install.ps1'):
        result[name]=(BASE/('bootstrap/'+name+'.in')).read_text().replace('@PYTHON@',code).encode()
    hashes={name:sha(value) for name,value in result.items()}
    result['downloads/release.json']=(json.dumps({'sdk_version':'0.1.0','contract_version':'0.1.0-draft.2','files':hashes},indent=2)+'\n').encode()
    result['downloads/SHA256SUMS.txt']=''.join(sha(data)+'  '+name+'\n' for name,data in sorted(result.items())).encode()
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,data in artifacts().items():
        target=BASE/name
        if args.check:
            if not target.is_file() or target.read_bytes()!=data:raise SystemExit('Distribution drift: '+name)
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print('agent_distribution='+('verified' if args.check else 'built'))
if __name__=='__main__':main()
