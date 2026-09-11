"""Export unchanged annotated CUAD clause spans, with full source contracts."""
import hashlib,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'datasets'/'contracts'
URL='https://huggingface.co/datasets/theatticusproject/cuad/resolve/main/CUAD_v1/CUAD_v1.json'
CATEGORIES={'Cap On Liability','Uncapped Liability','Audit Rights','Anti-Assignment','Insurance','Exclusivity','Revenue/Profit Sharing','Minimum Commitment','Ip Ownership Assignment','Non-Compete','Change Of Control','Termination For Convenience','License Grant','Post-Termination Services','Warranty Duration','Source Code Escrow','No-Solicit Of Employees','Liquidated Damages'}
def main():
 DEST.mkdir(exist_ok=True,parents=True)
 if not (DEST/'source.json').exists():urllib.request.urlretrieve(URL,DEST/'source.json')
 source=json.loads((DEST/'source.json').read_text());records=[];seen=set();duplicates=0
 old_names={f['name'] for f in json.loads((DEST/'manifest.json').read_text())['files']} if (DEST/'manifest.json').exists() else set()
 (DEST/'files').mkdir(exist_ok=True);(DEST/'full_contracts').mkdir(exist_ok=True)
 for di,doc in enumerate(source['data']):
  full=doc['paragraphs'][0]['context'];cid=f'contract_{di+1:03d}'
  (DEST/'full_contracts'/f'{cid}.txt').write_text(full,encoding='utf-8')
  for pi,par in enumerate(doc['paragraphs']):
   for qa in par['qas']:
    category=qa['id'].split('__')[-1]
    if category not in CATEGORIES:continue
    for answer in qa['answers']:
     text=answer['text'];start=answer['answer_start']
     if not 180<=len(text)<=1600 or par['context'][start:start+len(text)]!=text:continue
     normalized=' '.join(text.lower().split())
     if normalized in seen:duplicates+=1;continue
     seen.add(normalized);name=f'{cid}__{re.sub("[^a-z0-9]+","_",category.lower()).strip("_")}__{start}_{start+len(text)}.txt'
     (DEST/'files'/name).write_text(text,encoding='utf-8')
     records.append({'name':name,'contract_id':cid,'contract_title':doc['title'],'category':category,'group':category,'source_path':f"CUAD_v1.json / {doc['title']} / paragraph {pi} / characters {start}:{start+len(text)}",'source_document_index':di,'source_paragraph_index':pi,'start':start,'end':start+len(text),'sha256_utf8':hashlib.sha256(text.encode()).hexdigest(),'bytes':len(text.encode())})
 meta={'title':'Contract clause comparison · CUAD','source_url':'https://www.atticusprojectai.org/cuad/','archive_url':URL,'source_sha256':hashlib.sha256((DEST/'source.json').read_bytes()).hexdigest(),'citation':'Hendrycks, D., Burns, C., Chen, A. & Ball, S. (2021). CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review. NeurIPS. The Atticus Project.','license':'CC BY 4.0','selection':f'All {len(records)} unique annotated spans of 180–1,600 characters in 18 substantive clause categories. {duplicates} repeated spans were removed after lowercasing and whitespace normalization. No edits, generated variants or artificially duplicated files. No selection based on a target similarity score.','processing':'Every excerpt is checked byte-for-byte against its annotated character range in a real source contract. Files are clause excerpts, not whole contracts. Full source contract text is included. Matching compares different source contracts, requires at least 90% character-shingle Jaccard by default, and excludes 100% set matches.','contract_count':len(set(f['contract_id']for f in records)),'categories':sorted(CATEGORIES),'files':records}
 (DEST/'manifest.json').write_text(json.dumps(meta,indent=2))
 (DEST/'README.md').write_text('# Real contract clause comparison\n\n'+meta['citation']+'\n\nSource: '+meta['source_url']+'\n\nLicense: '+meta['license']+' https://creativecommons.org/licenses/by/4.0/\n\n'+meta['selection']+'\n\n'+meta['processing']+'\n\nPurpose: retrieve similar clauses from other agreements and inspect actual wording differences. Text similarity does not establish legal equivalence or determine which agreement is preferable.\n')
 for old in old_names-{f['name'] for f in records}:
  (DEST/'files'/old).unlink(missing_ok=True)
 print(json.dumps({'clauses':len(records),'contracts':meta['contract_count'],'duplicates_removed':duplicates,'bytes':sum(f['bytes']for f in records)}))
if __name__=='__main__':main()
