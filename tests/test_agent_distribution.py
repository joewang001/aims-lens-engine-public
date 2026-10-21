"""Actual archive extraction/install and public-boundary regressions."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('package_agent',ROOT/'tools/package_agent_access.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)

class AgentDistributionTests(unittest.TestCase):
    def test_generated_files_are_exact_and_bundle_has_no_hidden_entries(self):
        data=package.artifacts()
        for name,value in data.items():self.assertEqual((package.BASE/name).read_bytes(),value)
        import io
        with zipfile.ZipFile(io.BytesIO(data['downloads/'+package.NAME])) as archive:
            names=archive.namelist();self.assertEqual(len(names),22)
            self.assertFalse(any(any(part in name for part in ('services/','.env','tests/','postgres','evidence/')) for name in names))
            self.assertEqual(hashlib.sha256(archive.read('aims-lens-skills/skills/aims-lens/scripts/aims_client.py')).hexdigest(),'044e8b3134e28bc54d73b7dfa11e5080c0ece1667d3fde5f95ab23e566755a45')
    def test_standalone_install_is_complete_and_dryrun_loads_no_credential(self):
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp);project=temp/'project with spaces';project.mkdir()
            with zipfile.ZipFile(package.BASE/'downloads'/package.NAME) as archive:archive.extractall(temp)
            run=subprocess.run([sys.executable,str(temp/'aims-lens-skills/setup.py'),'--project-root',str(project),'--host','codex','--install-only'],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertEqual(json.loads(run.stdout)['status'],'INSTALLED_NOT_CONNECTED')
            script=project/'.agents/skills/aims-lens/scripts/aims_client.py'
            run=subprocess.run([sys.executable,'-I',str(script),'capabilities'],capture_output=True,text=True,check=True)
            self.assertFalse(json.loads(run.stdout)['credential_loaded'])
    def test_public_scanner_still_rejects_real_secrets_and_candidate_content(self):
        from tools.scan_public_export import scan_line
        for path in ('agent-access/skills/aims-lens/scripts/aims_client.py','agent-access/README.md'):
            findings=[];scan_line(path,1,'password = '+repr('arbitrary-real-secret'),findings)
            self.assertTrue(any(f.severity=='blocker' for f in findings))
        findings=[];scan_line('agent-access/uploads/person.txt',1,'candidate '+'resume body',findings)
        self.assertTrue(any(f.severity=='blocker' for f in findings))

    def test_bootstrap_refuses_disabled_service_without_starting_setup(self):
        from unittest.mock import patch
        import io,contextlib
        code=(package.BASE/'bootstrap/download.py.in').read_text().replace('@BUNDLE@',package.NAME).replace('@SHA256@',hashlib.sha256((package.BASE/'downloads'/package.NAME).read_bytes()).hexdigest())
        bundle=(package.BASE/'downloads'/package.NAME).read_bytes()
        class Opener:
            def open(self,url,timeout=0):return io.BytesIO(bundle if 'raw.githubusercontent.com' in url else b'{"agent_onboarding_enabled":false}')
        with patch('urllib.request.build_opener',return_value=Opener()),patch.object(sys,'argv',['bootstrap','--host','codex']),patch('subprocess.run') as run,contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as result:exec(compile(code,'bootstrap','exec'),{'__name__':'__main__'})
        self.assertEqual(result.exception.code,3);run.assert_not_called();self.assertIn('SERVICE_NOT_ENABLED',out.getvalue())
