import hashlib,json,sys,unittest,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import CONTRACT_DATA,collection_documents,run_job,shingles,jaccard,signatures,PRIME
class ContractCases(unittest.TestCase):
 def test_every_excerpt_is_original_and_unique(self):
  source=json.loads((CONTRACT_DATA/'source.json').read_text());meta=json.loads((CONTRACT_DATA/'manifest.json').read_text());seen=set()
  for f in meta['files']:
   text=(CONTRACT_DATA/'files'/f['name']).read_bytes().decode('utf-8');original=source['data'][f['source_document_index']]['paragraphs'][f['source_paragraph_index']]['context']
   self.assertEqual(text,original[f['start']:f['end']]);self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),f['sha256_utf8'])
   normalized=' '.join(text.lower().split());self.assertNotIn(normalized,seen);seen.add(normalized)
  self.assertEqual(len(seen),4609)
 def test_meaningful_real_example(self):
  docs={f['name']:f for f in collection_documents('contracts',4609)}
  a=docs['contract_093__anti_assignment__43975_44612.txt'];b=docs['contract_174__anti_assignment__46567_47142.txt']
  self.assertNotEqual(a['contract_id'],b['contract_id']);self.assertIn('controlling interest',a['text']);self.assertIn('an interest',b['text'])
  self.assertAlmostEqual(jaccard(shingles(a['text']),shingles(b['text'])),.9166666666666666)
 def test_exact_matches_and_same_contract_are_excluded(self):
  files=[{'name':str(i),'text':t,'contract_id':cid}for i,(t,cid)in enumerate([('abcdefghi','a'),('abcdefghi','b'),('abcdefghj','a'),('abcdefghk','c')])]
  j={};run_job(j,dict(files=files,k=2,threshold=.5,mode='both',exclude_exact=True,cross_contract=True))
  self.assertEqual(j['status'],'complete')
  for m in j['result']['methods'].values():
   for pair in m['matches']:
    self.assertLess(pair['similarity'],1);self.assertNotEqual(files[pair['a']]['contract_id'],files[pair['b']]['contract_id'])
  self.assertEqual(j['result']['methods']['brute']['count'],4)
 def test_shared_row_hashing_preserves_reference_signatures(self):
  sets=[shingles('this is a small contract clause'),shingles('this is another small contract clause')]
  ids={s:i+1 for i,s in enumerate(sorted(set().union(*sets)))};rng=random.Random(42);funcs=[(rng.randrange(1,PRIME),rng.randrange(PRIME))for _ in range(12)]
  expected=[[min((a*ids[s]+c)%PRIME for s in doc)for a,c in funcs]for doc in sets]
  self.assertEqual(signatures(sets,4,3),expected)
if __name__=='__main__':unittest.main()
