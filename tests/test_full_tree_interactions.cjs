const assert = require('node:assert/strict');
const test = require('node:test');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.resolve(__dirname, '..');
const render = `from pathlib import Path
from family_data import load_site_data, index_people, relationship_index
from full_tree import build_full_tree_html
data=load_site_data(Path("data"))
print(build_full_tree_html(index_people(data["people"]),relationship_index(data["people"]),initial_person_id="harold_h_beverage_1893"))`;
const html=execFileSync(process.env.PYTHON||'python',['-c',render],{cwd:root,encoding:'utf8',maxBuffer:12*1024*1024});

function setup(){
  const errors=[];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', e=>errors.push(e.message));
  const dom = new JSDOM(html,{
    url:'https://family.example/?page=full-tree',
    referrer:'https://family.example/?page=tree',
    pretendToBeVisual:true,
    runScripts:'dangerously',
    virtualConsole,
    beforeParse(win){
      if(!win.CSS)win.CSS={};
      win.CSS.escape=value=>String(value).replace(/[^a-zA-Z0-9_-]/g,'\\$&');
    }
  });
  return {dom,errors};
}
function change(dom,id,value){
 const el=dom.window.document.getElementById(id);
 el.value=value;
 el.dispatchEvent(new dom.window.Event('change',{bubbles:true}));
}
const wait=()=>new Promise(r=>setTimeout(r,85));

test('focused explorer loads on prior selected person and synchronizes selector',async()=>{
 const {dom,errors}=setup();
 try{
   await wait();
   const d=dom.window.document;
   assert.deepEqual(errors,[]);
   assert.equal(d.getElementById('mode').value,'all');
   assert.equal(d.getElementById('branchDepthControl').hidden,true);
   assert.equal(d.getElementById('personSelect').value,'harold_h_beverage_1893');
   assert.match(d.getElementById('selection').textContent,/Harold/);
   const all=d.querySelectorAll('#world .node').length;
   const visible=d.querySelectorAll('#world .node:not(.is-hidden)').length;
   assert.equal(visible,all,'whole family overview should display every node on arrival');
   change(dom,'mode','branch');
   assert.equal(d.getElementById('branchDepthControl').hidden,false);
   assert.equal(d.getElementById('distance').options[0].textContent,'Immediate family');
   const nearby=d.querySelectorAll('#world .node:not(.is-hidden)').length;
   assert(nearby>1&&nearby<all,`expected nearby people instead of all ${all}, got ${nearby}`);
 }finally{dom.window.close();}
});

test('clicking a relative changes selected person and linked profile',async()=>{
 const {dom,errors}=setup();
 try{
   await wait();
   const d=dom.window.document;
   const candidates=[...d.querySelectorAll('#world .node:not(.is-hidden)')];
   const target=candidates.find(n=>n.dataset.id!=='harold_h_beverage_1893'&&!n.classList.contains('unresolved'));
   assert(target,'expected another known nearby relative');
   target.dispatchEvent(new dom.window.MouseEvent('click',{bubbles:true}));
   assert.equal(d.getElementById('personSelect').value,target.dataset.id);
   assert.equal(d.getElementById('selection').querySelector('a').href,
      'https://family.example/?page=people&profile='+target.dataset.id);
   assert.deepEqual(errors,[]);
 }finally{dom.window.close();}
});

test('steps and full overview show expected nodes without changing selected identity',async()=>{
 const {dom,errors}=setup();
 try{
   await wait();
   const d=dom.window.document;
   const selected=d.getElementById('personSelect').value;
   change(dom,'mode','branch');
   change(dom,'distance','1');
   const one=d.querySelectorAll('#world .node:not(.is-hidden)').length;
   change(dom,'distance','4');
   const four=d.querySelectorAll('#world .node:not(.is-hidden)').length;
   assert(four>=one);
   change(dom,'mode','all');
   assert.equal(d.getElementById('branchDepthControl').hidden,true);
   assert.equal(d.querySelectorAll('#world .node.is-hidden').length,0);
   assert.equal(d.getElementById('personSelect').value,selected);
   change(dom,'mode','branch');
   assert.equal(d.getElementById('personSelect').value,selected);
   assert.deepEqual(errors,[]);
 }finally{dom.window.close();}
});
