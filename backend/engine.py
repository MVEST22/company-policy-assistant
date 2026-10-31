import csv, os, re, time, math
from pathlib import Path
from collections import Counter
import requests

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / 'data/company_policies.csv').open(encoding='utf-8-sig', newline='') as f:
    POLICIES = list(csv.DictReader(f))
OLLAMA = os.getenv('OLLAMA_URL', 'http://localhost:11434')
MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
EMBED_MODEL = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
STOP = set('a an the is are was were do does can i we you for to of and or in on at with what how much long many policy company employees employee our about please tell me'.split())

def words(text):
    return [x for x in re.findall(r"[a-z0-9]+", text.lower()) if x not in STOP]

def search(query, k=3):
    q = Counter(words(query))
    scored = []
    for p in POLICIES:
        title = Counter(words(p['title']))
        body = Counter(words(p['policy_text']+' '+p['category']+' '+p['department']))
        score = sum(min(v, title[w]) * 4 + min(v, body[w]) for w, v in q.items())
        if score: scored.append((score,p))
    return [p for _,p in sorted(scored, key=lambda item: -item[0])[:k]]

def ollama_generate(question, policies):
    context = '\n'.join(f"POLICY: {p['title']} | DEPARTMENT: {p['department']} | TEXT: {p['policy_text']}" for p in policies)
    prompt = f'''Answer the user's question ONLY using the policy records below. If the records do not answer it, reply exactly: "The provided policy database does not specify this." Cite the relevant policy title in the answer. Do not invent rules.\n\nRECORDS:\n{context}\n\nQUESTION: {question}\nANSWER:'''
    r = requests.post(OLLAMA+'/api/generate', json={'model':MODEL,'prompt':prompt,'stream':False,'options':{'temperature':0}}, timeout=240)
    r.raise_for_status()
    v=r.json()
    return v.get('response','').strip(), v.get('prompt_eval_count',0)+v.get('eval_count',0)

class Index:
    def __init__(self): self.vectors = None
    def vector(self,text):
        r=requests.post(OLLAMA+'/api/embed',json={'model':EMBED_MODEL,'input':text},timeout=120)
        r.raise_for_status()
        return r.json()['embeddings'][0]
    def retrieve(self,question,k=3):
        if self.vectors is None:
            self.vectors=[self.vector(p['title']+'. '+p['policy_text']) for p in POLICIES]
        q=self.vector(question)
        def cosine(v):
            return sum(a*b for a,b in zip(v,q))/(math.sqrt(sum(a*a for a in v))*math.sqrt(sum(b*b for b in q)) or 1)
        ids=sorted(range(len(POLICIES)),key=lambda i:-cosine(self.vectors[i]))[:k]
        return [POLICIES[i] for i in ids]
INDEX=Index()

def answer(query, method):
    start=time.perf_counter()
    if method=='rules':
        matches=search(query)
        if matches:
            p=matches[0]; response=p['policy_text']; policy=p['title']
        else: response='No matching policy found.'; policy='None'
        tokens=0
    elif method=='llm_no_vector':
        response,tokens=ollama_generate(query,POLICIES)
        matches=[p for p in POLICIES if p['title'].lower() in response.lower()]
        policy=matches[0]['title'] if matches else 'Not identified'
    elif method=='llm_vector':
        matches=INDEX.retrieve(query)
        response,tokens=ollama_generate(query,matches)
        policy=matches[0]['title'] if matches else 'Not identified'
    else: raise ValueError('Unknown method')
    return {'method':method,'answer':response,'policy':policy,'time_ms':round((time.perf_counter()-start)*1000,1),'tokens':tokens,'note':'Unsupported-answer risk must be evaluated manually against source policies; no automatic hallucination detection.'}
