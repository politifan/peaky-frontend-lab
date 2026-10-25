import React,{useState,useEffect,useRef} from 'react';
import {acceptSearch,persistQueue,readCache,closeTop} from './faults.js';
function read(key,fallback) { try {return JSON.parse(localStorage.getItem(key)) ?? fallback;}catch{return fallback;} }
export default function App(){
 const params=new URLSearchParams(location.search),fault=params.get('fault')||'';
 const [query,setQuery]=useState(params.get('q')||''),[items,setItems]=useState([]),[loading,setLoading]=useState(false),[error,setError]=useState('');
 const [selected,setSelected]=useState(null),[title,setTitle]=useState(''),[queue,setQueue]=useState(()=>read('peaky-outbox-v2',[]));
 const [stack,setStack]=useState([]),[notice,setNotice]=useState(''),[draft,setDraft]=useState(()=>read('peaky-draft-v2',''));
 const active=useRef(0),dialog=useRef(null),confirm=useRef(null),opener=useRef(null);
 useEffect(()=>{let live=true;const generation=++active.current;const controller=new AbortController();setLoading(true);setError('');
  fetch('/api/tickets?q='+encodeURIComponent(query)+'&delay='+(query==='a'?350:20),fault==='search'?{}:{signal:controller.signal})
  .then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();})
  .then(data=>{if(live&&(fault!=='search'||acceptSearch(active.current,generation)))setItems(data);})
  .catch(e=>{if(live&&e.name!=='AbortError')setError(e.message);})
  .finally(()=>{if(live&&(fault!=='search'||acceptSearch(active.current,generation)))setLoading(false);});
  return()=>{if(fault!=='search'){live=false;controller.abort();}};
 },[query,fault]);
 useEffect(()=>{localStorage.setItem('peaky-draft-v2',JSON.stringify(draft));},[draft]);
 useEffect(()=>{if(stack.includes('editor')&&!dialog.current.open)dialog.current.showModal();if(!stack.includes('editor')&&dialog.current.open)dialog.current.close();
  if(stack.includes('confirm')&&!confirm.current.open)confirm.current.showModal();if(!stack.includes('confirm')&&confirm.current.open)confirm.current.close();},[stack]);
 function close(){const next=fault==='dialog'?closeTop(stack):stack.slice(0,-1);setStack(next);if(!next.length)requestAnimationFrame(()=>opener.current?.focus());}
 async function send(){
  let current=queue;if(!current.length){current=[{key:crypto.randomUUID(),payload:title.trim()}];setQueue(current);}
  if(fault==='outbox')persistQueue(localStorage,current);else localStorage.setItem('peaky-outbox-v2',JSON.stringify(current));
  const job=current[0];try{const r=await fetch('/api/tickets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:job.key,title:job.payload})});if(!r.ok)throw Error('HTTP '+r.status);const saved=await r.json();setNotice('Сохранено: '+saved.id);setQueue([]);localStorage.setItem('peaky-outbox-v2','[]');setItems(x=>[...x.filter(t=>t.id!==saved.id),saved]);}catch(e){setError(e.message);}
 }
 function loadCache(){const snapshot=read('peaky-cache-v2',{version:1,records:[{id:'stale',title:'Старый формат',version:1}]});setItems(fault==='cache'?readCache(snapshot,2):(snapshot.version===2?snapshot.records:[]));setNotice('Локальный набор прочитан');}
 const current=items.find(x=>x.id===selected)??null;
 return <div className="shell"><aside><p className="brand">PEAKY MINDS</p><h1>Peaky Desk</h1><p>Учебная диспетчерская</p><a href="/">Список заявок</a><p className="muted">Режим неисправности: {fault||'обычный'}</p><p>Исправляйте функции в faults.js по DOCX. Портфолио создаётся в четырёх собственных репозиториях.</p></aside>
 <main><header><div><p className="eyebrow">FRONTEND / LAB 02</p><h2>Рабочая очередь</h2></div><span className="badge">React + FastAPI</span></header>
 <section className="panel"><label htmlFor="search">Поиск заявок</label><input id="search" value={query} onChange={e=>{setQuery(e.target.value);const p=new URLSearchParams(location.search);p.set('q',e.target.value);history.replaceState(null,'','?'+p);}}/><p role="status">{loading?'Загрузка':`${items.length} заявок`}</p><button onClick={loadCache}>Прочитать локальный набор</button></section>
 {error&&<p role="alert" className="error">{error}</p>}<p aria-live="polite">{notice}</p>
 <section className="split"><div className="panel"><h2>Последние заявки</h2><ul className="cards">{items.slice(0,25).map(t=><li key={t.id}><button onClick={e=>{setSelected(t.id);opener.current=e.currentTarget;setStack(['editor']);}}>{t.title}</button><small>#{t.id} · v{t.version}</small></li>)}</ul></div>
 <div className="panel"><h2>Новая заявка</h2><label htmlFor="title">Название</label><input id="title" value={title} onChange={e=>setTitle(e.target.value)}/><button disabled={!title.trim()&&!queue.length} onClick={send}>Отправить</button><p data-testid="queue">В очереди: {queue.length}</p><label htmlFor="draft">Локальный черновик</label><textarea id="draft" value={draft} onChange={e=>setDraft(e.target.value)}/><p className="muted">Черновик хранится отдельно от кэша ответа.</p></div></section>
 <dialog ref={dialog} aria-labelledby="editor-title" onCancel={e=>{e.preventDefault();close();}}><h2 id="editor-title">Редактор заявки</h2><p>{current?.title??'Запись отсутствует'}</p><button onClick={()=>setStack(s=>[...s,'confirm'])}>Подтвердить действие</button><button onClick={close}>Закрыть редактор</button></dialog>
 <dialog ref={confirm} aria-labelledby="confirm-title" onCancel={e=>{e.preventDefault();close();}}><h2 id="confirm-title">Подтверждение</h2><p>Это учебное вложенное окно.</p><button onClick={close}>Отмена</button><button onClick={()=>{setNotice('Действие подтверждено');close();}}>Продолжить</button></dialog>
 </main></div>;
}
