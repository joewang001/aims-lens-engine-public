#!/usr/bin/env python3
"""Install, enroll through the browser, and verify without exposing a machine key."""
import argparse
from contextlib import contextmanager
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

from aims_secret_store import Store, SecretStoreError, reference

SOURCE=Path(__file__).resolve().parents[1]
ORIGIN='https://portal.aimslens.com'
CLIENT_SHA='044e8b3134e28bc54d73b7dfa11e5080c0ece1667d3fde5f95ab23e566755a45'
HOST_PATHS={'codex':'.agents','deepseek-harness':'.dsh','claude-code':'.claude'}


class SetupError(Exception):
    def __init__(self,code):
        self.code=code


def origin(value, local=False):
    parsed=urllib.parse.urlsplit(value)
    if value.rstrip('/')==ORIGIN:
        return ORIGIN
    if local and parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','localhost') and not parsed.username and not parsed.password and parsed.path in ('','/') and not parsed.query and not parsed.fragment:
        return value.rstrip('/')
    raise SetupError('UNAPPROVED_ORIGIN')


def state_path(project):
    folder=project/'.aims-lens'
    if folder.is_symlink() or not folder.resolve().is_relative_to(project):
        raise SetupError('UNSAFE_CONFIG_DIRECTORY')
    folder.mkdir(exist_ok=True)
    path=folder/'connection.json'
    if path.is_symlink():
        raise SetupError('UNSAFE_CONFIG_FILE')
    ignore=folder/'.gitignore'
    if not ignore.exists():
        ignore.write_text('*\n',encoding='utf-8')
    return path


def write_state(path,data):
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as stream:
        json.dump(data,stream)
        name=stream.name
    Path(name).replace(path)


@contextmanager
def project_lock(project):
    path=state_path(project).parent/'setup.lock'
    if path.is_symlink():raise SetupError('UNSAFE_LOCK_FILE')
    with path.open('a+b') as stream:
        stream.seek(0);stream.write(b'0');stream.flush();stream.seek(0)
        try:
            if sys.platform=='win32':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            raise SetupError('SETUP_ALREADY_RUNNING') from None
        try:
            yield
        finally:
            stream.seek(0)
            if sys.platform=='win32':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def install(project,host,upgrade=False):
    target=project/HOST_PATHS[host]/'skills/aims-lens'
    if host=='deepseek-harness' and not target.exists():
        shared=project/'.agents/skills/aims-lens'
        if shared.exists():
            target=shared
    for parent in (target.parent.parent,target.parent,target):
        if parent.is_symlink() or not parent.resolve().is_relative_to(project):
            raise SetupError('INSTALL_TARGET_ESCAPES_PROJECT')
    files=[p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    if any(p.is_symlink() for p in files):
        raise SetupError('UNSAFE_PACKAGE')
    replacing=False
    if target.exists():
        if any(p.is_symlink() for p in target.rglob('*')):
            raise SetupError('UNSAFE_EXISTING_SKILL')
        actual={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
        expected={p.relative_to(SOURCE).as_posix() for p in files}
        if actual!=expected or any((target/p.relative_to(SOURCE)).read_bytes()!=p.read_bytes() for p in files):
            if not upgrade:
                raise SetupError('EXISTING_SKILL_VERSION_CONFLICT_USE_UPGRADE_TO_BACK_UP')
            replacing=True
        else:
            return target
    target.parent.mkdir(parents=True,exist_ok=True)
    # Stage in the selected skill parent, then atomically publish the complete directory.
    # Python 3.13+ creates Windows mkdtemp directories with a private DACL.
    # Public Skill code must inherit the workspace ACL; protected secrets never live here.
    staging=target.parent/('.aims-install-'+secrets.token_hex(8))
    staging.mkdir(mode=0o755,exist_ok=False)
    backup=None
    try:
        for file in files:
            output=staging/file.relative_to(SOURCE)
            output.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(file,output)
            if output.read_bytes()!=file.read_bytes():
                raise SetupError('INSTALL_HASH_MISMATCH')
        if replacing:
            backup_root=state_path(project).parent/'skill-backups'
            if backup_root.is_symlink() or not backup_root.resolve().is_relative_to(project):
                raise SetupError('UNSAFE_BACKUP_PATH')
            backup_root.mkdir(exist_ok=True)
            # Keep old SKILL.md files outside every host's discovery directory.
            backup=backup_root/(host+'-'+secrets.token_hex(6))
            if not backup.resolve().is_relative_to(project):
                raise SetupError('UNSAFE_BACKUP_PATH')
            target.rename(backup)
        staging.rename(target)
    except Exception:
        # Only our own staging directory is removed, never an existing installation.
        if staging.resolve().parent==target.parent.resolve() and staging.name.startswith('.aims-install-'):
            shutil.rmtree(staging)
        if backup is not None and backup.exists() and not target.exists():
            backup.rename(target)
        raise
    return target


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None


def request(base,path,payload):
    raw=json.dumps(payload).encode()
    req=urllib.request.Request(base+path,data=raw,headers={'Content-Type':'application/json'},method='POST')
    opener=urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req,timeout=20) as response:
            value=response.read(65537)
            if len(value)>65536:
                raise SetupError('UNUSABLE_SERVER_RESPONSE')
            return json.loads(value)
    except urllib.error.HTTPError as exc:
        try:
            code=json.loads(exc.read(4096)).get('detail',{}).get('code')
        except (ValueError,AttributeError):
            code=None
        raise SetupError(code if isinstance(code,str) and re.fullmatch('[A-Z_]{1,80}',code) else 'CONNECTION_REQUEST_REJECTED') from None
    except (OSError,ValueError):
        raise SetupError('CONNECTION_TRANSPORT_UNKNOWN') from None


def invoke_client(skill,config,secret,arguments):
    if hashlib.sha256((skill/'scripts/aims_client.py').read_bytes()).hexdigest()!=CLIENT_SHA:
        raise SetupError('CLIENT_INTEGRITY_MISMATCH')
    forbidden={'--base-url','--allow-local-mock'}
    if any(arg.split('=')[0] in forbidden for arg in arguments):
        raise SetupError('ORIGIN_OVERRIDE_NOT_ALLOWED')
    command=[sys.executable,str(skill/'scripts/aims_client.py'),*arguments,'--base-url',config['origin']]
    if config['origin']!=ORIGIN:
        command+=['--allow-local-mock']
    env={k:v for k,v in os.environ.items() if k!='AIMS_API_KEY'}
    if secret:
        env['AIMS_API_KEY']=secret['api_key']
    run=subprocess.run(command,env=env,capture_output=True,timeout=65)
    if secret and secret['api_key'].encode() in run.stdout+run.stderr:
        raise SetupError('SECRET_REFLECTION_BLOCKED')
    return run


def load_secret(store,config,project):
    if config['secret_ref']!=reference(config['origin'],project):
        raise SetupError('SECRET_REFERENCE_MISMATCH')
    secret=store.load(config['secret_ref'])
    if secret.get('origin')!=config['origin'] or secret.get('project')!=str(project):
        raise SetupError('SECRET_BINDING_MISMATCH')
    if config.get('status')=='CONNECTED' and any(secret.get(k)!=config.get(k) for k in ('principal_id','organization_id')):
        raise SetupError('SECRET_IDENTITY_MISMATCH')
    return secret


def doctor(project,config,store):
    if config.get('status')!='CONNECTED':
        raise SetupError('LOCAL_AUTHORIZATION_REQUIRED')
    secret=load_secret(store,config,project)
    skill=Path(config['skill_path']).resolve()
    if not skill.is_relative_to(project):
        raise SetupError('INVALID_SKILL_PATH')
    outputs={}
    for operation in ('capabilities','whoami'):
        run=invoke_client(skill,config,secret,[operation,'--execute'])
        if run.returncode:
            try:
                error=json.loads(run.stdout).get('error',{}).get('code','VALIDATION_FAILED')
            except ValueError:
                error='VALIDATION_FAILED'
            raise SetupError(error)
        outputs[operation]=json.loads(run.stdout)['data']
    me=outputs['whoami']
    if outputs['capabilities'].get('contract_version')!='0.1.0-draft.2' or any(me.get(field)!=config.get(field) for field in ('principal_id','organization_id')):
        raise SetupError('CONNECTION_IDENTITY_MISMATCH')
    return {'status':'READY','host':config['host'],'organization_id':me['organization_id'],
            'principal_id':me['principal_id'],'scopes':me['scopes'],'role_access':me['role_access'],
            'expires_at':me['expires_at'],'validation':'capabilities+whoami','credential_store':store.kind}


def connect(project,host,base,local=False,no_browser=False,wait=120,upgrade=False):
    with project_lock(project):
        return _connect(project,host,base,local,no_browser,wait,upgrade)


def _connect(project,host,base,local=False,no_browser=False,wait=120,upgrade=False):
    target=install(project,host,upgrade)
    path=state_path(project)
    config=json.loads(path.read_text()) if path.exists() else {}
    if config and (config.get('origin')!=base or (config.get('host')!=host and config.get('status')!='CONNECTED')):
        raise SetupError('EXISTING_CONNECTION_CONFLICT')
    store=Store()  # Fail before sending any enrollment request if persistence is unavailable.
    if config.get('status')=='CONNECTED':
        config.update(host=host,skill_path=str(target))
        write_state(path,config)
        return doctor(project,config,store)
    ref=reference(base,project)
    if not config:
        credential_prefix='aims_mk_'
        token=credential_prefix+secrets.token_urlsafe(40)
        verifier=secrets.token_urlsafe(48)
        secret={'api_key':token,'verifier':verifier,'origin':base,'project':str(project)}
        store.save(ref,secret)
        config={'status':'STARTING','secret_ref':ref,'origin':base,'host':host,'skill_path':str(target),'local_test':local}
        write_state(path,config)  # Persist the original proof/key before the first network request.
    else:
        secret=load_secret(store,config,project)
    if config['status']=='STARTING':
        challenge=base64.urlsafe_b64encode(hashlib.sha256(secret['verifier'].encode()).digest()).decode().rstrip('=')
        enrollment=request(base,'/connect/v1/start',{'challenge':challenge,'credential_hash':hashlib.sha256(secret['api_key'].encode()).hexdigest(),
            'device_label':re.sub('[^A-Za-z0-9 ._-]','_',socket.gethostname())[:60]+' '+host,'host':host})
        # A server may not redirect enrollment to another origin or arbitrary browser action.
        expected=base+'/?aims_connect='+enrollment['connection_id']
        if enrollment.get('verification_uri')!=expected or not re.fullmatch(r'con_[a-f0-9]{32}',enrollment['connection_id']):
            raise SetupError('UNAPPROVED_AUTHORIZATION_URL')
        config.update(status='PENDING',connection_id=enrollment['connection_id'],verification_uri=expected,
                      user_code=enrollment['user_code'],expires_at=enrollment['expires_at'])
        write_state(path,config)
    if config['status']!='PENDING':
        raise SetupError('LOCAL_AUTHORIZATION_REQUIRED')
    print(json.dumps({'status':'NEEDS_BROWSER_AUTHORIZATION','verification_uri':config['verification_uri'],'user_code':config['user_code'],
                      'instruction':'Confirm this code, institution and permissions in your browser. Never paste an API key into chat.'}),flush=True)
    if not no_browser:
        webbrowser.open(config['verification_uri'])
    deadline=time.monotonic()+wait
    while True:
        result=request(base,'/connect/v1/poll',{'connection_id':config['connection_id'],'verifier':secret['verifier'],'cancel':False})
        if result['status']=='READY':
            config.update({key:result[key] for key in ('principal_id','organization_id','key_id','expires_at')})
            config['status']='CONNECTED'
            secret.update({key:result[key] for key in ('principal_id','organization_id')})
            store.save(ref,secret)  # Keep proof until CONNECTED state is durably recorded.
            write_state(path,config)
            store.save(ref,{key:value for key,value in secret.items() if key!='verifier'})
            return doctor(project,config,store)
        if result['status'] not in ('CREATED','CONSENTED'):
            raise SetupError('AUTHORIZATION_'+result['status'])
        if time.monotonic()>=deadline:
            return {'status':'AUTHORIZATION_PENDING','resume':'Run the same installer again; the saved request will be reused.'}
        time.sleep(5)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path.cwd())
    parser.add_argument('--host',choices=sorted(HOST_PATHS))
    parser.add_argument('--base-url',default=ORIGIN)
    parser.add_argument('--allow-local-test',action='store_true')
    parser.add_argument('--install-only',action='store_true')
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--wait',type=int,default=120)
    parser.add_argument('--status',action='store_true')
    parser.add_argument('--cancel',action='store_true')
    parser.add_argument('--reconnect',action='store_true')
    parser.add_argument('--upgrade',action='store_true')
    parser.add_argument('--run',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    try:
        project=args.project_root.resolve(strict=True)
        if not project.is_dir() or not 0<=args.wait<=600:
            raise SetupError('INVALID_PROJECT_OR_WAIT')
        base=origin(args.base_url,args.allow_local_test)
        if args.reconnect:
            path=state_path(project)
            if path.exists():
                old=json.loads(path.read_text())
                if old['origin']!=base:
                    raise SetupError('EXISTING_CONNECTION_CONFLICT')
                saved=load_secret(Store(),old,project)
                if old.get('status')=='CONNECTED':
                    probe=invoke_client(Path(old['skill_path']),old,saved,['whoami','--execute'])
                    if probe.returncode==0:
                        raise SetupError('REVOKE_CURRENT_DEVICE_IN_PORTAL_FIRST')
                    try:code=json.loads(probe.stdout)['error']['code']
                    except (ValueError,KeyError):code=None
                    if code!='UNAUTHENTICATED':
                        raise SetupError('RECONCILE_CURRENT_CONNECTION_FIRST')
                elif old.get('status')=='PENDING':
                    status=request(base,'/connect/v1/poll',{'connection_id':old['connection_id'],'verifier':saved['verifier'],'cancel':False})['status']
                    if status not in ('CANCELLED','DENIED','EXPIRED','REVOKED'):
                        raise SetupError('CANCEL_CURRENT_AUTHORIZATION_FIRST')
                else:
                    raise SetupError('RESUME_SAVED_REQUEST_FIRST')
                path.replace(path.with_name('previous-'+secrets.token_hex(4)+'.json'))
                args.host=args.host or old['host']
        if args.status or args.run is not None or args.cancel:
            path=state_path(project)
            if not path.exists():
                raise SetupError('LOCAL_AUTHORIZATION_REQUIRED')
            config=json.loads(path.read_text())
            origin(config['origin'],config.get('local_test') is True)
            if args.run is not None:
                execute='--execute' in args.run
                if execute and config.get('status')!='CONNECTED':
                    raise SetupError('LOCAL_AUTHORIZATION_REQUIRED')
                secret=load_secret(Store(),config,project) if execute else None
                skill=Path(config['skill_path']).resolve()
                if not skill.is_relative_to(project):
                    raise SetupError('INVALID_SKILL_PATH')
                run=invoke_client(skill,config,secret,args.run)
                sys.stdout.buffer.write(run.stdout)
                sys.stderr.buffer.write(run.stderr)
                return run.returncode
            store=Store()
            if args.cancel:
                if config.get('status')!='PENDING':
                    raise SetupError('NO_PENDING_AUTHORIZATION')
                value=load_secret(store,config,project)
                result=request(config['origin'],'/connect/v1/poll',{'connection_id':config['connection_id'],'verifier':value['verifier'],'cancel':True})
            else:
                result=doctor(project,config,store)
        else:
            host=args.host
            if not host:
                if os.environ.get('CODEX_THREAD_ID'):
                    host='codex'
                elif os.environ.get('DSH_PROFILE'):
                    host='deepseek-harness'
                elif sys.stdin.isatty():
                    selection=input('Install for 1) Codex 2) DeepSeek Harness 3) Claude Code [1]: ').strip() or '1'
                    host={'1':'codex','2':'deepseek-harness','3':'claude-code'}.get(selection)
                if not host:
                    raise SetupError('SELECT_HOST_WITH_HOST_OPTION')
            if args.install_only:
                result={'status':'INSTALLED_NOT_CONNECTED','skill_path':str(install(project,host,args.upgrade)),'api_enabled':False}
            else:
                result=connect(project,host,base,args.allow_local_test,args.no_browser,args.wait,args.upgrade)
        print(json.dumps(result))
        return 0 if result.get('status') in ('READY','INSTALLED_NOT_CONNECTED') else 3
    except (SetupError,SecretStoreError) as exc:
        result={'status':'NOT_READY','code':getattr(exc,'code',str(exc))}
        if isinstance(exc,SecretStoreError):
            result['next_step']='Run the downloaded native installer in your local terminal with an available OS credential store. Preserve the saved request; do not send a key in chat or weaken the harness sandbox.'
        print(json.dumps(result))
        return 3
    except Exception:
        print(json.dumps({'status':'NOT_READY','code':'SETUP_FAILED_SAFE','message':'No secret details printed. Preserve the saved request and reconcile before retrying.'}))
        return 4


if __name__=='__main__':
    raise SystemExit(main())
