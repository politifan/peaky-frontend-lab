import React, {useReducer, useState} from 'react';
import {solve} from './practice/selector.js';
import {editorReducer} from './practice/editorReducer.js';
function counter(state,event){
  if(event.type==='add')return {...state,count:state.count+1};
  return state;
}
export default function StatePractice(){
  const [items,setItems]=useState([{id:'a',title:''},{id:'b',title:'Лекторий'}]);
  const [selectedId,setSelectedId]=useState('a');
  const [count,dispatchCount]=useReducer(counter,{count:0});
  const [editor,dispatch]=useReducer(editorReducer,{saved:'Исходный текст',draft:'Исходный текст'});
  const selectedTitle=solve({items,selectedId});
  return <main className="panel" style={{maxWidth:800,margin:'24px auto'}}>
    <h1>Из функции в компонент</h1><p>Маленький счётчик уже работает. Селектор и редактор — ваша реализация в src/practice. Две задачи проверяют разные переходы состояния.</p>
    <section><h2>Разобранный reducer</h2><button onClick={()=>dispatchCount({type:'add'})}>Добавить один</button><output aria-live="polite">Счётчик: {count.count}</output></section>
    <section><h2>Селектор собственной функции</h2>
      <button onClick={()=>setSelectedId('a')}>Выбрать пустую подпись</button><button onClick={()=>setSelectedId('b')}>Выбрать лекторий</button>
      <p role="status" data-testid="selection">{selectedTitle===null?'Не выбрано':selectedTitle===''?'(пустая подпись)':selectedTitle}</p>
      <button onClick={()=>setItems(rows=>rows.map(row=>row.id===selectedId?{...row,title:row.title+' — изменено'}:row))}>Изменить выбранную запись</button>
      <button onClick={()=>setItems(rows=>rows.filter(row=>row.id!==selectedId))}>Удалить выбранную запись</button>
      <p>После изменения исходной записи подпись обновляется. После удаления — «Не выбрано». Пустая строка сохраняет отдельный смысл.</p>
    </section>
    <section><h2>Собственный reducer редактора</h2><label htmlFor="practice-draft">Черновик</label>
      <input id="practice-draft" value={editor.draft} onChange={e=>dispatch({type:'edit',value:e.target.value})}/>
      <button onClick={()=>dispatch({type:'save'})}>Сохранить черновик</button><button onClick={()=>dispatch({type:'cancel'})}>Отменить изменения</button>
      <p>Сохранено: <output data-testid="saved">{editor.saved}</output></p>
      <p>edit меняет только draft, save копирует draft в saved, cancel возвращает draft к saved. Неподдержанное событие сохраняет state.</p>
    </section>
    <p><a href="/">Вернуться в диспетчерскую</a></p>
  </main>;
}
