#!/usr/bin/env python3
"""Version & purpose gate: static evidence only, no project executables launched.

The self-check validates Teseo's claims/identities. Project inventory reports
candidate declarations; never equates manifest text with effective runtime.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$')
ID = re.compile(r'\b(?:N|D|FE|BE|ALG|RES|OBJ)-\d\d\b')
SUPPORTED = {'TESTED_SCOPE','IMPLEMENTED_LIMITED','DOCUMENTED_PROCEDURE','NOT_IMPLEMENTED'}


def _load_json(path):
    if path.is_symlink() or path.stat().st_size > 500_000:
        raise ValueError('unsafe metadata file')
    return json.loads(path.read_text(encoding='utf-8'))


def audit_self(root=ROOT):
    root=Path(root).resolve()
    errors=[]
    try:
        v=_load_json(root/'VERSION.json');c=_load_json(root/'CAPABILITIES.json')
        ver=v['release_version']; protocol=v['protocol_version']
        if not SEMVER.fullmatch(ver):errors.append('INVALID_SEMVER')
        if v['release_channel']=='release_candidate' and '-' not in ver:
            errors.append('CANDIDATE_MUST_HAVE_PRERELEASE')
        if not re.fullmatch(r'teseo-v\d+\.\d+',protocol):errors.append('INVALID_PROTOCOL_ID')
        if protocol not in v['guard_compatible_protocols']:errors.append('GUARD_PROTOCOL_NOT_SUPPORTED')
        for key in ['SKILL.md','README.md']:
            content=(root/key).read_text(encoding='utf-8')
            if f'v{ver}' not in content[:4500]:errors.append('VERSION_MISMATCH_'+key)
        criteria=(root/v['criteria']['file']).read_bytes()
        if hashlib.sha256(criteria).hexdigest()!=v['criteria']['sha256']:errors.append('CATALOG_SHA_DRIFT')
        ids=set(ID.findall(criteria.decode('utf-8'))) - {'N-01'}  # N-01 fue retirado en el catalogo historico
        if len(ids)!=v['criteria']['count'] or len(ids)!=77:errors.append('CATALOG_COUNT_DRIFT')
        if c.get('version_source')!='VERSION.json':errors.append('CAPABILITY_VERSION_SOURCE_DRIFT')
        known=set()
        for cap in c['capabilities']:
            code=cap['id']
            if code in known:errors.append('DUPLICATE_CAPABILITY_'+code)
            known.add(code)
            if cap['status'] not in SUPPORTED:errors.append('INVALID_CAPABILITY_STATUS_'+code)
            if not cap.get('claim'):errors.append('MISSING_CLAIM_'+code)
            if cap['status']!='NOT_IMPLEMENTED' and not cap['evidence']:
                errors.append('MISSING_EVIDENCE_'+code)
            for item in cap['evidence']:
                p=root/item
                if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):
                    errors.append('MISSING_EVIDENCE_FILE_'+code+':'+item)
        package=(root/'crear_skill_refactor_v2.5.py').read_text(encoding='utf-8')
        if 'release_version()' not in package or "ROOT/'VERSION.json'" not in package:
            errors.append('PACKAGER_NOT_VERSION_DRIVEN')
        runner=(root/'scripts/teseo_runner.py').read_text(encoding='utf-8')
        guard=(root/'scripts/git_guard.py').read_text(encoding='utf-8')
        if "'teseo-v2.5'" not in runner:errors.append('RUNNER_PROTOCOL_MISMATCH')
        for supported in v['guard_compatible_protocols']:
            if repr(supported) not in guard:errors.append('GUARD_PROTOCOL_MISMATCH_'+supported)
        if "pre['protocol']='teseo-v2.4'" in runner:errors.append('HIDDEN_PROTOCOL_REWRITE')
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        errors.append('METADATA_UNREADABLE:'+type(exc).__name__)
    return errors


MANIFESTS=(
    'package.json','pyproject.toml','Cargo.toml','go.mod','composer.json',
    'gradle.properties','pom.xml','Dockerfile','global.json','.tool-versions',
    '.nvmrc','.node-version','.python-version','Gemfile','*.csproj',
    'package-lock.json','pnpm-lock.yaml','yarn.lock','poetry.lock','Cargo.lock',
)

def inventory_project(root):
    root=Path(root).resolve(strict=True)
    if not root.is_dir(): raise ValueError('PROJECT_NOT_DIRECTORY')
    items=[]
    for pattern in MANIFESTS:
        for p in sorted(root.glob(pattern)):
            if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):continue
            size=p.stat().st_size
            if size>500_000:
                items.append({'path':p.name,'status':'SKIPPED_OVERSIZE'})
                continue
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            entry={'path':p.name,'sha256':h,'status':'DECLARED_CANDIDATE','effective_runtime':'UNVERIFIED'}
            if p.name=='package.json':
                try:
                    o=_load_json(p)
                    entry['declared_version']=o.get('version')
                    entry['engine_constraints']=o.get('engines',{})
                except (ValueError,OSError):entry['parse_status']='UNVERIFIED'
            elif p.name=='pyproject.toml':
                try:
                    import tomllib
                    o=tomllib.loads(p.read_text(encoding='utf-8'))
                    entry['declared_version']=o.get('project',{}).get('version')
                    entry['python_constraint']=o.get('project',{}).get('requires-python')
                except (UnicodeError,ValueError,OSError):entry['parse_status']='UNVERIFIED'
            items.append(entry)
    return {'root':str(root),'source':'STATIC_MANIFEST_EVIDENCE',
            'warning':'No executable, database, runtime or deployment is invoked. Declarations are candidates; effective versions, behavior and purpose require independent evidence.',
            'items':items}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-check',action='store_true')
    ap.add_argument('--project',type=Path)
    a=ap.parse_args()
    if a.self_check:
        errors=audit_self();print(json.dumps({'result':'PASS' if not errors else 'FAIL','errors':errors},indent=2))
        if errors:return 2
    if a.project:
        print(json.dumps(inventory_project(a.project),ensure_ascii=False,indent=2))
    if not a.self_check and a.project is None:
        ap.error('specify --self-check or --project PATH')
    return 0

if __name__=='__main__':sys.exit(main())
