param(
    [string]$ProjectRoot = (Get-Location).Path,
    [ValidateSet('', 'codex', 'deepseek-harness', 'claude-code')][string]$HostName = '',
    [string]$BaseUrl = 'https://portal.aimslens.com',
    [switch]$AllowLocalTest,
    [switch]$InstallOnly,
    [switch]$NoBrowser,
    [switch]$Upgrade,
    [switch]$Reconnect,
    [int]$WaitSeconds = 120
)
$ErrorActionPreference='Stop'
$pythonRuntime=Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pythonRuntime) { Write-Output '{"status":"NOT_READY","code":"PYTHON_310_REQUIRED"}'; exit 3 }
& $pythonRuntime.Source -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 3)'
if ($LASTEXITCODE -ne 0) { Write-Output '{"status":"NOT_READY","code":"PYTHON_310_REQUIRED"}'; exit 3 }
if (-not $HostName) {
    if ($env:CODEX_THREAD_ID) { $HostName='codex' }
    elseif ($env:DSH_PROFILE) { $HostName='deepseek-harness' }
    elseif (-not [Console]::IsInputRedirected) {
        $choice=Read-Host 'Install for 1) Codex 2) DeepSeek Harness 3) Claude Code [1]'
        $HostName=switch ($choice) { '2' {'deepseek-harness'} '3' {'claude-code'} '1' {'codex'} '' {'codex'} default { Write-Output '{"status":"NOT_READY","code":"INVALID_HOST_SELECTION"}'; exit 3 } }
    } else { Write-Output '{"status":"NOT_READY","code":"SELECT_HOST_WITH_HOSTNAME_OPTION"}'; exit 3 }
}
$setupArgs=@('--project-root',$ProjectRoot,'--host',$HostName,'--base-url',$BaseUrl,'--wait',[string]$WaitSeconds)
if($AllowLocalTest){$setupArgs+='--allow-local-test'}
if($InstallOnly){$setupArgs+='--install-only'}
if($NoBrowser){$setupArgs+='--no-browser'}
if($Upgrade){$setupArgs+='--upgrade'}
if($Reconnect){$setupArgs+='--reconnect'}
$bootstrapCode=@'
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
    if len(data)>2*1024*1024 or hashlib.sha256(data).hexdigest()!='9b6cb569d879cec2d7fa0b11797f3bca6aba6a3069b142614ce21cf8ba71c499':
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

'@
$bootstrapCode | & $pythonRuntime.Source - @setupArgs
exit $LASTEXITCODE
