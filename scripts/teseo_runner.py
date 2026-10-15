#!/usr/bin/env python3
"""Teseo v2.5: restricted single-file writer with identity checks and restore drill.

This is a controlled mutation primitive, NOT an OS sandbox. Its contract must
be issued outside the agent's editable directory by a trusted coordinator.
Reject if the agent can edit the contract, ledger or backups, or if multiple
uncoordinated processes can modify the worktree. No arbitrary shell execution.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_guard import check_contract, Blocked
from path_policy import authorized, open_parent_confined, Denied

MAX_CONTENT = 2_000_000

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def utc(s):
    if not isinstance(s,str): raise Blocked('MISSING_EXPIRY')
    try:
        d=datetime.fromisoformat(s.replace('Z','+00:00'))
        if d.tzinfo is None: raise ValueError('naive date')
        return d.astimezone(timezone.utc)
    except ValueError as e:
        raise Blocked('INVALID_EXPIRY') from e

def load_contract(p):
    p=Path(p).absolute()
    if p.is_symlink(): raise Blocked('CONTRACT_SYMLINK')
    c=json.loads(p.read_text(encoding='utf-8'))
    if c.get('protocol')!='teseo-v2.5': raise Blocked('WRONG_RUNNER_PROTOCOL')
    if not c.get('runId') or not c.get('approved',False): raise Blocked('UNAPPROVED_RUN')
    if utc(c.get('expiresAt'))<=datetime.now(timezone.utc): raise Blocked('EXPIRED_APPROVAL')
    root=Path(c['repository']['refactorWorktree']).resolve()
    state=Path(c['stateDir']).resolve()
    if state==root or state.is_relative_to(root): raise Blocked('STATE_INSIDE_MUTABLE_WORKTREE')
    if p==root or p.is_relative_to(root): raise Blocked('CONTRACT_INSIDE_MUTABLE_WORKTREE')
    if state==p.parent and p.name in ('ledger.jsonl','lock'): raise Blocked('STATE_CONFLICT')
    if not state.is_dir() or state.is_symlink(): raise Blocked('MISSING_TRUSTED_STATE_DIR')
    # The tool cannot certify who controls these files; restrict ordinary
    # group/world writes, but real separation requires OS principals.
    for path in (p,state):
        if path.stat().st_mode & 0o022: raise Blocked('UNSAFE_CONTRACT_OR_STATE_PERMISSIONS')
    return c

def read_regular(fd, name):
    try: f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
    except FileNotFoundError: return None
    try:
        s=os.fstat(f)
        if not stat.S_ISREG(s.st_mode) or s.st_size>MAX_CONTENT: raise Blocked('INVALID_TARGET_FILE')
        chunks=[]; total=0
        while True:
            data=os.read(f,65536)
            if not data: break
            total+=len(data)
            if total>MAX_CONTENT: raise Blocked('OVERSIZED_TARGET')
            chunks.append(data)
        return b''.join(chunks)
    finally: os.close(f)

def write_atomic(fd,name,data):
    tmp='.teseo-'+secrets.token_hex(16)
    f=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
    try:
        with os.fdopen(f,'wb',closefd=True) as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        # Leaf symlink replacement is not followed; parent's fd is pinned.
        os.replace(tmp,name,src_dir_fd=fd,dst_dir_fd=fd)
        os.fsync(fd)
    except BaseException:
        try: os.unlink(tmp,dir_fd=fd)
        except OSError: pass
        raise

def read_ledger(state):
    p=state/'ledger.jsonl'
    if not p.exists(): return []
    if p.is_symlink(): raise Blocked('LEDGER_SYMLINK')
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

def append_ledger(state,row):
    p=state/'ledger.jsonl'
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    try:
        os.write(fd,(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8'))
        os.fsync(fd)
    finally: os.close(fd)

def run(contract_path,intent_path,content_path=None,recover=False):
    c=load_contract(contract_path)
    intent=json.loads(Path(intent_path).read_text(encoding='utf-8'))
    if intent.get('runId')!=c['runId'] or not intent.get('stepId'):
        raise Blocked('INTENT_IDENTITY_MISMATCH')
    op='RECOVER' if recover else 'WRITE'
    if op not in c.get('authorizedOperations',[]): raise Blocked('OPERATION_NOT_AUTHORIZED')
    target=intent.get('target')
    try: authorized(target,c['scope']['allowedPaths'])
    except Denied as e: raise Blocked(str(e)) from e
    state=Path(c['stateDir']).resolve()
    lock_fd=os.open(state/'lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(lock_fd,fcntl.LOCK_EX)
        # Identity and allowed paths are checked under the local runner lock.
        pre=dict(c);pre['protocol']='teseo-v2.4'
        check_contract(pre,'preflight',target)
        ledger=read_ledger(state)
        run_id=c['runId']; step=intent['stepId']
        previous=[r for r in ledger if r.get('runId')==run_id and r.get('stepId')==step and r.get('op')=='PREPARED']
        committed=[r for r in ledger if r.get('runId')==run_id and r.get('stepId')==step and r.get('op')=='COMMITTED']
        if recover:
            if len(previous)!=1: raise Blocked('RECOVERY_STEP_NOT_FOUND_OR_AMBIGUOUS')
            old=previous[0]
            if old['target']!=target: raise Blocked('RECOVERY_TARGET_MISMATCH')
            if any(r.get('op')=='RECOVER' and r.get('stepId')==step for r in ledger):
                return {'status':'ALREADY_RECOVERED','stepId':step}
        elif previous:
            if not committed: raise Blocked('INTERRUPTED_STEP_REQUIRES_RECOVERY')
            if len(previous)==1 and len(committed)==1 and previous[0].get('expectedAfter')==intent.get('expectedAfterSha256') and previous[0]['target']==target:
                return {'status':'ALREADY_APPLIED','stepId':step}
            raise Blocked('DUPLICATE_STEP_DIFFERENT_INTENT')
        fd,name=open_parent_confined(Path(c['repository']['refactorWorktree']),target)
        try:
            before=read_regular(fd,name)
            expected=(old['expectedAfter'] if recover else intent.get('expectedBeforeSha256'))
            actual=sha(before) if before is not None else None
            if recover and actual==old['expectedBefore']:
                return {'status':'ALREADY_AT_BASELINE','stepId':step}
            if expected!=actual: raise Blocked('SOURCE_CONTENT_DRIFT')
            if recover:
                back=state/(old['backupName'])
                if back.is_symlink(): raise Blocked('BACKUP_SYMLINK')
                data=back.read_bytes()
                if sha(data)!=old['expectedBefore']:raise Blocked('CORRUPT_BACKUP')
            else:
                if not content_path: raise Blocked('CONTENT_REQUIRED')
                payload=Path(content_path)
                if payload.is_symlink() or not payload.is_file() or payload.stat().st_size>MAX_CONTENT:
                    raise Blocked('INVALID_PAYLOAD')
                data=payload.read_bytes()
                if len(data)>MAX_CONTENT or sha(data)!=intent.get('expectedAfterSha256'):
                    raise Blocked('PAYLOAD_HASH_MISMATCH')
                if before is None: raise Blocked('NEW_FILES_NOT_SUPPORTED')
                backup_name='before-'+secrets.token_hex(16)
                bfd=os.open(state/backup_name,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
                try:
                    with os.fdopen(bfd,'wb') as stream:
                        stream.write(before);stream.flush();os.fsync(stream.fileno())
                except BaseException:
                    raise
                append_ledger(state,{'runId':run_id,'stepId':step,'op':'PREPARED',
                                     'target':target,'expectedBefore':expected,
                                     'expectedAfter':sha(data),'backupName':backup_name})
            write_atomic(fd,name,data)
            if sha(read_regular(fd,name))!=sha(data): raise Blocked('POST_WRITE_MISMATCH')
        finally: os.close(fd)
        check_contract(pre,'postflight',target)
        row={'runId':run_id,'stepId':step,'op':'RECOVER' if recover else 'COMMITTED','target':target,
             'baselineCommit':c['repository'].get('baselineCommit'),
             'expectedBefore':expected,'expectedAfter':sha(data),
             'timestamp':datetime.now(timezone.utc).isoformat()}
        if not recover:row['backupName']=backup_name
        append_ledger(state,row)
        return {'status':'RECOVERED' if recover else 'APPLIED','stepId':step,'target':target,'sha256':sha(data)}
    finally:
        fcntl.flock(lock_fd,fcntl.LOCK_UN);os.close(lock_fd)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('operation',choices=['write','recover'])
    ap.add_argument('--contract',required=True)
    ap.add_argument('--intent',required=True)
    ap.add_argument('--content-file')
    args=ap.parse_args()
    try: result=run(args.contract,args.intent,args.content_file,args.operation=='recover')
    except (Blocked,Denied,KeyError,ValueError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','reason':str(e)}),file=sys.stderr)
        return 2
    print(json.dumps(result));return 0
if __name__=='__main__':sys.exit(main())
