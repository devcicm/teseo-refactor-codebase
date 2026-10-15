#!/usr/bin/env python3
"""environment_probe.py — inventario operacional genérico READ-ONLY.

No presupone lenguaje, DB, framework ni hardware. Observa plataforma,
executables conocidos y artefactos de dependencia/build. La presencia de un
artefacto es evidencia candidata, NO prueba de que sea una dimensión activa E(P).
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil
from pathlib import Path
from path_policy import read_confined, Denied

SKIP_DIRS={'.git','.hg','.svn','node_modules','vendor','dist','build','target','bin','obj','.venv','venv','__pycache__','.next','.cache'}
TOOLS={
 'python':['python','--version'], 'python3':['python3','--version'], 'node':['node','--version'],
 'java':['java','-version'], 'dotnet':['dotnet','--version'], 'go':['go','version'],
 'rustc':['rustc','--version'], 'cargo':['cargo','--version'], 'gcc':['gcc','--version'],
 'clang':['clang','--version'], 'php':['php','--version'], 'ruby':['ruby','--version'],
 'npm':['npm','--version'], 'pnpm':['pnpm','--version'], 'yarn':['yarn','--version'],
 'pip':['pip','--version'], 'poetry':['poetry','--version'], 'uv':['uv','--version'],
 'mvn':['mvn','--version'], 'gradle':['gradle','--version']}
ARTIFACT_NAMES={
 'package.json','package-lock.json','npm-shrinkwrap.json','pnpm-lock.yaml','yarn.lock',
 'pyproject.toml','requirements.txt','poetry.lock','uv.lock','Pipfile','Pipfile.lock',
 'pom.xml','build.gradle','build.gradle.kts','gradle.lockfile','go.mod','go.sum',
 'Cargo.toml','Cargo.lock','composer.json','composer.lock','Gemfile','Gemfile.lock',
 'packages.lock.json','Directory.Packages.props','Makefile','CMakeLists.txt','Dockerfile'}
ARTIFACT_SUFFIXES={'.sln','.csproj','.fsproj','.vbproj'}


def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def installed_tools():
    """Passive presence-only inventory; never invoke a project-controlled executable."""
    result={}
    for name,args in TOOLS.items():
        candidate=shutil.which(args[0])
        if candidate:
            result[name]={'candidate_path':candidate,'executed':False,
                          'trust':'UNVERIFIED_PATH', 'version':'NOT_PROBED'}
    return result

def artifacts(root:Path, limit=500):
    rows=[]
    for base,dirs,files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (Path(base)/d).is_symlink()]
        for name in files:
            p=Path(base)/name
            if not p.is_symlink() and (name in ARTIFACT_NAMES or p.suffix.lower() in ARTIFACT_SUFFIXES):
                try:
                    relative=str(p.relative_to(root))
                    raw=read_confined(root, relative, max_bytes=10_000_000)
                    rows.append({'path':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                except (OSError, Denied): continue
                if len(rows)>=limit: return rows+[{'truncated':True}]
    return sorted(rows,key=lambda x:x.get('path',''))

def probe(root:Path):
    root=root.resolve()
    tools=installed_tools()
    return {
      'probe':'refactor-codebase-environment-v2.5','read_only_intent':True, 'external_commands_executed':0,
      'root':str(root),'cwd':os.getcwd(),
      'platform':{'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'python_for_probe':platform.python_version()},
      'detected_tools':tools,'candidate_artifacts':artifacts(root),
      'warning':'Discovery only: detected tools/artifacts are candidates. Activate E(P) dimensions only with project evidence.'}

def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r=Path(td); (r/'package.json').write_text('{}',encoding='utf-8'); (r/'go.mod').write_text('module x',encoding='utf-8')
        d=probe(r); paths={x.get('path') for x in d['candidate_artifacts']}
        assert {'package.json','go.mod'} <= paths
        assert d['read_only_intent'] is True
    print('SELF-TEST OK')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    if a.self_test: return self_test()
    print(json.dumps(probe(Path(a.root)),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
