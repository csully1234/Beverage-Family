const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');

const html=fs.readFileSync(path.join(__dirname,'../static/tree_component/index.html'),'utf8');
const wait=()=>new Promise(resolve=>setTimeout(resolve,25));

function setup(){
 const errors=[],console=new VirtualConsole();
 console.on('jsdomError',error=>errors.push(error.message));
 const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,
  url:'https://family.example/component/',virtualConsole:console});
 return {dom,errors};
}

test('render message loads graph and keeps subsequent HTML unchanged',async()=>{
 const {dom,errors}=setup();
 try {
  const w=dom.window, iframe=w.document.getElementById('graph');
  const payload={type:'streamlit:render',args:{html:'<!doctype html><title>Family</title>',
   selected_id:'harold_h_beverage_1893',height:830}};
  w.dispatchEvent(new w.MessageEvent('message',{data:payload,source:w.parent}));
  assert.match(iframe.srcdoc,/Family/);
  assert.equal(iframe.style.height,'830px');
  w.dispatchEvent(new w.MessageEvent('message',{data:payload,source:w.parent}));
  assert.match(iframe.srcdoc,/Family/);
  assert.deepEqual(errors,[]);
 } finally {dom.window.close();}
});

test('map click travels through Streamlit component-value protocol',async()=>{
 const {dom,errors}=setup();
 try {
  const w=dom.window, frame=w.document.getElementById('graph'),outputs=[];
  w.addEventListener('message',e=>{if(e.data?.type==='streamlit:setComponentValue') outputs.push(e.data)});
  w.dispatchEvent(new w.MessageEvent('message',{
    data:{type:'beverage:person-selected',person_id:'mary_white_1750'},
    source:frame.contentWindow
  }));
  await wait();
  assert.equal(outputs.length,1);
  assert.equal(outputs[0].value.person_id,'mary_white_1750');
  assert.equal(outputs[0].value.action,'select');
  assert.equal(outputs[0].dataType,'json');
  assert.deepEqual(errors,[]);
 }finally{dom.window.close();}
});

test('Open profile and invalid IDs follow intended navigation/safety rules',async()=>{
 const {dom,errors}=setup();
 try {
  const w=dom.window,frame=w.document.getElementById('graph'),values=[];
  w.addEventListener('message',e=>{if(e.data?.type==='streamlit:setComponentValue') values.push(e.data.value)});
  const event=(type,person_id)=>w.dispatchEvent(new w.MessageEvent('message',{
    data:{type,person_id},source:frame.contentWindow
  }));
  event('beverage:open-profile','mary_white_1750');
  event('beverage:person-selected','../../evil');
  await wait();
  assert.equal(values.length,1);
  assert.deepEqual(values[0],{person_id:'mary_white_1750',action:'profile'});
  assert.deepEqual(errors,[]);
 }finally{dom.window.close();}
});
