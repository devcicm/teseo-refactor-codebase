import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evidence_graph import validate

class GraphTests(unittest.TestCase):
    def test_dangling_edge_blocked(self):
        d={'version':'teseo-evidence-v2.5','nodes':[{'id':'r','kind':'REQUIREMENT'}],
           'edges':[{'from':'r','to':'unknown'}]}
        self.assertEqual(validate(d)['status'],'BLOCKED')
    def test_graph_warning_without_hash(self):
        d={'version':'teseo-evidence-v2.5','nodes':[{'id':'e','kind':'EVIDENCE','source':'log'}], 'edges':[]}
        self.assertEqual(validate(d)['status'],'BLOCKED')
    def test_graph_with_valid_minimum(self):
        names=['REQUIREMENT','DECISION','SEGMENT','CHANGE','TEST','RESULT','EVIDENCE']
        nodes=[{'id':str(i),'kind':name} for i,name in enumerate(names)]
        for i in [3,4,5]:nodes[i]['commit']='1'*40
        nodes[6]['source']='tests/test.py:20';nodes[6]['sha256']='a'*64
        d={'version':'teseo-evidence-v2.5','nodes':nodes,
           'edges':[{'from':str(i),'to':str(i+1)} for i in range(6)]}
        self.assertEqual(validate(d)['status'],'VERIFIED')

if __name__=='__main__':unittest.main()
