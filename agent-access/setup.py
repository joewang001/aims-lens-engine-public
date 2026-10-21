"""Single setup entry point shared by shell, PowerShell and agent instructions."""
from pathlib import Path
import runpy
import sys
directory=Path(__file__).resolve().parent/'skills/aims-lens/scripts'
sys.path.insert(0,str(directory))
runpy.run_path(str(directory/'aims_setup.py'),run_name='__main__')
