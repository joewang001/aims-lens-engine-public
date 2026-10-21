"""OS-protected storage. No plaintext-file fallback or secret command arguments."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


class SecretStoreError(Exception):
    pass


def reference(origin, project):
    return hashlib.sha256((origin+'\n'+str(project)).encode()).hexdigest()


def _run(command, data=None):
    try:
        result=subprocess.run(command,input=data,capture_output=True,timeout=15)
    except (OSError,subprocess.TimeoutExpired):
        raise SecretStoreError('SECRET_STORE_UNAVAILABLE') from None
    if result.returncode:
        raise SecretStoreError('SECRET_STORE_UNAVAILABLE')
    return result.stdout


class Store:
    def __init__(self):
        if sys.platform=='win32':
            self.kind='windows-dpapi'
            buffer=ctypes.create_unicode_buffer(32768)
            if ctypes.WinDLL('shell32').SHGetFolderPathW(None,0x1c,None,0,buffer)!=0:
                raise SecretStoreError('SECRET_STORE_UNAVAILABLE')
            # Resolve the OS folder, not an agent-overridden environment path.
            self.root=Path(buffer.value)/'AIMS/agent-credentials'
            if self.root.is_symlink():
                raise SecretStoreError('UNSAFE_SECRET_DIRECTORY')
        elif sys.platform=='darwin' and shutil.which('security'):
            self.kind='macos-keychain'
        elif shutil.which('secret-tool'):
            self.kind='secret-service'
        else:
            raise SecretStoreError('NO_OS_SECRET_STORE')

    def _prepare_windows_store(self):
        # Enrollment writes prepare ACLs; normal API reads never mutate user storage.
        self.root.mkdir(parents=True,exist_ok=True)
        # Files also remain encrypted to this Windows account by DPAPI.
        import csv
        sid=list(csv.reader(_run(['whoami.exe','/user','/fo','csv','/nh']).decode().strip().splitlines()))[0][1]
        _run(['icacls.exe',str(self.root),'/inheritance:r','/grant:r','*'+sid+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F'])

    @staticmethod
    def _dpapi(data, decrypt=False):
        from ctypes import wintypes
        class Blob(ctypes.Structure):
            _fields_=[('length',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
        buffer=ctypes.create_string_buffer(data)
        source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)))
        target=Blob()
        library=ctypes.WinDLL('crypt32',use_last_error=True)
        operation=library.CryptUnprotectData if decrypt else library.CryptProtectData
        operation.restype=wintypes.BOOL
        if not operation(ctypes.byref(source),None,None,None,None,1,ctypes.byref(target)):
            raise SecretStoreError('DPAPI_FAILED')
        try:
            return ctypes.string_at(target.data,target.length)
        finally:
            ctypes.memset(target.data,0,target.length)
            kernel=ctypes.WinDLL('kernel32',use_last_error=True)
            kernel.LocalFree.argtypes=[ctypes.c_void_p]
            kernel.LocalFree(ctypes.cast(target.data,ctypes.c_void_p))

    def save(self, ref, value):
        if not re.fullmatch(r'[0-9a-f]{64}',ref):
            raise SecretStoreError('INVALID_SECRET_REFERENCE')
        raw=json.dumps(value,separators=(',',':')).encode()
        if self.kind=='windows-dpapi':
            self._prepare_windows_store()
            path=self.root/(ref+'.dpapi')
            if path.is_symlink():
                raise SecretStoreError('UNSAFE_SECRET_FILE')
            encrypted=self._dpapi(raw)
            fd,name=tempfile.mkstemp(prefix=ref+'.',suffix='.tmp',dir=self.root)
            temporary=Path(name)
            try:
                with os.fdopen(fd,'wb') as stream:
                    stream.write(encrypted)
                    stream.flush()
                    os.fsync(stream.fileno())
                temporary.replace(path)
            finally:
                if temporary.exists():temporary.unlink()
        elif self.kind=='secret-service':
            _run(['secret-tool','store','--label=AIMS Agent Access','application','aims-lens','account',ref],raw)
        else:
            # security's interactive command input avoids putting the secret in argv.
            # JSON is hex encoded; no quotes, whitespace or command delimiters enter it.
            command='add-generic-password -U -a '+ref+' -s aims-lens -w '+raw.hex()+'\n'
            _run(['security','-i'],command.encode())

    def load(self, ref):
        if not re.fullmatch(r'[0-9a-f]{64}',ref):
            raise SecretStoreError('INVALID_SECRET_REFERENCE')
        try:
            if self.kind=='windows-dpapi':
                path=self.root/(ref+'.dpapi')
                if path.is_symlink():
                    raise SecretStoreError('UNSAFE_SECRET_FILE')
                data=self._dpapi(path.read_bytes(),True)
            elif self.kind=='secret-service':
                data=_run(['secret-tool','lookup','application','aims-lens','account',ref])
            else:
                data=bytes.fromhex(_run(['security','find-generic-password','-a',ref,'-s','aims-lens','-w']).decode().strip())
            return json.loads(data)
        except (OSError,ValueError):
            raise SecretStoreError('SECRET_NOT_AVAILABLE') from None
