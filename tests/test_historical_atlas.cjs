const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');

const template = fs.readFileSync(path.join(__dirname, '../static/historical_atlas.html'), 'utf8');
const archive = 'https://holmgren.org/NorthHavenHistoricalMaps/';
const maps = [
  {id:'fox-islands',name:'North Haven & Vinalhaven',file:'NorthHaven-Vinalhaven1859.jpg'},
  {id:'north-haven-village',name:'North Haven village',file:'NorthHavenTown1859.jpg'},
  {id:'carvers-harbor',name:"Carver's Harbor, Vinalhaven",file:'CarversHarbor1859.jpg'},
].map(map => ({...map,url:archive+map.file,alt:map.name,description:'Historic residences',note:'Not a deed boundary'}));
const html = template.replace('ATLAS_JSON', JSON.stringify({maps,source:archive,download:archive+'NorthHaven-Vinalhaven1859.zip'}));

function setup() {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(html, {
    url:'https://family.example/?page=map',
    runScripts:'dangerously',
    pretendToBeVisual:true,
    virtualConsole,
    beforeParse(window) {
      Object.defineProperty(window.HTMLElement.prototype, 'clientWidth', {get(){return 800;}});
      Object.defineProperty(window.HTMLElement.prototype, 'clientHeight', {get(){return 500;}});
      Object.defineProperty(window.HTMLImageElement.prototype, 'naturalWidth', {get(){return 3016;}});
      Object.defineProperty(window.HTMLImageElement.prototype, 'naturalHeight', {get(){return 4302;}});
    },
  });
  assert.deepEqual(errors, []);
  const doc = dom.window.document;
  const picture = doc.getElementById('map-image');
  picture.dispatchEvent(new dom.window.Event('load'));
  return dom;
}

test('all original 1859 maps remain selectable with full-resolution source links', () => {
  const dom=setup(), doc=dom.window.document;
  assert.equal(doc.querySelectorAll('#map-choice option').length,3);
  assert.equal(doc.getElementById('map-choice').value,'fox-islands');
  assert(doc.getElementById('open-original').href.endsWith('NorthHaven-Vinalhaven1859.jpg'));
  assert(doc.getElementById('download-all').href.endsWith('.zip'));
  assert.equal(doc.getElementById('zoom-level').textContent,'100%');
  doc.getElementById('map-choice').value = 'north-haven-village';
  doc.getElementById('map-choice').dispatchEvent(new dom.window.Event('change'));
  doc.getElementById('map-image').dispatchEvent(new dom.window.Event('load'));
  assert(doc.getElementById('open-original').href.endsWith('NorthHavenTown1859.jpg'));
  assert.match(doc.getElementById('map-note').textContent,/deed boundary/);
  dom.window.close();
});

test('zoom buttons, fit, drag and keyboard pan work without external image fetches',()=>{
  const dom=setup(), doc=dom.window.document;
  const stage=doc.getElementById('stage'), picture=doc.getElementById('map-image');
  doc.getElementById('zoom-in').click();
  assert.equal(doc.getElementById('zoom-level').textContent,'160%');
  doc.getElementById('zoom-out').click();
  assert.equal(doc.getElementById('zoom-level').textContent,'100%');
  function pointer(type, values) {
    const e=new dom.window.Event(type,{bubbles:true,cancelable:true});
    Object.assign(e,{pointerId:3,button:0,...values});stage.dispatchEvent(e);
  }
  pointer('pointerdown',{clientX:100,clientY:110});
  pointer('pointermove',{clientX:150,clientY:130});
  pointer('pointerup',{clientX:150,clientY:130});
  assert.match(picture.style.transform,/50px,20px/);
  stage.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));
  assert.match(picture.style.transform,/5px,20px/);
  doc.getElementById('fit').click();
  assert.match(picture.style.transform,/0px,0px/);
  assert.equal(doc.getElementById('zoom-level').textContent,'100%');
  dom.window.close();
});

test('missing remote image shows a helpful warning and still offers the original URL',()=>{
  const dom=setup(), doc=dom.window.document;
  doc.getElementById('map-image').dispatchEvent(new dom.window.Event('error'));
  assert.match(doc.getElementById('status').textContent,/could not load/);
  assert.equal(doc.getElementById('status').hidden,false);
  assert(doc.getElementById('open-original').href.startsWith(archive));
  dom.window.close();
});
