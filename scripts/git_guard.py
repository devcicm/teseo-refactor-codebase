#!/usr/bin/env python3
"""Teseo 2.4: inspección Git y detección READ-ONLY de deriva.

No aplica un sandbox; NO intercepta comandos de otros agentes. El contrato se
considera confiable sólo cuando lo proporciona un coordinador externo al repo.
"""
import argparse
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

UNTRUSTED_GIT_ENV = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_CONFIG_COUNT', 'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG',
    'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM', 'GIT_TEMPLATE_DIR'
)


class Blocked(Exception):
    pass


def git(repo, *args, ok=True):
    env = dict(os.environ)
    for key in UNTRUSTED_GIT_ENV:
        env.pop(key, None)
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    env['GIT_OPTIONAL_LOCKS'] = '0'
    p = subprocess.run(['git', '-C', str(repo), '--no-pager', *args],
                       capture_output=True, env=env, check=False)
    if ok and p.returncode:
        raise Blocked(f'git {args[0]} failed: {p.stderr.decode(errors="replace")[:300]}')
    return p.stdout.decode('utf-8', errors='replace').strip()


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
        if not isinstance(pat, str) or not pat.strip() or pat.startswith('/') or '\\' in pat:
            raise Blocked('INVALID_SCOPE_PATTERN')
        if '..' in PurePosixPath(pat).parts or '.git' in PurePosixPath(pat).parts:
            raise Blocked('INVALID_SCOPE_PATTERN')
    return patterns


def check_path(root, relpath, patterns):
    if not isinstance(relpath, str) or not relpath or '\\' in relpath:
        raise Blocked('INVALID_PATH')
    rel = PurePosixPath(relpath)
    if rel.is_absolute() or '..' in rel.parts or '.git' in rel.parts or relpath in ('.', ''):
        raise Blocked('INVALID_PATH')
    normalized = rel.as_posix()
    if normalized.startswith('./'):
        normalized = normalized[2:]
    if not any(fnmatch.fnmatchcase(normalized, p) for p in patterns):
        raise Blocked(f'OUT_OF_SCOPE: {normalized}')
    root = Path(root).resolve()
    current = root
    for item in rel.parts:
        current = current / item
        if current.is_symlink():
            raise Blocked('SYMLINK_PATH')
    target = current.resolve()
    if not target.is_relative_to(root) or target == root:
        raise Blocked('OUTSIDE_WORKTREE')
    return normalized


def status_paths(repo):
    """Parse Git porcelain v1 -z, including rename/copy paths; ignores ignored files."""
    env = dict(os.environ)
    for key in UNTRUSTED_GIT_ENV:
        env.pop(key, None)
    env['GIT_OPTIONAL_LOCKS'] = '0'
    p = subprocess.run(['git', '-C', str(repo), '--no-pager', 'status',
                        '--porcelain=v1', '-z', '--untracked-files=all'],
                       capture_output=True, env=env, check=True)
    toks = p.stdout.split(b'\0')
    out = []
    i = 0
    while i < len(toks) and toks[i]:
        item = toks[i]
        if len(item) < 4 or item[2:3] != b' ':
            raise Blocked('UNEXPECTED_PORCELAIN')
        xy = item[:2]
        out.append(item[3:].decode(errors='surrogateescape'))
        i += 1
        if b'R' in xy or b'C' in xy:
            if i >= len(toks) or not toks[i]:
                raise Blocked('UNEXPECTED_PORCELAIN_RENAME')
            out.append(toks[i].decode(errors='surrogateescape'))
            i += 1
    return sorted(set(out))


def check_contract(contract, mode, target=None):
    if not isinstance(contract, dict) or contract.get('protocol') != 'teseo-v2.4':
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
