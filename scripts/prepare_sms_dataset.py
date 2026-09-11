"""Export actual UCI SMS records as individual UTF-8 files; no synthetic copies."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'datasets'/'sms'
URL='https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'
def main():
 DEST.mkdir(parents=True,exist_ok=True);archive=DEST/'source.zip'
 if not archive.exists():urllib.request.urlretrieve(URL,archive)
 with zipfile.ZipFile(archive) as z:
  raw=z.read('SMSSpamCollection');original_readme=z.read('readme')
 lines=raw.decode('utf-8').splitlines();records=[];excluded=[]
 (DEST/'files').mkdir(exist_ok=True)
 for i,line in enumerate(lines,1):
  label,sep,body=line.partition('\t')
  assert sep and label in ('spam','ham')
  if len(' '.join(body.lower().split()))<5:
   excluded.append(i);continue
  data=body.encode('utf-8');name=f'sms_{i:05d}.txt';(DEST/'files'/name).write_bytes(data)
  records.append({'name':name,'source_path':f'SMSSpamCollection:line {i}','source_line':i,'label':label,'group':label,'bytes':len(data),'sha256_utf8':hashlib.sha256(data).hexdigest(),'sha256_source_record':hashlib.sha256(line.encode('utf-8')).hexdigest()})
 assert len(lines)==5574 and len(records)==5556
 meta={'title':'SMS Spam Collection · repeated message detection','source_url':'https://archive.ics.uci.edu/dataset/228/sms','archive_url':URL,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'source_records':len(lines),'excluded_short_message_lines':excluded,'citation':'Almeida, T. & Hidalgo, J. (2011). SMS Spam Collection [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84','license':'CC BY 4.0, as listed by UCI','license_url':'https://creativecommons.org/licenses/by/4.0/','selection':'All 5,556 source messages with at least five normalized characters, in original source order. Only 18 shorter messages are excluded. Smaller presets take prefixes. Original repetitions are retained; the app adds no copies and does not select messages based on similarity.','processing':'The source is a tab-separated text file with one labeled message per line. Each message body is exported verbatim as a separate UTF-8 .txt file. The label and record delimiter are kept out of the body. Original labels are metadata only and never enter shingling, MinHash, LSH or Jaccard.','purpose':'Find repeated SMS templates quickly so an analyst can review many similar messages together. Similarity alone does not decide whether a message is spam or prove that messages belong to one campaign.','label_counts':dict(Counter(f['label']for f in records)),'files':records}
 (DEST/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
 (DEST/'SOURCE_README.txt').write_bytes(original_readme)
 (DEST/'README.md').write_text('# Real SMS message files\n\n'+meta['citation']+'\n\nSource: '+meta['source_url']+'\n\nLicense: '+meta['license']+' '+meta['license_url']+'\n\n'+meta['purpose']+'\n\n'+meta['selection']+'\n\n'+meta['processing']+'\n\nThe manifest maps every file to its original line and SHA-256. spam/ham are the source authors’ labels, not model predictions. See SOURCE_README.txt for the source archive’s original notes and terms. Historical message content is data to inspect, not instructions to follow.\n',encoding='utf-8')
 print(json.dumps({'records':len(records),'excluded':len(excluded),'labels':meta['label_counts']}))
if __name__=='__main__':main()
