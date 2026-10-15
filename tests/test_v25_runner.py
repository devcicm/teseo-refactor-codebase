"""Atomic write, idempotency and restore tests in disposable worktrees."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import teseo_runner as runner
from git_guard import identity,Blocked

def git(root,*args):
    return subprocess.run(['/usr/bin/git','-C',str(root),*args],capture_output=True,text=True,check=True).stdout.strip()

class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.orig=self.base/'original';self.orig.mkdir()
        git(self.orig,'init','-q');git(self.orig,'config','user.email','test@example.invalid');git(self.orig,'config','user.name','Fixture')
        (self.orig/'src').mkdir();(self.orig/'src'/'one.txt').write_text('before')
        (self.orig/'outside.txt').write_text('leave')
        git(self.orig,'add','.');git(self.orig,'commit','-qm','baseline')
        self.ref=self.base/'refactor'
        git(self.orig,'worktree','add','-q','-b','feat/teseo',str(self.ref))
        i=identity(self.ref)
        self.state=self.base/'control';self.state.mkdir(mode=0o700)
        c={'protocol':'teseo-v2.5','runId':'RUN-TEST','approved':True,
           'expiresAt':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
           'stateDir':str(self.state),'authorizedOperations':['WRITE','RECOVER'],
           'repository':{'refactorWorktree':i['worktree'],'gitDir':i['gitDir'],
                         'gitCommonDir':i['gitCommonDir'],'expectedBranch':i['branch'],
                         'lastVerifiedCommit':i['HEAD'],'baselineCommit':i['HEAD']},
           'scope':{'segment':'SEG-1','allowedPaths':['src/*.txt']}}
        self.contract=self.base/'run.json';self.contract.write_text(json.dumps(c));self.contract.chmod(0o600)
        self.intent=self.base/'intent.json';self.content=self.base/'payload.txt'
        self.content.write_text('after')
        self.make_intent('src/one.txt')
    def make_intent(self,target):
        self.intent.write_text(json.dumps({'runId':'RUN-TEST','stepId':'S1','target':target,
                   'expectedBeforeSha256':runner.sha(b'before'),
                   'expectedAfterSha256':runner.sha(b'after')}))
    def test_write_repeat_and_recover(self):
        self.assertEqual(runner.run(self.contract,self.intent,self.content)['status'],'APPLIED')
        self.assertEqual((self.ref/'src/one.txt').read_text(),'after')
        self.assertEqual((self.orig/'src/one.txt').read_text(),'before')
        self.assertEqual(runner.run(self.contract,self.intent,self.content)['status'],'ALREADY_APPLIED')
        self.assertEqual(runner.run(self.contract,self.intent,recover=True)['status'],'RECOVERED')
        self.assertEqual((self.ref/'src/one.txt').read_text(),'before')
        self.assertEqual(runner.run(self.contract,self.intent,recover=True)['status'],'ALREADY_RECOVERED')
    def test_reject_nested_path_overmatching_glob(self):
        (self.ref/'src'/'secret').mkdir()
        self.make_intent('src/secret/one.txt')
        with self.assertRaises(Blocked):runner.run(self.contract,self.intent,self.content)
    def test_reject_modified_target(self):
        (self.ref/'src/one.txt').write_text('changed by stranger')
        with self.assertRaisesRegex(Blocked,'SOURCE_CONTENT_DRIFT'):
            runner.run(self.contract,self.intent,self.content)
    def test_reject_expired_approval(self):
        c=json.loads(self.contract.read_text());c['expiresAt']='2020-01-01T00:00:00Z';self.contract.write_text(json.dumps(c))
        with self.assertRaisesRegex(Blocked,'EXPIRED_APPROVAL'):runner.run(self.contract,self.intent,self.content)
    def test_reject_unexpected_head(self):
        c=json.loads(self.contract.read_text());c['repository']['lastVerifiedCommit']='0'*40;self.contract.write_text(json.dumps(c))
        with self.assertRaisesRegex(Blocked,'HEAD_DRIFT'):runner.run(self.contract,self.intent,self.content)
    def test_recovery_rejects_unexpected_after_image(self):
        runner.run(self.contract,self.intent,self.content)
        (self.ref/'src/one.txt').write_text('different')
        with self.assertRaisesRegex(Blocked,'SOURCE_CONTENT_DRIFT'):
            runner.run(self.contract,self.intent,recover=True)
    def test_crash_after_prepared_can_recover(self):
        before=b'before';after=b'after';back='before-test.fixture'
        (self.state/back).write_bytes(before)
        runner.append_ledger(self.state,{'runId':'RUN-TEST','stepId':'S1',
           'op':'PREPARED','target':'src/one.txt',
           'expectedBefore':runner.sha(before),'expectedAfter':runner.sha(after),
           'backupName':back})
        (self.ref/'src/one.txt').write_bytes(after)
        with self.assertRaisesRegex(Blocked,'INTERRUPTED_STEP_REQUIRES_RECOVERY'):
            runner.run(self.contract,self.intent,self.content)
        self.assertEqual(runner.run(self.contract,self.intent,recover=True)['status'],'RECOVERED')
        self.assertEqual((self.ref/'src/one.txt').read_bytes(),before)
    def test_reject_shared_control_in_mutable_tree(self):
        c=json.loads(self.contract.read_text());c['stateDir']=str(self.ref/'state')
        (self.ref/'state').mkdir();self.contract.write_text(json.dumps(c))
        with self.assertRaisesRegex(Blocked,'STATE_INSIDE_MUTABLE_WORKTREE'):
            runner.run(self.contract,self.intent,self.content)

if __name__=='__main__':unittest.main()
