from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import answer

app = FastAPI(title='Company Policy Assistant')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['POST','GET'], allow_headers=['*'])

class Question(BaseModel):
    question: str

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/compare')
def compare(question: Question):
    if not question.question.strip() or len(question.question)>1000:
        raise HTTPException(400,'Enter a question (up to 1000 characters).')
    result=[]
    for m in ('rules','llm_no_vector','llm_vector'):
        try:
            result.append(answer(question.question,m))
        except Exception as ex:
            result.append({'method':m,'error':str(ex)})
    return {'results':result}
