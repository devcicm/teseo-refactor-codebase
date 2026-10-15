#!/usr/bin/env python3
"""Tests adversariales contra repositorios efímeros; no toca repos del usuario."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MOD = Path(__file__).resolve().parents[1]/'scripts'/'git_guard.py'
spec = importlib.util.spec_from_file_location('git_guard', MOD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def g(repo, *args):
    return subprocess.run(['git','-C',str(repo),*args], check=True,
                          capture_output=True, text=True).stdout.strip()


class TestGitGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.original = d/'original'
        self.original.mkdir()
        g(self.original, 'init', '-q')
        g(self.original, 'config', 'user.email', 'test@example.invalid')
        g(self.original, 'config', 'user.name', 'Teseo Test')
        (self.original/'src').mkdir()
        (self.original/'src'/'valid.txt').write_text('baseline\n')
        (self.original/'outside.txt').write_text('baseline\n')
        g(self.original,'add','.')
        g(self.original,'commit','-qm','seed')
        self.refactor = d/'refactor'
        g(self.original, 'worktree', 'add', '-q', '-b', 'refactor/teseo-test', str(self.refactor))
        i = guard.identity(self.refactor)
        self.contract = {
            'protocol':'teseo-v2.4',
            'repository': {
                'refactorWorktree': i['worktree'], 'gitDir':i['gitDir'],
                'gitCommonDir':i['gitCommonDir'], 'expectedBranch':i['branch'],
                'lastVerifiedCommit':i['HEAD']},
            'scope':{'segment':'SEG-001', 'allowedPaths':['src/**']}
        }
    def tearDown(self):
        self.tmp.cleanup()
    def test_clean_preflight(self):
        self.assertIn('VERIFIED', guard.check_contract(self.contract,'preflight','src/valid.txt')['result'])
    def test_wrong_worktree(self):
        self.contract['repository']['refactorWorktree'] = str(self.original)
        with self.assertRaisesRegex(guard.Blocked,'(GITDIR|BRANCH|WORKTREE)_DRIFT'):
            guard.check_contract(self.contract,'preflight','src/valid.txt')
    def test_wrong_branch(self):
        self.contract['repository']['expectedBranch']='refs/heads/main'
        with self.assertRaisesRegex(guard.Blocked,'BRANCH_DRIFT'):
            guard.check_contract(self.contract,'preflight','src/valid.txt')
    def test_wrong_oid(self):
        self.contract['repository']['lastVerifiedCommit']='0'*40
        with self.assertRaisesRegex(guard.Blocked,'HEAD_DRIFT'):
            guard.check_contract(self.contract,'preflight','src/valid.txt')
    def test_path_escape(self):
        with self.assertRaisesRegex(guard.Blocked,'INVALID_PATH'):
            guard.check_contract(self.contract,'preflight','../original/outside.txt')
    def test_path_out_of_scope(self):
        with self.assertRaisesRegex(guard.Blocked,'OUT_OF_SCOPE'):
            guard.check_contract(self.contract,'preflight','outside.txt')
    def test_dirty_outside_scope(self):
        (self.refactor/'outside.txt').write_text('bad\n')
        with self.assertRaisesRegex(guard.Blocked,'DIRTY_OUTSIDE_SCOPE'):
            guard.check_contract(self.contract,'postflight')
    def test_good_modified_file(self):
        (self.refactor/'src'/'valid.txt').write_text('changed\n')
        self.assertIn('src/valid.txt', guard.check_contract(self.contract,'postflight')['dirtyTrackedAndUntracked'])
    def test_symlink_escape(self):
        link = self.refactor/'src'/'evil'
        try:
            link.symlink_to(self.original, target_is_directory=True)
        except OSError:
            self.skipTest('symlink unavailable')
        with self.assertRaisesRegex(guard.Blocked,'SYMLINK_PATH'):
            guard.check_contract(self.contract,'preflight','src/evil/outside.txt')
    def test_rogue_gitdir(self):
        self.contract['repository']['gitDir'] = self.contract['repository']['gitCommonDir']
        with self.assertRaisesRegex(guard.Blocked,'GITDIR_DRIFT'):
            guard.check_contract(self.contract,'preflight','src/valid.txt')
    def test_missing_scope(self):
        self.contract['scope']['allowedPaths']=[]
        with self.assertRaisesRegex(guard.Blocked,'EMPTY_SCOPE'):
            guard.check_contract(self.contract,'preflight','src/valid.txt')
    def test_rename_out_of_scope(self):
        g(self.refactor,'mv','outside.txt','outside-renamed.txt')
        with self.assertRaisesRegex(guard.Blocked,'DIRTY_OUTSIDE_SCOPE'):
            guard.check_contract(self.contract,'postflight')

if __name__ == '__main__':
    unittest.main(verbosity=2)
