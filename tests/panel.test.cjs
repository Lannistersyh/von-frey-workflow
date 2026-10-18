const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

const html = fs.readFileSync(path.join(__dirname, '../app/von_frey_entry.html'), 'utf8');
const uncommented = html.replace(/<!--[\s\S]*?-->/g, '');
const scripts = [...uncommented.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(match => match[1]);
function panel() {
  const context = vm.createContext({console, document: {readyState: 'loading', addEventListener() {}},
    setTimeout, clearTimeout, Blob, URL});
  for (const script of scripts) vm.runInContext(script, context);
  vm.runInContext('state = defaultState()', context);
  return context;
}
const value = (context, code) => JSON.parse(JSON.stringify(vm.runInContext(code, context)));

test('panel JavaScript loads and uses an isolated empty draft', () => {
  const context = panel();
  assert.equal(value(context, 'state.subjects.length'), 0);
  assert.equal(value(context, 'IDB_NAME'), 'vonfrey-public-workflow');
  assert.match(value(context, 'LS_KEY'), /^vonfrey-public-workflow::/);
});

test('actual final force differs from start and next force', () => {
  const context = panel();
  assert.deepEqual(value(context, 'forceTrace("OOXOXO", .16, SCHEMA.KIT.standard.fibers)'),
    [.16, .4, .6, .4, .6, .4]);
  assert.equal(value(context, 'finalForceOf("OOXOXO", .16, SCHEMA.KIT.standard.fibers)'), .4);
  assert.equal(value(context, 'traceClamped("XXXXXX", .16, SCHEMA.KIT.standard.fibers)'), true);
});

test('synthetic demo contains only synthetic IDs and clears imported study results', () => {
  const context = panel();
  vm.runInContext('save = () => {}; renderAll = () => {}; renderAudit = () => {}; state.webImports = {old: 1}; loadDemo()', context);
  assert.deepEqual(value(context, 'state.subjects.map(s => s.id)'),
    ['DEMO-001', 'DEMO-002', 'DEMO-003', 'DEMO-004']);
  assert.equal(value(context, 'state.meta.protocol'), 'SYNTHETIC-DEMO');
  assert.deepEqual(value(context, 'state.webImports'), {});
  assert.equal(value(context, 'state.webArchive'), null);
  assert.match(html, /载入模拟 demo/);
});

test('retains boundary observation metadata', () => {
  const context = panel();
  const result = value(context, 'boundaryOutcome("XXXXXX", .16, SCHEMA.KIT.standard.fibers)');
  assert.equal(result.kind, 'min');
  assert.equal(result.value, .07);
});

test('local panel contains no automatic network transport or remote scripts', () => {
  assert.equal(/<script[^>]+src\s*=/i.test(html), false);
  const code = scripts.join('\n');
  assert.equal(/\bfetch\s*\(|XMLHttpRequest|sendBeacon\s*\(|new\s+WebSocket\s*\(/.test(code), false);
});
