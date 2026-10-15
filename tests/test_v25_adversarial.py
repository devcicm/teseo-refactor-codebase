"""Failure injection on entirely synthetic disposable repos; no user assets."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from path_policy import matches,authorized,Denied,read_confined
import environment_probe,git_guard,verify_invariants

class Adversarial(unittest.TestCase):
    def test_scope_glob_stays_in_one_directory(self):
        self.assertTrue(matches('src/good.py','src/*.py'))
        self.assertFalse(matches('src/private/secret.py','src/*.py'))
        with self.assertRaises(Denied): authorized('src/private/secret.py',['src/*.py'])
        self.assertTrue(matches('src/private/good.py','src/**/*.py'))
    def test_environment_fake_executable_is_never_invoked(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);d=r/'bin';d.mkdir(); marker=r/'marker'
            exe=d/'node';exe.write_text(f'#!/bin/sh\ntouch "{marker}"\n')
            exe.chmod(0o755)
            old=os.environ['PATH']
            try:
                os.environ['PATH']=str(d)+os.pathsep+old
                profile=environment_probe.probe(r)
            finally:os.environ['PATH']=old
            self.assertFalse(marker.exists())
            self.assertFalse(profile['detected_tools']['node']['executed'])
    def test_discover_refuses_symlink_to_external(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);root=r/'repo';root.mkdir();external=r/'secret.js'
            external.write_text('entry.innerHTML = "outside"')
            (root/'fake.js').symlink_to(external)
            with self.assertRaises(OSError):
                read_confined(root,'fake.js')
            p=subprocess.run([sys.executable,str(SCRIPTS/'discover.py'),str(root),'--json'],capture_output=True,text=True,check=True)
            self.assertNotIn('fake.js',json.loads(p.stdout)['candidates'].get('FE-15',[]))
    def test_git_fsmonitor_does_not_execute(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);r=root/'repo';r.mkdir()
            subprocess.run(['/usr/bin/git','-C',str(r),'init','-q'],check=True)
            script=root/'monitor.sh';mark=root/'executed'
            script.write_text(f'#!/bin/sh\ntouch "{mark}"\nexit 0\n');script.chmod(0o755)
            subprocess.run(['/usr/bin/git','-C',str(r),'config','core.fsmonitor',str(script)],check=True)
            git_guard.status_paths(r)
            self.assertFalse(mark.exists())
    def test_invariants_do_not_hide_critical_failure(self):
        specs={'version':'teseo-invariants-v2.5','invariants':[{'id':'workflow','comparator':'exact','critical':True},{'id':'memory','comparator':'resource_non_regression'}]}
        out=verify_invariants.verify(specs,{'workflow':'OK','memory':3},{'workflow':'BROKEN','memory':1})
        self.assertEqual(out['status'],'BLOCKED')
        self.assertEqual(verify_invariants.verify(specs,{'workflow':'OK'},{'workflow':'OK'})['status'],'PARTIAL')
    def test_unknown_comparator_not_green(self):
        s={'version':'teseo-invariants-v2.5','invariants':[{'id':'x','comparator':'eval'}]}
        self.assertEqual(verify_invariants.verify(s,{'x':1},{'x':1})['status'],'PARTIAL')

if __name__=='__main__':unittest.main()
