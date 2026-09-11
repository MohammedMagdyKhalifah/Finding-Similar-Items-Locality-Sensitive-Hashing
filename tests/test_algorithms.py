import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import shingles,jaccard,signatures,candidates,run_job,sample_documents
class Algorithms(unittest.TestCase):
 def test_lecture(self):
  self.assertEqual(shingles('abcab',2),{'ab','bc','ca'})
  self.assertEqual(jaccard({'apple','banana','orange'},{'apple','banana','mango'}),.5)
  self.assertEqual(shingles(' A  BCAB ',2),shingles('a bcab',2))
 def test_bands_and_deduplication(self):
  self.assertEqual(candidates([[1,2,3,4],[1,2,9,8],[1,9,3,8]],2,2),{(0,1)})
  self.assertEqual(candidates([[1,2,3,4]]*3,2,2),{(0,1),(0,2),(1,2)})
 def test_exact_ground_truth(self):
  files=[{'name':'a.txt','text':'abcabcabc'},{'name':'b.txt','text':'abcabcabc'},{'name':'c.txt','text':'xyzxyzxyz'}]
  job={};run_job(job,{'files':files,'k':2,'mode':'both'})
  self.assertEqual(job['status'],'complete');r=job['result']
  self.assertEqual(r['methods']['brute']['comparisons'],3)
  self.assertEqual(r['methods']['lsh']['count'],1)
  self.assertEqual(r['recall'],1)
 def test_empty_rejected_and_cancel(self):
  job={};run_job(job,{'files':[{'name':'empty','text':''},{'name':'full','text':'abcdef'}]})
  self.assertEqual(job['status'],'error')
  job={'cancel':True};run_job(job,{'files':sample_documents(4)})
  self.assertEqual(job['status'],'cancelled')
 def test_deterministic_signatures(self):
  sets=[shingles(f['text']) for f in sample_documents(4)]
  self.assertEqual(signatures(sets,4,2),signatures(sets,4,2))
if __name__=='__main__':unittest.main()
