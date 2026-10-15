#!/usr/bin/env python3
"""Adaptador opcional SQLite read-only. Usar sólo si discovery confirma SQLite."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('db'); a=ap.parse_args(); p=Path(a.db).resolve()
 con=sqlite3.connect(f'file:{p.as_posix()}?mode=ro',uri=True,timeout=2)
 try:
  c=con.cursor(); out={'adapter':'sqlite','read_only_intent':True,'path':str(p),'sqlite_version':sqlite3.sqlite_version}
  for k,q in {'database_list':'PRAGMA database_list','journal_mode':'PRAGMA journal_mode','user_version':'PRAGMA user_version','schema_version':'PRAGMA schema_version','foreign_keys':'PRAGMA foreign_keys','quick_check':'PRAGMA quick_check','foreign_key_check':'PRAGMA foreign_key_check'}.items():
   try: out[k]=c.execute(q).fetchall()
   except Exception as e: out[k]={'error':str(e)}
  rows=c.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE sql IS NOT NULL ORDER BY type,name").fetchall(); canonical='\n'.join(json.dumps(x,separators=(',',':')) for x in rows); out['schema_sha256']=hashlib.sha256(canonical.encode()).hexdigest(); out['schema_objects']=len(rows)
  print(json.dumps(out,ensure_ascii=False,indent=2))
 finally: con.close()
if __name__=='__main__': main()
