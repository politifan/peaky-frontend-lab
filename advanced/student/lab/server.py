"""Учебный FastAPI/SQLAlchemy API. Only synthetic data, bind localhost."""
from pathlib import Path
import os,asyncio,json,hashlib
from fastapi import FastAPI,HTTPException,Query,Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from sqlalchemy import create_engine,String,Integer,Text,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
from sqlalchemy.exc import IntegrityError
BASE=Path(__file__).resolve().parent
DB=Path(os.environ.get('PEAKY_DB',str(BASE/'peaky.sqlite3')))
DB.parent.mkdir(parents=True,exist_ok=True)
engine=create_engine('sqlite:///'+DB.as_posix(),connect_args={'check_same_thread':False})
class Model(DeclarativeBase):pass
class Ticket(Model):
 __tablename__='tickets'
 id:Mapped[int]=mapped_column(primary_key=True)
 title:Mapped[str]=mapped_column(String(120))
 version:Mapped[int]=mapped_column(Integer,default=1)
 column:Mapped[str]=mapped_column(String(20),default='todo')
class Operation(Model):
 __tablename__='operations'
 key:Mapped[str]=mapped_column(String(100),primary_key=True)
 payload:Mapped[str]=mapped_column(Text)
 result:Mapped[str]=mapped_column(Text)
class Booking(Model):
 __tablename__='bookings'
 id:Mapped[int]=mapped_column(primary_key=True)
 room:Mapped[str]=mapped_column(String(20))
 start:Mapped[int]=mapped_column(Integer)
 end:Mapped[int]=mapped_column(Integer)
 total:Mapped[int]=mapped_column(Integer)
Model.metadata.create_all(engine)
with Session(engine) as s:
 if not s.scalar(select(Ticket.id).limit(1)):
  s.add_all([Ticket(title=({199:'a — Alpha',200:'ab — Atlas'}.get(i,'Заявка '+str(i))),column=['todo','doing','done'][i%3]) for i in range(1,201)]);s.commit()
app=FastAPI(title='Peaky Minds Frontend Lab',version='2.0')
class NewTicket(BaseModel):
 key:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
 title:str=Field(min_length=1,max_length=120)
class EditTicket(BaseModel):
 title:str=Field(min_length=1,max_length=120)
 baseVersion:int=Field(ge=1)
class Move(BaseModel):
 key:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
 to:str=Field(pattern=r'^(todo|doing|done)$')
 baseVersion:int=Field(ge=1)
class NewBooking(BaseModel):
 key:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
 room:str=Field(pattern=r'^room-[1-5]$')
 start:int=Field(ge=0,le=10080)
 end:int=Field(ge=1,le=10080)
 unit:int=Field(ge=0,le=100000)
 quantity:int=Field(ge=1,le=20)
 discount:int=Field(ge=0,le=100000)
def ticket(t):return dict(id=str(t.id),title=t.title,version=t.version,column=t.column)
def payload(d):return json.dumps(d,sort_keys=True,ensure_ascii=False)
def replay(s,key,body):
 op=s.get(Operation,key)
 if op:
  if op.payload!=body:raise HTTPException(409,'key payload conflict')
  return json.loads(op.result)
 return None
def persist(s,key,body,result):s.add(Operation(key=key,payload=body,result=payload(result)));s.commit();return result
@app.get('/api/health')
def health():return {'ok':True,'version':2,'database':'SQLite учебный стенд'}
@app.get('/api/tickets')
async def tickets(q:str='',delay:int=Query(0,ge=0,le=1000),fail:bool=False):
 if delay:await asyncio.sleep(delay/1000)
 if fail:raise HTTPException(503,'temporary exercise failure')
 with Session(engine) as s:return [ticket(t) for t in s.scalars(select(Ticket).order_by(Ticket.id)) if q.lower() in t.title.lower()]
@app.post('/api/tickets',status_code=201)
def create(d:NewTicket):
 title=d.title.strip()
 if not title:raise HTTPException(422,'empty title')
 body=payload(dict(title=title))
 with Session(engine) as s:
  old=replay(s,d.key,body)
  if old:return old
  t=Ticket(title=title);s.add(t)
  try:
   s.flush();r=ticket(t);return persist(s,d.key,body,r)
  except IntegrityError:
   s.rollback();r=replay(s,d.key,body)
   if r:return r
   raise HTTPException(409,'concurrent conflict')
@app.patch('/api/tickets/{ident}')
def edit(ident:int,d:EditTicket):
 with Session(engine) as s:
  # Atomic conditional update avoids read-check-write race.
  from sqlalchemy import update
  title=d.title.strip()
  if not title:raise HTTPException(422,'empty title')
  result=s.execute(update(Ticket).where(Ticket.id==ident,Ticket.version==d.baseVersion).values(title=title,version=Ticket.version+1))
  if result.rowcount!=1:s.rollback();raise HTTPException(409,'version conflict or missing id')
  s.commit();return ticket(s.get(Ticket,ident))
@app.delete('/api/tickets/{ident}')
def delete(ident:int):
 with Session(engine) as s:
  t=s.get(Ticket,ident)
  if not t:raise HTTPException(404,'missing')
  s.delete(t);s.commit();return {'deleted':str(ident)}
@app.post('/api/tickets/{ident}/move')
def move(ident:int,d:Move):
 from sqlalchemy import text
 body=payload(dict(id=ident,to=d.to,baseVersion=d.baseVersion))
 with Session(engine) as s:
  s.execute(text('BEGIN IMMEDIATE'))
  old=replay(s,d.key,body)
  if old:return old
  t=s.get(Ticket,ident)
  if not t:raise HTTPException(404,'missing')
  if t.version!=d.baseVersion:raise HTTPException(409,'version conflict')
  count=len(list(s.scalars(select(Ticket.id).where(Ticket.column==d.to))))
  if d.to=='doing' and t.column!='doing' and count>=70:raise HTTPException(409,'WIP limit 70')
  t.column=d.to;t.version+=1;s.flush();return persist(s,d.key,body,ticket(t))
@app.get('/api/metrics')
def metrics():return [dict(time=i,value=(i*17)%100-20,source='sensor-'+str(i%3)) for i in range(10000)]
@app.get('/api/bookings')
def bookings():
 with Session(engine) as s:return [dict(id=b.id,room=b.room,start=b.start,end=b.end,total=b.total) for b in s.scalars(select(Booking).order_by(Booking.id))]
@app.post('/api/bookings',status_code=201)
def book(d:NewBooking):
 from sqlalchemy import text
 if d.end<=d.start:raise HTTPException(422,'end must exceed start')
 body=payload(d.model_dump(exclude={'key'}))
 with Session(engine) as s:
  s.execute(text('BEGIN IMMEDIATE'))
  old=replay(s,d.key,body)
  if old:return old
  overlap=s.scalar(select(Booking.id).where(Booking.room==d.room,Booking.start<d.end,d.start<Booking.end).limit(1))
  if overlap:raise HTTPException(409,'booking conflict')
  b=Booking(room=d.room,start=d.start,end=d.end,total=max(0,d.unit*d.quantity-d.discount));s.add(b);s.flush()
  r=dict(id=b.id,room=b.room,start=b.start,end=b.end,total=b.total);return persist(s,d.key,body,r)
@app.get('/api/docs')
def docs():return dict(version=2,docs=[dict(id='doc-'+str(i),title='Заметка '+str(i),category='Раздел '+str(i%5+1),tags=['react','ui' if i%2 else 'api'],text='Учебная заметка '+str(i)+'. Сначала определите контракт действия. Сохраните исходные данные. Выполните изменение и повторите пользовательскую проверку. Документ содержит собственный демонстрационный текст, без личных данных.') for i in range(1,31)])
if (BASE/'dist/assets').exists():app.mount('/assets',StaticFiles(directory=BASE/'dist/assets'),name='assets')
@app.get('/{path:path}')
def ui(path:str):
 if path.startswith('api/'):raise HTTPException(404,'unknown API')
 if not (BASE/'dist/index.html').exists():raise HTTPException(503,'Run npm ci and npm run build first')
 return FileResponse(BASE/'dist/index.html',headers={'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"})
