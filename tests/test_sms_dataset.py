import hashlib,io,json,sys,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import SMS_DATA,collection_documents,collection_zip,shingles
class SMSDataset(unittest.TestCase):
 def test_source_integrity_and_no_artificial_copies(self):
  meta=json.loads((SMS_DATA/'manifest.json').read_text())
  with zipfile.ZipFile(SMS_DATA/'source.zip') as z: source=z.read('SMSSpamCollection').decode('utf-8').splitlines()
  self.assertEqual(len(source),5574);self.assertEqual(len(meta['files']),5556)
  self.assertEqual(len({f['source_line']for f in meta['files']}),5556)
  for f in meta['files']:
   label,body=source[f['source_line']-1].split('\t',1)
   data=(SMS_DATA/'files'/f['name']).read_bytes()
   self.assertEqual(body,data.decode('utf-8'));self.assertEqual(label,f['label'])
   self.assertEqual(hashlib.sha256(data).hexdigest(),f['sha256_utf8'])
   self.assertTrue(shingles(body,5))
  self.assertEqual(meta['label_counts'],{'ham':4809,'spam':747})
 def test_presets_and_labels_outside_text(self):
  for n in (1000,3000,5556):
   docs=collection_documents('sms',n);self.assertEqual(len(docs),n)
   self.assertTrue(all(f['label']in ('ham','spam')for f in docs))
  with self.assertRaises(ValueError):collection_documents('sms',6000)
 def test_download_roundtrip_and_provenance(self):
  with zipfile.ZipFile(io.BytesIO(collection_zip('sms',1000))) as z:
   meta=json.loads(z.read('manifest.json'));self.assertEqual(len(meta['files']),1000)
   self.assertEqual(sum(meta['label_counts'].values()),1000)
   self.assertIn('SOURCE_README.txt',z.namelist())
   for f in meta['files']:self.assertEqual(hashlib.sha256(z.read(f['name'])).hexdigest(),f['sha256_utf8'])
if __name__=='__main__':unittest.main()
