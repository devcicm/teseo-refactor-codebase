#!/usr/bin/env python3
"""Deterministic Teseo v2.5 packager; canonical sources are repository files.

No network access or subprocess execution. Does not modify the source except
when explicitly called with --sync-manifest.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'MANIFEST.sha256'

def source_files():
    entries=[ROOT/'SKILL.md']
    for d,ext in (('references','*.md'),('scripts','*.py'),('tests','*.py')):
        entries.extend(p for p in (ROOT/d).rglob(ext) if p.is_file() and not p.is_symlink())
    return sorted(entries,key=lambda p:p.relative_to(ROOT).as_posix())

def manifest_text():
    return ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in source_files())

def build():
    expected=manifest_text()
    if not MANIFEST.exists() or MANIFEST.read_text()!=expected:
        raise RuntimeError('MANIFEST_DRIFT: run --sync-manifest after verifying source changes')
    out=ROOT/'dist';folder=out/'refactor-codebase'
    if folder.exists():shutil.rmtree(folder)
    folder.mkdir(parents=True)
    for src in source_files()+[MANIFEST]:
        target=folder/src.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(src.read_bytes())
    zpath=out/'refactor-codebase-v2.5.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(folder.rglob('*')):
            if not p.is_file():continue
            arcname='refactor-codebase/'+p.relative_to(folder).as_posix()
            info=zipfile.ZipInfo(arcname,(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644<<16)
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print('zip:',zpath)
    print('sha256:',hashlib.sha256(zpath.read_bytes()).hexdigest())
    print('source_files:',len(source_files()))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sync-manifest',action='store_true')
    ap.add_argument('--check',action='store_true')
    a=ap.parse_args()
    if a.sync_manifest:
        MANIFEST.write_text(manifest_text(),encoding='utf-8');print('MANIFEST UPDATED');return
    if a.check:
        if not MANIFEST.exists() or MANIFEST.read_text()!=manifest_text():
            raise SystemExit('MANIFEST_DRIFT')
        print('MANIFEST VERIFIED');return
    build()
if __name__=='__main__':main()
