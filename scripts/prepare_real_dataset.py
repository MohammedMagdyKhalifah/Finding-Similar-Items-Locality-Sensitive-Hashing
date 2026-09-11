"""Reproduce the bundled real-document subset from UCI's original archive."""
import hashlib, json, random, re, tarfile, urllib.request
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'datasets'/'20newsgroups'
URL='https://kdd.ics.uci.edu/databases/20newsgroups/20_newsgroups.tar.gz'
SOURCE='https://archive.ics.uci.edu/dataset/113/twenty%2Bnewsgroups'
GROUPS={'comp.graphics','comp.os.ms-windows.misc','comp.sys.ibm.pc.hardware','comp.sys.mac.hardware','comp.windows.x','sci.electronics','sci.space'}
def main():
 DEST.mkdir(parents=True,exist_ok=True)
 archive=DEST/'source.tar.gz'
 if not archive.exists(): urllib.request.urlretrieve(URL,archive)
 records=[]
 with tarfile.open(archive,'r:gz') as tar:
  for member in tar:
   parts=Path(member.name).parts
   if not member.isfile() or len(parts)<2 or parts[-2] not in GROUPS or not parts[-1].isdigit() or not 500<=member.size<=5000: continue
   raw=tar.extractfile(member).read()
   if b'\x00' in raw: continue
   # UCI's historical text is decoded losslessly with Latin-1, then saved as UTF-8.
   text=raw.decode('latin-1')
   message=re.search(r'^Message-ID:\s*(.+)$',text,re.M|re.I)
   records.append({'source_path':member.name,'name':parts[-2]+'__'+parts[-1]+'.txt','text':text,'message_id':message.group(1).strip() if message else None,'sha256_original':hashlib.sha256(raw).hexdigest(),'original_bytes':len(raw),'group':parts[-2]})
 records.sort(key=lambda f:f['source_path'])
 grouped=defaultdict(list)
 for f in records:
  if f['message_id']: grouped[f['message_id']].append(f)
 # Include source-authentic crossposts, not fabricated copies. Selection bias is documented.
 crossposts=[v for _,v in sorted(grouped.items()) if len(v)>1]
 selected=[]
 for group in crossposts:
  if len(selected)+len(group)>60: break
  selected.extend(group)
 seed_count=len(selected)
 names={f['name'] for f in selected}
 remainder=[f for f in records if f['name'] not in names]
 random.Random(2026).shuffle(remainder)
 selected.extend(remainder[:1200-len(selected)])
 assert len(selected)==1200 and len({f['source_path'] for f in selected})==1200
 (DEST/'files').mkdir(exist_ok=True)
 for f in selected:
  data=f.pop('text').encode('utf-8');(DEST/'files'/f['name']).write_bytes(data)
  f['sha256_utf8']=hashlib.sha256(data).hexdigest();f['bytes']=len(data)
 manifest={'title':'Twenty Newsgroups · real Usenet documents','source_url':SOURCE,'archive_url':URL,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'citation':'Mitchell, T. (1997). Twenty Newsgroups [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5C323','license':'CC BY 4.0, as listed by UCI','license_url':'https://creativecommons.org/licenses/by/4.0/','selection':f'Curated teaching subset of seven computing, electronics and space newsgroups. Original files of 500–5,000 bytes only. First {seed_count} records are original crossposts sharing a Message-ID; remaining records are sampled without replacement with seed 2026. Smaller presets are prefixes. This is not a random benchmark of the full corpus. No files are fabricated or duplicated by this app.','processing':'Original headers, body, quoted replies and signatures retained. Lossless Latin-1 decode followed by UTF-8 encode; no wording edits or truncation. Comparison additionally normalizes case and whitespace, as for all app inputs.','files':selected}
 (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 (DEST/'README.md').write_text('# Twenty Newsgroups: real document subset\n\n'+manifest['citation']+'\n\nSource: '+SOURCE+'\n\nArchive: '+URL+'\n\nLicense: '+manifest['license']+' — '+manifest['license_url']+'\n\n'+manifest['selection']+'\n\n'+manifest['processing']+'\n\nEach entry in manifest.json maps the UTF-8 file to its original archive path and SHA-256. Historical messages may include public author addresses and dated opinions. Category membership is not a near-duplicate label. Headers and quotations can contribute to overlap.\n',encoding='utf-8')
 print(json.dumps({'files':len(selected),'crosspost_seed_records':seed_count,'available_source_records':len(records),'utf8_bytes':sum(f['bytes'] for f in selected)}))
if __name__=='__main__':main()
