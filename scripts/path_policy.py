#!/usr/bin/env python3
"""Shared, conservative path policy. Refuses symlinks and ambiguous globs.

Enforcement is POSIX-only. On unsupported platforms, callers must use an OS
sandbox or report UNSUPPORTED; they must not silently downgrade protection.
"""
from __future__ import annotations
import fnmatch
import os
from pathlib import Path, PurePosixPath

class Denied(Exception):
    pass

def components(path: str) -> tuple[str, ...]:
    if not isinstance(path, str) or not path or '\\' in path or '\x00' in path:
        raise Denied('INVALID_PATH')
    p = PurePosixPath(path)
    parts = p.parts
    if p.is_absolute() or not parts or any(x in ('.', '..', '.git') for x in parts):
        raise Denied('INVALID_PATH')
    if path.startswith('./') or '//' in path or path.endswith('/'):
        raise Denied('NON_CANONICAL_PATH')
    return parts

def matches(relative: str, pattern: str) -> bool:
    """Component-aware glob: * never crosses '/'; ** may cross directories."""
    a, b = components(relative), components(pattern)
    def go(i: int, j: int) -> bool:
        if j == len(b): return i == len(a)
        if b[j] == '**':
            return go(i, j+1) or (i < len(a) and go(i+1, j))
        return i < len(a) and fnmatch.fnmatchcase(a[i], b[j]) and go(i+1, j+1)
    return go(0,0)

def authorized(relative: str, patterns: list[str]) -> bool:
    if not isinstance(patterns,list) or not patterns: raise Denied('EMPTY_SCOPE')
    for pat in patterns: components(pat)
    components(relative)
    if not any(matches(relative, pat) for pat in patterns):
        raise Denied(f'OUT_OF_SCOPE: {relative}')
    return True

def _open_directory(root: Path, parts: tuple[str,...]) -> int:
    if os.name != 'posix' or not hasattr(os,'O_NOFOLLOW') or not hasattr(os,'O_DIRECTORY'):
        raise Denied('SECURE_DIRFD_UNSUPPORTED')
    root = Path(root)
    if root.is_symlink(): raise Denied('SYMLINK_ROOT')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in parts:
            nxt = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise

def read_confined(root: Path, relative: str, max_bytes: int = 2_000_000) -> bytes:
    parts=components(relative)
    fd = _open_directory(root, parts[:-1])
    try:
        f = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | getattr(os,'O_NONBLOCK',0), dir_fd=fd)
        try:
            import stat
            st=os.fstat(f)
            if not stat.S_ISREG(st.st_mode) or st.st_size>max_bytes: raise Denied('NOT_SMALL_REGULAR_FILE')
            data=bytearray()
            while True:
                chunk=os.read(f,min(65536,max_bytes+1-len(data)))
                if not chunk: break
                data.extend(chunk)
                if len(data)>max_bytes: raise Denied('OVERSIZED_FILE')
            return bytes(data)
        finally: os.close(f)
    finally: os.close(fd)

def open_parent_confined(root: Path, relative: str):
    """Return (dirfd, basename). Caller MUST close fd."""
    parts=components(relative)
    return _open_directory(root,parts[:-1]),parts[-1]
