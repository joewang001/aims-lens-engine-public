#!/bin/sh
set -eu
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 3)'; then
  printf '%s\n' '{"status":"NOT_READY","code":"PYTHON_310_REQUIRED"}'
  exit 3
fi
has_host=false
for argument in "$@"; do case "$argument" in --host|--host=*) has_host=true;; esac; done
if [ "$has_host" = false ]; then
  if [ -n "${CODEX_THREAD_ID:-}" ]; then set -- --host codex "$@"
  elif [ -n "${DSH_PROFILE:-}" ]; then set -- --host deepseek-harness "$@"
  elif [ -t 0 ]; then
    printf 'Install for 1) Codex 2) DeepSeek Harness 3) Claude Code [1]: '
    read -r choice
    case "$choice" in 2) selected_host=deepseek-harness;; 3) selected_host=claude-code;; 1|'') selected_host=codex;; *) printf '%s\n' '{"status":"NOT_READY","code":"INVALID_HOST_SELECTION"}'; exit 3;; esac
    set -- --host "$selected_host" "$@"
  else printf '%s\n' '{"status":"NOT_READY","code":"SELECT_HOST_WITH_HOST_OPTION"}'; exit 3
  fi
fi
python3 - "$@" <<'AIMS_BOOTSTRAP_PYTHON'
# Generated into both native entrypoints with a reviewed bundle digest.
import argparse, hashlib, json, os, pathlib, stat, subprocess, sys, tempfile, urllib.parse, urllib.request, zipfile

parser=argparse.ArgumentParser(add_help=False)
parser.add_argument('--base-url',default='https://portal.aimslens.com')
parser.add_argument('--allow-local-test',action='store_true')
options,_=parser.parse_known_args()
base=options.base_url.rstrip('/')
url=urllib.parse.urlsplit(base)
allowed=base=='https://portal.aimslens.com' or (options.allow_local_test and url.scheme=='http' and url.hostname in ('localhost','127.0.0.1') and not url.username and not url.password and not url.path and not url.query and not url.fragment)
if not allowed:
    print(json.dumps({'status':'NOT_READY','code':'UNAPPROVED_DOWNLOAD_ORIGIN'}));sys.exit(3)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
try:
    with urllib.request.build_opener(NoRedirect).open('https://raw.githubusercontent.com/joewang001/aims-lens-engine-public/main/agent-access/downloads/aims-lens-agent-access-0.1.0.zip',timeout=30) as response:
        data=response.read(2*1024*1024+1)
    if len(data)>2*1024*1024 or hashlib.sha256(data).hexdigest()!='b285118dc8ecc59f228d76de5de87a201912972762b4790b11bfb10e22f569f8':
        raise ValueError('bundle integrity')
    with tempfile.TemporaryDirectory(prefix='aims-setup-') as folder:
        root=pathlib.Path(folder)
        archive_path=root/'bundle.zip';archive_path.write_bytes(data)
        with zipfile.ZipFile(archive_path) as archive:
            total=0
            for member in archive.infolist():
                p=pathlib.PurePosixPath(member.filename)
                total+=member.file_size
                if not member.filename.startswith('aims-lens-skills/') or p.is_absolute() or '..' in p.parts or '\\' in member.filename or stat.S_ISLNK(member.external_attr>>16) or total>20*1024*1024:
                    raise ValueError('unsafe archive')
            archive.extractall(root)
        package=root/'aims-lens-skills'
        for line in (package/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
            digest,relative=line.split('  ',1)
            file=(package/relative).resolve()
            if not file.is_relative_to(package.resolve()) or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
                raise ValueError('manifest integrity')
        if '--install-only' not in sys.argv:
            with urllib.request.build_opener(NoRedirect).open(base+'/v1/public-config',timeout=15) as check:
                configuration=json.loads(check.read(8193))
            if configuration.get('agent_onboarding_enabled') is not True:
                print(json.dumps({'status':'NOT_READY','code':'SERVICE_NOT_ENABLED','message':'The Skill can be installed with --install-only. API connection requires Portal activation and approved organization access.'}));sys.exit(3)
        code=subprocess.run([sys.executable,str(package/'setup.py'),*sys.argv[1:]]).returncode
    sys.exit(code)
except Exception:
    print(json.dumps({'status':'NOT_READY','code':'BOOTSTRAP_FAILED','message':'Download or integrity verification failed. No global settings changed.'}));sys.exit(3)

AIMS_BOOTSTRAP_PYTHON
