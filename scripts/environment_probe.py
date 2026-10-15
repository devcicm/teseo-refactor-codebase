#!/usr/bin/env python3
"""environment_probe.py — inventario operacional genérico READ-ONLY.

No presupone lenguaje, DB, framework ni hardware. Observa plataforma,
executables conocidos y artefactos de dependencia/build. La presencia de un
artefacto es evidencia candidata, NO prueba de que sea una dimensión activa E(P).
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess
from pathlib import Path

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

def run(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=8,check=False)
        out=(p.stdout or p.stderr).strip().splitlines()
        return {'ok':p.returncode==0,'code':p.returncode,'summary':out[0][:500] if out else ''}
    except Exception as e:
        return {'ok':False,'error':f'{type(e).__name__}: {e}'}

def artifacts(root:Path, limit=500):
    rows=[]
    for base,dirs,files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            p=Path(base)/name
            if name in ARTIFACT_NAMES or p.suffix.lower() in ARTIFACT_SUFFIXES:
                try: rows.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha256(p)})
                except OSError: continue
                if len(rows)>=limit: return rows+[{'truncated':True}]
    return sorted(rows,key=lambda x:x.get('path',''))

def probe(root:Path):
    root=root.resolve(); tools={}
    for name,args in TOOLS.items():
        if shutil.which(args[0]): tools[name]=run(args)
    return {
      'probe':'refactor-codebase-environment-v2.3','read_only_intent':True,
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
