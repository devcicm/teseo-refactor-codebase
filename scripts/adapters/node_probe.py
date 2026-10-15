#!/usr/bin/env python3
"""Adaptador opcional Node.js. Usar sólo si discovery confirma Node.js."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def cmd(a):
 try:
  p=subprocess.run(a,capture_output=True,text=True,timeout=8,check=False); return {'ok':p.returncode==0,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
 except Exception as e:return {'ok':False,'error':str(e)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); r=Path(a.root).resolve(); d={'adapter':'node','read_only_intent':True}
 if not shutil.which('node'): d['active']=False; d['reason']='node executable not found'; print(json.dumps(d,indent=2)); return
 d['active']=True; d['node_version']=cmd(['node','--version']); d['process_versions']=cmd(['node','-p','JSON.stringify(process.versions)'])
 for n in ('package.json','package-lock.json','npm-shrinkwrap.json','pnpm-lock.yaml','yarn.lock'):
  p=r/n
  if p.exists(): d.setdefault('artifacts',{})[n]={'sha256':sha(p),'bytes':p.stat().st_size}
 addons=[]
 nm=r/'node_modules'
 if nm.exists():
  for base,dirs,files in os.walk(nm):
   for f in files:
    if f.endswith('.node'): addons.append(str((Path(base)/f).relative_to(r)))
    if len(addons)>=100: break
   if len(addons)>=100: break
 d['native_addons']=addons
 print(json.dumps(d,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
