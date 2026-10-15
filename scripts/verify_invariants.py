#!/usr/bin/env python3
"""Teseo v2.5 scoped comparison of explicit observed invariants.

No dynamic Python evaluation, no shell execution. A passing result only
verifies the named observations, never universal program equivalence.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

class ContractError(ValueError): pass

def compare(spec, before, after):
    kind=spec['comparator']
    if kind in ('exact','ordered'):
        return before==after
    if kind=='unordered':
        if not isinstance(before,list) or not isinstance(after,list):raise ContractError('UNORDERED_REQUIRES_ARRAYS')
        return sorted(json.dumps(v,sort_keys=True) for v in before)==sorted(json.dumps(v,sort_keys=True) for v in after)
    if kind=='numeric_tolerance':
        epsilon=spec.get('epsilon')
        if not isinstance(epsilon,(int,float)) or isinstance(epsilon,bool) or not math.isfinite(epsilon) or epsilon<0:
            raise ContractError('INVALID_EPSILON')
        if isinstance(before,bool) or isinstance(after,bool) or not isinstance(before,(int,float)) or not isinstance(after,(int,float)):
            raise ContractError('INVALID_NUMERIC_OBSERVATION')
        return math.isfinite(before) and math.isfinite(after) and abs(before-after)<=epsilon
    if kind=='resource_non_regression':
        if not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in (before,after)):
            raise ContractError('INVALID_RESOURCE_OBSERVATION')
        limit=spec.get('maxIncrease',0)
        if not isinstance(limit,(int,float)) or isinstance(limit,bool) or not math.isfinite(limit) or limit<0:
            raise ContractError('INVALID_RESOURCE_TOLERANCE')
        return after<=before+limit
    raise ContractError('UNSUPPORTED_COMPARATOR')

def verify(contract, baseline, current):
    if not isinstance(contract,dict) or contract.get('version')!='teseo-invariants-v2.5':raise ContractError('INVALID_SPEC')
    rows=[];ids=set()
    for s in contract.get('invariants',[]):
        key=s.get('id')
        if not isinstance(key,str) or not key or key in ids:raise ContractError('INVALID_OR_DUPLICATE_ID')
        ids.add(key)
        if key not in baseline or key not in current:
            rows.append({'id':key,'result':'UNVERIFIED','reason':'MISSING_OBSERVATION','critical':s.get('critical',True)})
            continue
        try:passcheck=compare(s,baseline[key],current[key])
        except (KeyError,ContractError) as err:
            rows.append({'id':key,'result':'UNVERIFIED','reason':str(err),'critical':s.get('critical',True)});continue
        rows.append({'id':key,'result':'PASS' if passcheck else 'FAIL','critical':s.get('critical',True)})
    if not rows: return {'status':'PARTIAL','evidence':rows,'reason':'NO_INVARIANTS'}
    if any(r['result']=='FAIL' and r['critical'] for r in rows):status='BLOCKED'
    elif any(r['result']!='PASS' for r in rows):status='PARTIAL'
    else:status='VERIFIED'
    return {'status':status,'scope':'ONLY_DECLARED_OBSERVATIONS','evidence':rows,
            'verified':sum(r['result']=='PASS' for r in rows),'total':len(rows)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--contract',required=True)
    ap.add_argument('--baseline',required=True)
    ap.add_argument('--current',required=True)
    a=ap.parse_args()
    try:r=verify(*[json.loads(Path(f).read_text()) for f in (a.contract,a.baseline,a.current)])
    except (ValueError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','reason':str(e)}));return 2
    print(json.dumps(r,indent=2));return 0 if r['status']=='VERIFIED' else 1
if __name__=='__main__':raise SystemExit(main())
