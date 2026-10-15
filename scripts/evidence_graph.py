#!/usr/bin/env python3
"""Validate explicit provenance links; never infer causal equivalence from a graph."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

KINDS=('REQUIREMENT','DECISION','SEGMENT','CHANGE','TEST','RESULT','EVIDENCE')
LINKS={('REQUIREMENT','DECISION'),('DECISION','SEGMENT'),('SEGMENT','CHANGE'),
       ('CHANGE','TEST'),('TEST','RESULT'),('RESULT','EVIDENCE')}
HEX=re.compile(r'^[a-fA-F0-9]{40,64}$')

def validate(doc):
    problems=[];warnings=[]
    if doc.get('version')!='teseo-evidence-v2.5':problems.append('BAD_SCHEMA')
    nodes=doc.get('nodes',[]);edges=doc.get('edges',[])
    index={}
    for n in nodes:
        key=n.get('id');kind=n.get('kind')
        if not key or key in index or kind not in KINDS:problems.append('BAD_OR_DUPLICATE_NODE');continue
        index[key]=n
        if kind=='EVIDENCE':
            if not HEX.fullmatch(str(n.get('sha256',''))):problems.append(f'{key}:MISSING_EVIDENCE_HASH')
            if not n.get('source'):problems.append(f'{key}:MISSING_SOURCE')
        if kind in ('CHANGE','TEST','RESULT') and not HEX.fullmatch(str(n.get('commit',''))):
            warnings.append(f'{key}:UNVERIFIED_COMMIT')
    for e in edges:
        a,b=e.get('from'),e.get('to')
        if a not in index or b not in index:
            problems.append('DANGLING_EDGE');continue
        if (index[a]['kind'],index[b]['kind']) not in LINKS:
            problems.append('INVALID_RELATION')
    if not nodes: warnings.append('EMPTY_GRAPH')
    if not any(n.get('kind')=='EVIDENCE' for n in nodes): warnings.append('NO_EVIDENCE_NODES')
    status='BLOCKED' if problems else 'PARTIAL' if warnings else 'VERIFIED'
    return {'status':status,'scope':'GRAPH_STRUCTURE_ONLY','nodes':len(nodes),'edges':len(edges),
            'problems':problems,'warnings':warnings}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('graph');a=ap.parse_args()
    try:res=validate(json.loads(Path(a.graph).read_text()))
    except (OSError,ValueError) as err:res={'status':'BLOCKED','problems':[str(err)]}
    print(json.dumps(res,indent=2));return 0 if res['status']=='VERIFIED' else 1
if __name__=='__main__':raise SystemExit(main())
