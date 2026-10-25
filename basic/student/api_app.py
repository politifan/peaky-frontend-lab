"""Local teaching API. FastAPI and SQLAlchemy. Bind to localhost only."""
from pathlib import Path
import asyncio,os
from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,ConfigDict
from sqlalchemy import create_engine,String,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
ROOT=Path(__file__).resolve().parent
DB=Path(os.environ.get('PM_FRONTEND_DB',str(ROOT/'submissions.sqlite3')))
engine=create_engine('sqlite:///'+str(DB),connect_args={'check_same_thread':False})
class Base(DeclarativeBase):pass
class Submission(Base):
    __tablename__='submissions'
    id:Mapped[int]=mapped_column(primary_key=True)
    text:Mapped[str]=mapped_column(String(2000))
Base.metadata.create_all(engine)
class Message(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    text:str=Field(min_length=1,max_length=2000)
app=FastAPI(title='Peaky Minds local Frontend API')
MODE=os.environ.get('PM_FRONTEND_MODE','ready')
@app.get('/')
def home():return RedirectResponse('/docs')
@app.get('/api/items')
async def items():
    if MODE=='slow':await asyncio.sleep(.8)
    if MODE=='error':return JSONResponse({'detail':'учебный отказ'},status_code=503)
    if MODE=='invalid':return {'wrong':'not-an-array'}
    if MODE=='empty':return []
    return [{'id':'a','name':'Лекторий'},{'id':'b','name':'<b>Буквальная подпись</b>'}]
@app.get('/api/search')
async def search(q:str=''):
    await asyncio.sleep(.35 if len(q)==1 else .02)
    if q=='!':return JSONResponse({'detail':'учебный отказ'},status_code=500)
    return [{'name':q}]
@app.post('/api/send',status_code=201)
async def send(message:Message):
    if not message.text.strip():raise HTTPException(422,'пустой текст')
    if MODE=='slow':await asyncio.sleep(.8)
    if MODE=='error':raise HTTPException(503,'учебный отказ')
    with Session(engine) as s:
        row=Submission(text=message.text);s.add(row);s.commit();s.refresh(row)
        return {'id':row.id,'text':row.text}
@app.get('/api/submissions')
def submissions():
    with Session(engine) as s:return [{'id':x.id,'text':x.text} for x in s.scalars(select(Submission).order_by(Submission.id))]
app.mount('/tasks',StaticFiles(directory=ROOT/'tasks',html=True),name='tasks')
