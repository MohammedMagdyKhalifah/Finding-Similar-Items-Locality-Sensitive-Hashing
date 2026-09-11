"""Similarity Lab: Python standard-library server. Run: python3 app.py."""
import csv, io, json, math, random, re, threading, time, uuid, zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parent
PRIME = 4294967311
JOBS = {}
POOL = ThreadPoolExecutor(max_workers=1)
REAL_DATA = ROOT/'datasets'/'20newsgroups'
SMS_DATA = ROOT/'datasets'/'sms'
CONTRACT_DATA = ROOT/'datasets'/'contracts'
MAX_FILES = 6000

def real_manifest():
    return json.loads((REAL_DATA/'manifest.json').read_text(encoding='utf-8'))

def collection_documents(dataset, n):
    if dataset=='contracts':
        meta=json.loads((CONTRACT_DATA/'manifest.json').read_text())
        if n not in (1000,len(meta['files'])): raise ValueError('Choose a supported contract collection')
        return [dict(f,text=(CONTRACT_DATA/'files'/f['name']).read_bytes().decode('utf-8')) for f in meta['files'][:n]]
    if dataset == 'sms':
        if n not in (1000,3000,5556): raise ValueError('Choose 1,000, 3,000 or 5,556 SMS files')
        meta=json.loads((SMS_DATA/'manifest.json').read_text(encoding='utf-8'))
        return [dict(name=f['name'],text=(SMS_DATA/'files'/f['name']).read_bytes().decode('utf-8'),group=f['label'],label=f['label'],source_path=f['source_path']) for f in meta['files'][:n]]
    if dataset == 'classroom':
        return sample_documents(n)
    if dataset != 'real' or n not in (120, 600, 1200):
        raise ValueError('Choose a valid dataset and file count')
    return [dict(name=f['name'], text=(REAL_DATA/'files'/f['name']).read_bytes().decode('utf-8'),
                 group=f['group'], source_path=f['source_path']) for f in real_manifest()['files'][:n]]

def collection_zip(dataset, n):
    documents = collection_documents(dataset, n)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in documents:
            z.writestr(f['name'], f['text'])
        if dataset in ('real','sms','contracts'):
            folder = CONTRACT_DATA if dataset=='contracts' else SMS_DATA if dataset=='sms' else REAL_DATA
            manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
            manifest['files'] = manifest['files'][:n]
            if dataset=='sms': manifest['label_counts']=dict(Counter(f['label'] for f in manifest['files']))
            z.writestr('manifest.json', json.dumps(manifest, indent=2))
            z.writestr('README.md', (folder/'README.md').read_text(encoding='utf-8'))
            if dataset=='contracts':
                for cid in sorted({f['contract_id'] for f in manifest['files']}):
                    z.writestr('full_contracts/'+cid+'.txt',(CONTRACT_DATA/'full_contracts'/f'{cid}.txt').read_bytes())
            if dataset=='sms':
                z.writestr('SOURCE_README.txt',(SMS_DATA/'SOURCE_README.txt').read_bytes())
        else:
            z.writestr('README.md', 'Original synthetic classroom documents. The eight-file case contains authored campus announcements. Larger collections are generated with seed 2026. These are not internet-sourced documents.\n')
    return buf.getvalue()

def shingles(text, k=5):
    """Character shingles, normalized case and whitespace; exact strings retained."""
    text = ' '.join(text.lower().split())
    return {text[i:i+k] for i in range(max(0, len(text)-k+1))}

def jaccard(a, b):
    intersection = len(a & b)
    union = len(a) + len(b) - intersection
    return intersection / union if union else 1.0

def signatures(sets, bands, rows, report=lambda *a: None):
    # Shared row IDs eliminate shingle-hash collisions within this corpus.
    universe = sorted(set().union(*sets))
    ids = {s: i+1 for i, s in enumerate(universe)}
    rng = random.Random(42)
    funcs = [(rng.randrange(1, PRIME), rng.randrange(PRIME)) for _ in range(bands*rows)]
    # Calculate each shared row hash once, process all documents, then discard it.
    # Only one hash column is resident, instead of a vocabulary × signature cache.
    from array import array
    document_rows = [[ids[s] for s in doc] for doc in sets]
    result = [[] for _ in sets]
    for h, (a, c) in enumerate(funcs):
        column = array('Q', ((a*x+c) % PRIME for x in range(len(universe)+1)))
        for i, values in enumerate(document_rows):
            result[i].append(min(map(column.__getitem__, values), default=PRIME))
        report('MinHash · shared row hashing', h+1, len(funcs))
    return result

def candidates(sigs, bands, rows, report=lambda *a: None):
    pairs = set()
    for b in range(bands):
        buckets = defaultdict(list)
        for i, sig in enumerate(sigs): buckets[tuple(sig[b*rows:(b+1)*rows])].append(i)
        for group in buckets.values(): pairs.update(combinations(group, 2))
        report('Hashing bands into buckets', b+1, bands)
    return pairs

def sample_documents(n=240):
    """Original classroom files: revision families of campus project reports."""
    if n == 8:
        return [{'name':p.name,'text':p.read_text()} for p in sorted((ROOT/'case_files').glob('*.txt'))]
    rng = random.Random(2026)
    topics = ['library search', 'solar energy', 'water quality', 'campus transport', 'student attendance', 'network security', 'recycling program', 'research archive']
    vocab = ['analysis','sensor','report','quality','system','method','experiment','design','review','learning','results','storage','measurement','service','project','access','sample','collection','update','capacity','process','signal','record','resource','planning','testing','model','output','training','monitor']
    docs=[]
    for family in range(math.ceil(n/4)):
        topic=topics[family%len(topics)]
        # Different report bodies avoid a corpus dominated by shared boilerplate.
        body=' '.join(rng.choices(vocab,k=95))
        base=f'Project {family+1}: {topic}. '+body+'. The team will review these findings at the next meeting.'
        for version in range(4):
            words=base.split()
            for _ in range(version*2): words[rng.randrange(8,len(words)-10)]=rng.choice(vocab)
            docs.append({'name':f'report_{family+1:03d}_v{version+1}.txt','text':' '.join(words)+'\n'})
    return docs[:n]

def run_job(job, data):
    def report(stage, done, total):
        if job.get('cancel'): raise InterruptedError('Run cancelled')
        job.update(stage=stage, done=done, total=total, elapsed=time.perf_counter()-job['started'])
    try:
        job['started']=time.perf_counter()
        files=data['files']; k=int(data.get('k',5)); b=int(data.get('bands',20)); r=int(data.get('rows',5)); threshold=float(data.get('threshold',.8)); mode=data.get('mode','both'); exclude_exact=bool(data.get('exclude_exact',False)); cross_contract=bool(data.get('cross_contract',False))
        if cross_contract: exclude_exact=True
        report('Building exact shingle sets',0,len(files))
        t=time.perf_counter(); sets=[]
        for i,f in enumerate(files):
            s=shingles(f['text'],k)
            if not s: raise ValueError(f"{f['name']}: needs at least {k} normalized characters")
            sets.append(s); report('Building exact shingle sets',i+1,len(files))
        prep=time.perf_counter()-t
        total=len(files)*(len(files)-1)//2
        result={'n':len(files),'all_pairs':total,'shingling_seconds':prep,'methods':{},'config':{'k':k,'bands':b,'rows':r,'threshold':threshold,'exclude_exact':exclude_exact,'cross_contract':cross_contract}}
        found={}
        for method in (['brute','lsh'] if mode=='both' else [mode]):
            start=time.perf_counter(); index_seconds=0
            if method=='lsh':
                sig=signatures(sets,b,r,report); pairs=candidates(sig,b,r,report); count=len(pairs); index_seconds=time.perf_counter()-start
            else: pairs=combinations(range(len(files)),2); count=total
            matches=[]; keys=set(); verify_start=time.perf_counter()
            report('Exact verification · '+method,0,count)
            for q,(i,j) in enumerate(pairs):
                score=jaccard(sets[i],sets[j])
                different_contract=not cross_contract or (files[i].get('contract_id') and files[j].get('contract_id') and files[i]['contract_id']!=files[j]['contract_id'])
                if score>=threshold and (not exclude_exact or score<1.0) and different_contract:
                    keys.add((i,j)); matches.append({'a':i,'b':j,'left':files[i]['name'],'right':files[j]['name'],'similarity':score})
                if q%500==0: report('Exact verification · '+method,q+1,count)
            verify_seconds=time.perf_counter()-verify_start
            elapsed=time.perf_counter()-start+prep
            matches.sort(key=lambda x:(-x['similarity'],x['left'],x['right']))
            result['methods'][method]={'seconds':elapsed,'index_seconds':index_seconds,'verify_seconds':verify_seconds,'comparisons':count,'matches':matches,'count':len(matches)}
            found[method]=keys
            job['partial']=result.copy()
        if mode=='both':
            result['missed']=len(found['brute']-found['lsh']); result['recall']=len(found['brute']&found['lsh'])/len(found['brute']) if found['brute'] else None
            result['speedup']=result['methods']['brute']['seconds']/result['methods']['lsh']['seconds']
        job.update(status='complete',stage='Complete',result=result,elapsed=time.perf_counter()-job['started'])
    except InterruptedError: job.update(status='cancelled',stage='Cancelled')
    except Exception as e: job.update(status='error',error=str(e))

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send(self, body, content='application/json', status=200, filename=None):
        if isinstance(body,(dict,list)): body=json.dumps(body).encode()
        if isinstance(body,str): body=body.encode()
        self.send_response(status); self.send_header('Content-Type',content); self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        if filename: self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        from urllib.parse import urlparse,parse_qs
        u=urlparse(self.path); q=parse_qs(u.query)
        if u.path in ('/api/sample', '/api/download', '/api/dataset-info'):
            try:
                dataset=q.get('dataset',['classroom'])[0]
                n=int(q.get('n',[240])[0])
                if not 2<=n<=MAX_FILES: raise ValueError('Choose between 2 and 6,000 files')
                if dataset=='classroom' and n>1200: raise ValueError('Classroom datasets support up to 1,200 files')
                if dataset not in ('real','classroom','sms','contracts'): raise ValueError('Unknown dataset')
                if u.path=='/api/dataset-info':
                    meta=(json.loads((CONTRACT_DATA/'manifest.json').read_text()) if dataset=='contracts' else json.loads((SMS_DATA/'manifest.json').read_text(encoding='utf-8')) if dataset=='sms' else real_manifest() if dataset=='real' else {'title':'Synthetic classroom documents'})
                    return self.send({k:v for k,v in meta.items() if k!='files'})
                if u.path=='/api/sample': return self.send(collection_documents(dataset,n))
                return self.send(collection_zip(dataset,n),'application/zip',filename=f'{"contract-clauses" if dataset=="contracts" else "sms-messages" if dataset=="sms" else "20newsgroups" if dataset=="real" else "classroom"}-{n}-files.zip')
            except (ValueError, OSError) as e:
                return self.send({'error':str(e)},status=400)
        if u.path.startswith('/api/job/'):
            job=JOBS.get(u.path.rsplit('/',1)[1]); return self.send(job or {'error':'Run not found'},status=200 if job else 404)
        if u.path=='/api/contract-example':
            names=['contract_093__anti_assignment__43975_44612.txt','contract_174__anti_assignment__46567_47142.txt']
            manifest=json.loads((CONTRACT_DATA/'manifest.json').read_text())
            by_name={f['name']:f for f in manifest['files']}
            docs=[dict(by_name[n],text=(CONTRACT_DATA/'files'/n).read_bytes().decode('utf-8'))for n in names]
            score=jaccard(shingles(docs[0]['text'],5),shingles(docs[1]['text'],5))
            return self.send({'files':docs,'similarity':score,'k':5})
        if u.path=='/api/contract':
            cid=q.get('id',[''])[0]
            if cid not in {f['contract_id']for f in json.loads((CONTRACT_DATA/'manifest.json').read_text())['files']}: return self.send({'error':'Contract not found'},status=404)
            return self.send((CONTRACT_DATA/'full_contracts'/f'{cid}.txt').read_bytes(),'text/plain; charset=utf-8')
        if u.path=='/api/diff':
            import difflib
            names=[q.get(k,[''])[0]for k in ('a','b')]
            known={f['name']for f in json.loads((CONTRACT_DATA/'manifest.json').read_text())['files']}
            if any(n not in known for n in names):return self.send({'error':'Clause not found'},status=404)
            texts=[(CONTRACT_DATA/'files'/n).read_bytes().decode('utf-8')for n in names]
            tokens=[re.findall(r'\S+\s*',t)for t in texts]
            blocks=[]
            for op,i,j,k,l in difflib.SequenceMatcher(None,*tokens,autojunk=False).get_opcodes():
                blocks.append({'operation':op,'a':''.join(tokens[0][i:j]),'b':''.join(tokens[1][k:l])})
            return self.send(blocks)
        if u.path=='/api/code': return self.send((ROOT/'app.py').read_text(),'text/plain')
        path=ROOT/'static'/('index.html' if u.path=='/' else u.path.lstrip('/'))
        if not path.resolve().is_relative_to(ROOT/'static') or not path.is_file(): return self.send({'error':'Not found'},status=404)
        return self.send(path.read_bytes(),{'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml'}.get(path.suffix,'text/plain'))
    def do_POST(self):
        try:
            length=int(self.headers.get('Content-Length',0))
            if length>12_000_000: raise ValueError('Upload limit is 12 MB per run')
            data=json.loads(self.rfile.read(length))
            if self.path.startswith('/api/cancel/'):
                job=JOBS.get(self.path.rsplit('/',1)[1])
                if job: job['cancel']=True
                return self.send({'ok':True})
            if self.path!='/api/run': return self.send({'error':'Not found'},status=404)
            files=data.get('files',[])
            if not 2<=len(files)<=MAX_FILES: raise ValueError('Choose between 2 and 6,000 text files')
            if any(not isinstance(f.get('text'),str) or not isinstance(f.get('name'),str) for f in files): raise ValueError('Invalid files')
            k=int(data.get('k',5))
            if not 2<=k<=15: raise ValueError('Shingle size must be 2–15')
            short=next((f['name'] for f in files if len(' '.join(f['text'].lower().split()))<k), None)
            if short: raise ValueError(f'{short}: needs at least {k} normalized characters')
            if not 1<=int(data.get('bands',20))<=40 or not 1<=int(data.get('rows',5))<=10: raise ValueError('Invalid band settings')
            if not 0<=float(data.get('threshold',.8))<=1: raise ValueError('Invalid threshold')
            if data.get('mode','both') not in ['both','brute','lsh']: raise ValueError('Invalid method')
            if any(j['status']=='running' for j in JOBS.values()): raise ValueError('A run is already active; wait or cancel it first')
            for key in list(JOBS):
                if JOBS[key]['status']!='running': del JOBS[key]
            key=uuid.uuid4().hex; job={'status':'running','stage':'Preparing','done':0,'total':len(files),'elapsed':0}; JOBS[key]=job
            POOL.submit(run_job,job,data); self.send({'id':key})
        except Exception as e: self.send({'error':str(e)},status=400)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=8000); args=p.parse_args()
    print(f'Similarity Lab running at http://127.0.0.1:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
