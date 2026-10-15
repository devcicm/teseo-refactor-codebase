#!/usr/bin/env python3
"""Compatibilidad v2.2.

v2.3 usa environment_probe.py como probe canónico y adaptadores condicionales.
Este wrapper conserva el entry point antiguo sin convertir Node/SQLite en gates.
"""
from __future__ import annotations
import argparse, json, runpy, subprocess, sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--sqlite-db'); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
 here=Path(__file__).resolve().parent
 if a.self_test:
  subprocess.check_call([sys.executable,str(here/'environment_probe.py'),'--self-test']); print('COMPAT SELF-TEST OK'); return
 p=subprocess.run([sys.executable,str(here/'environment_probe.py'),a.root],capture_output=True,text=True,check=False)
 try: env=json.loads(p.stdout)
 except Exception: env={'error':p.stderr or p.stdout}
 out={'compat_entrypoint':'runtime_probe.py','canonical':'environment_probe.py','environment':env,'optional_adapters':{}}
 # Preserve prior convenience only when evidence/explicit input activates it.
 node=subprocess.run([sys.executable,str(here/'adapters'/'node_probe.py'),a.root],capture_output=True,text=True,check=False)
 try:
  nd=json.loads(node.stdout)
  if nd.get('active'): out['optional_adapters']['node']=nd
 except Exception: pass
 if a.sqlite_db:
  sq=subprocess.run([sys.executable,str(here/'adapters'/'sqlite_probe.py'),a.sqlite_db],capture_output=True,text=True,check=False)
  try: out['optional_adapters']['sqlite']=json.loads(sq.stdout)
  except Exception: out['optional_adapters']['sqlite']={'error':sq.stderr or sq.stdout}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
