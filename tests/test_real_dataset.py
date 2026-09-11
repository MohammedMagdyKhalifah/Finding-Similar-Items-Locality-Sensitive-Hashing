import hashlib, io, json, sys, tarfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import REAL_DATA, collection_documents, collection_zip, real_manifest
class RealDataset(unittest.TestCase):
 def test_provenance_and_sizes(self):
  meta=real_manifest();records=meta['files']
  self.assertEqual(len(records),1200)
  self.assertEqual(len({f['source_path'] for f in records}),1200)
  for f in records:
   self.assertEqual(hashlib.sha256((REAL_DATA/'files'/f['name']).read_bytes()).hexdigest(),f['sha256_utf8'])
  for n in (120,600,1200):self.assertEqual(len(collection_documents('real',n)),n)
 def test_original_archive_content(self):
  archive=REAL_DATA/'source.tar.gz'
  if not archive.exists():self.skipTest('Original download omitted from portable bundle')
  meta=real_manifest();self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),meta['archive_sha256'])
  wanted={f['source_path']:f for f in meta['files']}
  with tarfile.open(archive) as tar:
   for member in tar:
    if member.name in wanted:
     record=wanted.pop(member.name);raw=tar.extractfile(member).read()
     self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256_original'])
     self.assertEqual(raw.decode('latin-1'),(REAL_DATA/'files'/record['name']).read_bytes().decode('utf-8'))
  self.assertFalse(wanted)
 def test_zip_contains_exact_selected_files_and_attribution(self):
  with zipfile.ZipFile(io.BytesIO(collection_zip('real',120))) as z:
   self.assertEqual(len(z.namelist()),122)
   meta=json.loads(z.read('manifest.json'));self.assertEqual(len(meta['files']),120)
   self.assertIn('UCI',z.read('README.md').decode())
   for f in meta['files']:self.assertEqual(hashlib.sha256(z.read(f['name'])).hexdigest(),f['sha256_utf8'])
 def test_unknown_dataset_does_not_fall_back_to_synthetic(self):
  for dataset,n in [('other',120),('real',24)]:
   with self.assertRaises(ValueError):collection_documents(dataset,n)
if __name__=='__main__':unittest.main()
