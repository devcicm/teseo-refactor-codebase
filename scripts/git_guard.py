#!/usr/bin/env python3
"""Teseo 2.4: inspección Git y detección READ-ONLY de deriva.

No aplica un sandbox; NO intercepta comandos de otros agentes. El contrato se
considera confiable sólo cuando lo proporciona un coordinador externo al repo.
"""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_policy import authorized, components, Denied, open_parent_confined

TRUSTED_GIT = '/usr/bin/git' if Path('/usr/bin/git').is_file() else None

UNTRUSTED_GIT_ENV = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_CONFIG_COUNT', 'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG',
    'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM', 'GIT_TEMPLATE_DIR'
)


class Blocked(Exception):
    pass


def git_environment():
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('GIT_'):
            env.pop(key, None)
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['GIT_CONFIG_GLOBAL'] = os.devnull
    env['GIT_CONFIG_SYSTEM'] = os.devnull
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_EXTERNAL_DIFF'] = '0'
    return env


def git(repo, *args, ok=True):
    if not TRUSTED_GIT or not os.path.isabs(TRUSTED_GIT):
        raise Blocked('TRUSTED_GIT_UNAVAILABLE')
    command=[TRUSTED_GIT, '-C', str(repo), '--no-optional-locks',
             '-c', 'core.fsmonitor=false',
             '-c', 'core.hooksPath=/dev/null',
             '-c', 'core.untrackedCache=false',
             '-c', 'diff.external=false',
             '--no-pager', *args]
    p=subprocess.run(command,capture_output=True,env=git_environment(),check=False,timeout=20)
    if ok and p.returncode:
        raise Blocked(f'git {args[0]} failed: {p.stderr.decode(errors="replace")[:300]}')
    return p.stdout.decode('utf-8',errors='replace').strip()

def identity(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise Blocked('NOT_A_DIRECTORY')
    git_root = Path(git(root, 'rev-parse', '--show-toplevel')).resolve()
    git_dir = Path(git(root, 'rev-parse', '--absolute-git-dir')).resolve()
    git_common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    branch = git(root, 'symbolic-ref', '-q', 'HEAD', ok=False)
    oid = git(root, 'rev-parse', '--verify', 'HEAD')
    return dict(worktree=str(git_root), gitDir=str(git_dir),
                gitCommonDir=str(git_common), branch=branch,
                HEAD=oid, detached=not bool(branch))


def safe_patterns(patterns):
    if not isinstance(patterns, list) or not patterns:
        raise Blocked('EMPTY_SCOPE')
    for pat in patterns:
        try: components(pat)
        except Denied as e: raise Blocked(str(e)) from e
    return patterns


def check_path(root, relpath, patterns):
    try:
        authorized(relpath, patterns)
        rel=components(relpath)
        current=Path(root).resolve()
        for item in rel:
            current=current/item
            if current.is_symlink(): raise Blocked('SYMLINK_PATH')
        target=current.resolve()
        if not target.is_relative_to(Path(root).resolve()):
            raise Blocked('OUTSIDE_WORKTREE')
    except Denied as e:
        raise Blocked(str(e)) from e
    return relpath

def status_paths(repo):
    """Parse porcelain-v1 -z. No repo-provided fsmonitor or hooks executed."""
    if not TRUSTED_GIT: raise Blocked('TRUSTED_GIT_UNAVAILABLE')
    cmd=[TRUSTED_GIT, '-C', str(repo), '--no-optional-locks',
         '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null',
         '-c', 'core.untrackedCache=false', '--no-pager', 'status',
         '--porcelain=v1', '-z', '--untracked-files=all']
    p=subprocess.run(cmd,capture_output=True,env=git_environment(),check=True,timeout=20)
    toks=p.stdout.split(b'\0')
    out=[]; i=0
    while i<len(toks) and toks[i]:
        item=toks[i]
        if len(item)<4 or item[2:3]!=b' ':
            raise Blocked('UNEXPECTED_PORCELAIN')
        xy=item[:2]
        out.append(item[3:].decode(errors='surrogateescape'))
        i+=1
        if b'R' in xy or b'C' in xy:
            if i>=len(toks) or not toks[i]:
                raise Blocked('UNEXPECTED_PORCELAIN_RENAME')
            out.append(toks[i].decode(errors='surrogateescape'))
            i+=1
    return sorted(set(out))

def check_contract(contract, mode, target=None):
    if not isinstance(contract, dict) or contract.get('protocol') not in ('teseo-v2.4', 'teseo-v2.5'):
        raise Blocked('INVALID_CONTRACT_VERSION')
    repo = contract.get('repository', {})
    must = ('refactorWorktree', 'gitDir', 'gitCommonDir', 'expectedBranch', 'lastVerifiedCommit')
    if not all(isinstance(repo.get(k), str) and repo[k] for k in must):
        raise Blocked('INCOMPLETE_IDENTITY')
    root = Path(repo['refactorWorktree'])
    if not root.is_absolute():
        raise Blocked('NON_ABSOLUTE_WORKTREE')
    actual = identity(root)
    expected = {
        'worktree': str(root.resolve()),
        'gitDir': str(Path(repo['gitDir']).resolve()),
        'gitCommonDir': str(Path(repo['gitCommonDir']).resolve()),
        'branch': repo['expectedBranch'],
        'HEAD': repo['lastVerifiedCommit'],
    }
    for k, v in expected.items():
        if actual[k] != v:
            raise Blocked(f'{k.upper()}_DRIFT expected={v!r} actual={actual[k]!r}')
    patterns = safe_patterns(contract.get('scope', {}).get('allowedPaths'))
    if target:
        check_path(root, target, patterns)
    dirty = status_paths(root)
    violations = []
    for p in dirty:
        try:
            check_path(root, p, patterns)
        except Blocked as ex:
            violations.append({'path': p, 'reason': str(ex)})
    if violations:
        raise Blocked('DIRTY_OUTSIDE_SCOPE: '+ json.dumps(violations, ensure_ascii=False))
    return {'result': 'VERIFIED_PREFLIGHT' if mode == 'preflight' else 'VERIFIED_POSTFLIGHT',
            'identity': actual, 'target': target, 'dirtyTrackedAndUntracked': dirty,
            'limitations': ['Does not inspect ignored files', 'Not a write interceptor',
                            'TOCTOU possible without a trusted runner']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    inp = sub.add_parser('inspect', help='read-only worktree identity/status')
    inp.add_argument('--repo', required=True)
    for name in ('preflight','postflight'):
        p = sub.add_parser(name, help='detect drift with trusted external contract (read-only)')
        p.add_argument('--contract', required=True)
        p.add_argument('--target', help='relative path of intended edit')
    args = parser.parse_args()
    try:
        if args.cmd == 'inspect':
            result = {'identity': identity(args.repo), 'dirtyTrackedAndUntracked': status_paths(args.repo)}
        else:
            c = json.loads(Path(args.contract).read_text(encoding='utf-8'))
            result = check_contract(c, args.cmd, args.target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (Blocked, OSError, subprocess.CalledProcessError, ValueError, KeyError) as ex:
        print(json.dumps({'result': 'BLOCKED', 'reason': str(ex)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
