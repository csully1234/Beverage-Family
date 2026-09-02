const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {JSDOM, VirtualConsole} = require('jsdom');
const {connectionOverlaps, matchingLinks} = require('../static/historical_map.js');
const root = path.resolve(__dirname, '..');
const render = `from pathlib import Path
from archive import ArchiveIndex
from family_data import load_site_data
from historical_map import build_historical_map_html
print(build_historical_map_html(ArchiveIndex(load_site_data(Path('data')))))`;
const html = execFileSync(process.env.PYTHON || 'python', ['-c', render], {cwd:root, encoding:'utf8'});
const data = JSON.parse(html.match(/<script id="archive-data" type="application\/json">(.*?)<\/script>/s)[1]);
const all = {person:'',event:'',category:'',start:1700,end:2100,undated:true};
function setup(documentHTML=html) {
  const errors=[];
  const console = new VirtualConsole();
  console.on('jsdomError', error => errors.push(error.message));
  // No network resources are enabled: exercises the offline marker/list path.
  const dom = new JSDOM(documentHTML, {url:'https://family.example/?page=map', referrer:'https://family.example/?page=map',
    runScripts:'dangerously', pretendToBeVisual:true, virtualConsole:console,
    beforeParse(window) {
      Object.defineProperty(window.HTMLElement.prototype,'clientWidth',{get(){return 800;}});
      Object.defineProperty(window.HTMLElement.prototype,'clientHeight',{get(){return 460;}});
    }});
  assert.deepEqual(errors,[]);
  return dom;
}
function change(dom,id,value) {
  const input=dom.window.document.getElementById(id);
  if (typeof value==='boolean') input.checked=value; else input.value=value;
  input.dispatchEvent(new dom.window.Event('change',{bubbles:true}));
}
function text(dom,id){return dom.window.document.getElementById(id).textContent;}

test('inclusive year filtering covers tenure, point dates, and explicit unknowns', () => {
  const link={date_from:'1790',date_to:'1798'};
  assert.equal(connectionOverlaps(link,1798,1798,false),true);
  assert.equal(connectionOverlaps(link,1799,1799,false),false);
  assert.equal(connectionOverlaps({date_from:null,date_to:null},1900,2000,false),false);
  assert.equal(connectionOverlaps({date_from:null,date_to:'1798'},1794,1795,false),true);
  assert.equal(connectionOverlaps({date_from:'1798',date_to:null},1800,1850,false),true);
});
test('person selection includes documented events but never invents presence in petition towns',()=>{
  const links=matchingLinks(data,{...all,person:'john_white_beverage_1774'});
  assert.deepEqual([...new Set(links.map(l=>l.place_id))],['vinalhaven_me']);
  assert(links.some(l=>l.subject_id==='event_john_hancock_courts_memorial_1808'));
});
test('event selection includes multiple places without fabricating people-place links',()=>{
  const links=matchingLinks(data,{...all,event:'event_john_hancock_courts_memorial_1808'});
  assert.equal(new Set(links.map(l=>l.place_id)).size,3);
  assert(!links.some(l=>l.subject_type==='person' && l.place_id==='castine_me'));
});
test('Leaflet initializes and every seeded place has a keyboard-accessible list entry',()=>{
  const dom=setup();const doc=dom.window.document;
  assert.equal(doc.querySelectorAll('#place-list button').length,21);
  assert.equal(doc.querySelectorAll('.leaflet-marker-icon').length,21);
  assert.match(text(dom,'status'),/21 places/);
  assert(doc.querySelector('.leaflet-control-attribution').textContent.includes('OpenStreetMap'));
  dom.window.close();
});
test('clicking a place exposes real people, events, evidence and valid application links',()=>{
  const dom=setup();const doc=dom.window.document;
  doc.querySelector('button[data-place="pulpit_harbor_me"]').click();
  assert.match(text(dom,'detail'),/James Beverage/);
  assert.match(text(dom,'detail'),/Josiah/);
  assert.match(text(dom,'detail'),/1848/);
  assert.match(text(dom,'detail'),/Evidence:/);
  assert.equal(doc.querySelector('button[data-place="pulpit_harbor_me"]').getAttribute('aria-pressed'),'true');
  for(const link of doc.querySelectorAll('#detail a')) {
    assert.equal(new URL(link.href).origin,'https://family.example');
    assert.equal(link.target,'_blank');
  }
  dom.window.close();
});
test('marker click and keyboard-compatible list selection use the same detail',()=>{
  const dom=setup();const doc=dom.window.document;
  doc.querySelector('.leaflet-marker-icon[title="Pulpit Harbor"]').click();
  assert.match(text(dom,'detail'),/Pulpit Harbor/);
  dom.window.close();
});
test('person filters, event jumps, category filters, and reset work together',()=>{
  const dom=setup();const doc=dom.window.document;
  change(dom,'person','harold_h_beverage_1893');
  assert.equal(doc.querySelectorAll('#place-list button').length,2);
  assert.match(text(dom,'status'),/Harold/);
  change(dom,'category','engineering');
  assert.equal(doc.querySelectorAll('#place-list button').length,1);
  change(dom,'event','event_john_hancock_courts_memorial_1808');
  assert.equal(doc.getElementById('person').value,'');
  assert.equal(doc.getElementById('category').value,'');
  assert.equal(doc.querySelectorAll('#place-list button').length,3);
  doc.getElementById('reset').click();
  assert.equal(doc.querySelectorAll('#place-list button').length,21);
  dom.window.close();
});
test('empty results, reversed dates, and undated exclusions are understandable',()=>{
  const dom=setup();const doc=dom.window.document;
  change(dom,'from','1794');change(dom,'to','1794');change(dom,'undated',false);
  assert.match(text(dom,'status'),/1 places/);
  doc.querySelector('button[data-place="vinalhaven_me"]').click();
  assert.match(text(dom,'detail'),/Thomas/);
  change(dom,'from','2100');
  assert.match(text(dom,'status'),/valid year range/);
  change(dom,'to','2101');
  assert.match(text(dom,'detail'),/No matching places/);
  dom.window.close();
});
test('direct event route initializes its places and detail',()=>{
  const initial={...data,initial:{person:'',event:'event_north_haven_bridge_act_1848',place:''}};
  const input=html.replace(/(<script id="archive-data" type="application\/json">).*?(<\/script>)/s,(_,a,b)=>a+JSON.stringify(initial).replaceAll('<','\\u003c')+b);
  const dom=setup(input);
  assert.match(text(dom,'status'),/1 places/);
  assert.match(text(dom,'detail'),/Pulpit Harbor/);
  dom.window.close();
});
test('HTML-like place text cannot execute as markup',()=>{
  const poisoned=structuredClone(data);
  poisoned.places[0].name='<img src=x onerror="window.pwned=true">';
  const input=html.replace(/(<script id="archive-data" type="application\/json">).*?(<\/script>)/s,(_,a,b)=>a+JSON.stringify(poisoned).replaceAll('<','\\u003c')+b);
  const dom=setup(input);
  dom.window.document.querySelector('button[data-place="north_haven_me"]').click();
  assert.equal(dom.window.document.querySelectorAll('#detail img').length,0);
  assert.equal(dom.window.pwned,undefined);
  dom.window.close();
});
test('map asset failure leaves the place list, filters, and evidence working',()=>{
  const noLeaflet=html.replace(/<script>\/\* @preserve[\s\S]*?<\/script>/,'<script></script>');
  const dom=setup(noLeaflet);
  assert.equal(dom.window.L,undefined);
  assert.equal(dom.window.document.querySelectorAll('#place-list button').length,21);
  assert.match(text(dom,'map-warning'),/could not start/);
  dom.window.close();
});
test('tile errors are visible without removing the records',()=>{
  const dom=setup();
  const image=dom.window.document.querySelector('.leaflet-tile');
  assert(image);
  image.dispatchEvent(new dom.window.Event('error'));
  assert.match(text(dom,'map-warning'),/background map could not load/);
  assert.equal(dom.window.document.querySelectorAll('#place-list button').length,21);
  dom.window.close();
});
