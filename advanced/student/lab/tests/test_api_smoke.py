"""Public functional smoke. Start the learner API first on PEAKY_URL."""
import os,uuid,httpx
BASE=os.environ.get('PEAKY_URL','http://127.0.0.1:8000')
def test_one_effect_after_repeat():
 key='public-'+uuid.uuid4().hex;title='Учебная проверка '+key
 with httpx.Client(base_url=BASE) as c:
  a=c.post('/api/tickets',json={'key':key,'title':title})
  b=c.post('/api/tickets',json={'key':key,'title':title})
  assert a.status_code==b.status_code==201
  assert a.json()['id']==b.json()['id']
  assert len([x for x in c.get('/api/tickets').json() if x['title']==title])==1
  assert c.post('/api/tickets',json={'key':key,'title':'Иное содержимое'}).status_code==409
def test_client_route_and_api_error_differ():
 with httpx.Client(base_url=BASE) as c:
  assert c.get('/tickets/demo').status_code==200
  assert c.get('/api/unknown').status_code==404
