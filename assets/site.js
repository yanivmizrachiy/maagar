const G = { '7': 'כיתה ז׳', '8': 'כיתה ח׳', '9': 'כיתה ט׳', 'high-school': 'חטיבה עליונה', unknown: 'לא ידוע' };
const C = { algebra: 'אלגברה', geometry: 'גיאומטריה', summaries: 'מסכמות', exams: 'מבחנים', uncategorized: 'שונות', unknown: 'לא מסווג' };
const T = { worksheet: 'דף עבודה', 'summary-work': 'סיכום/עבודה', exam: 'מבחן', link: 'קישור', 'digital-task': 'דיגיטלי', 'printable-task': 'להדפסה', 'embedded-resource': 'מוטמע', mixed: 'מעורב', unknown: 'לא ידוע' };
const I = { pdf: '📕', doc: '📘', docx: '📘', ppt: '📙', pptx: '📙', xls: '📗', xlsx: '📗' };
const GO = { '7': 10, '8': 20, '9': 30, 'high-school': 40, unknown: 99 };
const CO = { algebra: 10, geometry: 20, summaries: 30, exams: 40, uncategorized: 90, unknown: 99 };
const TO = { worksheet: 10, 'summary-work': 20, exam: 30, 'digital-task': 40, 'printable-task': 50, 'embedded-resource': 60, link: 70, mixed: 80, unknown: 99 };
const EO = { pdf: 10, doc: 20, docx: 21, ppt: 30, pptx: 31, xls: 40, xlsx: 41 };

let S = { files: [], q: '', g: 'all', c: 'all', t: 'all' };

const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const he = (a, b) => String(a || '').localeCompare(String(b || ''), 'he', { numeric: true, sensitivity: 'base' });
const rank = (map, value) => Object.prototype.hasOwnProperty.call(map, value) ? map[value] : 95;

function title(f) { return f.display_title_clean || f.title || f.file_name || 'קובץ ללא שם'; }
function topics(f) { return Array.isArray(f.topics) ? f.topics.filter(t => t && t !== 'unknown') : []; }
function mainTopic(f) { return topics(f)[0] || 'ללא נושא מסווג'; }
function gradeKey(f) { return f.grade || 'unknown'; }
function categoryKey(f) { return f.primary_category || 'unknown'; }
function typeKey(f) { return f.document_type || 'unknown'; }
function gradeLabel(f) { return G[gradeKey(f)] || gradeKey(f); }
function categoryLabel(f) { return C[categoryKey(f)] || categoryKey(f); }
function typeLabel(f) { return T[typeKey(f)] || typeKey(f); }
function ext(f) {
  const e = String(f.extension || '').replace(/^\./, '').toLowerCase();
  if (e) return e;
  const m = String(f.file_name || f.path || '').toLowerCase().match(/\.([a-z0-9]+)$/);
  return m ? m[1] : '';
}
function repo(f) { return f.source_type === 'repo-file' && !!f.path; }
function url(f) { return repo(f) ? `./${f.path}` : (f.source_url || ''); }
function abs(u) { try { return new URL(u, location.href).href; } catch { return u; } }
function viewUrl(f) {
  const u = url(f);
  const e = ext(f);
  if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(e) && location.protocol.startsWith('http')) {
    return 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(abs(u));
  }
  return u;
}
function count(n) { return n === 1 ? 'קובץ אחד' : n + ' קבצים'; }
function downloadable(f) { return repo(f) && !!f.path && f.download_ready !== false; }
function downloadName(f) { return f.file_name || `${f.id || 'maagar-file'}.${ext(f) || 'pdf'}`; }
function downloadUrl(f) { return downloadable(f) ? url(f) : ''; }
function downloadButton(f) {
  if (!downloadable(f)) return '';
  return `<a class="act down fast-download" href="${esc(downloadUrl(f))}" download="${esc(downloadName(f))}" data-download="${esc(f.id)}" title="הורדה ישירה ומהירה של הקובץ">⬇ הורדה מהירה</a>`;
}
function yearValue(f) {
  const y = Number(String(f.year || '').replace(/[^0-9]/g, ''));
  return Number.isFinite(y) && y > 0 ? y : 9999;
}
function groupLabel(f) { return `${gradeLabel(f)} · ${categoryLabel(f)} · ${mainTopic(f)}`; }
function groupRank(label) {
  const sample = S.files.find(f => groupLabel(f) === label) || {};
  return [rank(GO, gradeKey(sample)), rank(CO, categoryKey(sample)), mainTopic(sample)];
}
function compareFiles(a, b) {
  return rank(GO, gradeKey(a)) - rank(GO, gradeKey(b)) ||
    rank(CO, categoryKey(a)) - rank(CO, categoryKey(b)) ||
    he(mainTopic(a), mainTopic(b)) ||
    rank(TO, typeKey(a)) - rank(TO, typeKey(b)) ||
    yearValue(a) - yearValue(b) ||
    rank(EO, ext(a)) - rank(EO, ext(b)) ||
    he(title(a), title(b));
}
function compareGroups(a, b) {
  const ar = groupRank(a);
  const br = groupRank(b);
  return ar[0] - br[0] || ar[1] - br[1] || he(ar[2], br[2]) || he(a, b);
}

async function init() {
  try {
    const r = await fetch('metadata/index.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('metadata ' + r.status);
    const d = await r.json();
    S.files = Array.isArray(d.files) ? d.files : [];
    bind();
    render();
  } catch (e) {
    $('app').innerHTML = '<div class="empty">שגיאה בטעינת metadata/index.json<br>' + esc(e.message) + '</div>';
  }
}

function bind() {
  $('q').oninput = e => { S.q = e.target.value; render(); };
  $('clear').onclick = () => { S.q = ''; S.g = 'all'; S.c = 'all'; S.t = 'all'; $('q').value = ''; render(); };
  $('x').onclick = close;
  $('modal').onclick = e => { if (e.target.id === 'modal') close(); };
  document.onkeydown = e => { if (e.key === 'Escape') close(); };
}

function render() { stats(); filters(); files(); }

function stats() {
  const total = S.files.length;
  const rep = S.files.filter(repo).length;
  const downloads = S.files.filter(downloadable).length;
  const tops = new Set(S.files.flatMap(topics)).size;
  $('stats').innerHTML = [[total, 'קבצים'], [rep, 'לצפייה'], [downloads, 'להורדה'], [tops, 'נושאים']]
    .map(x => `<div class="stat box"><b>${x[0]}</b><div class="sub">${x[1]}</div></div>`).join('');
}

function vals(field) { return [...new Set(S.files.map(f => f[field]).filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b), 'he')); }
function chip(key, val, label, on) { return `<button class="chip ${on ? 'on' : ''}" data-k="${key}" data-v="${esc(val)}">${esc(label)}</button>`; }
function filters() {
  const g = ['all', ...vals('grade')].sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : rank(GO, a) - rank(GO, b) || he(a, b)));
  const c = ['all', ...vals('primary_category')].sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : rank(CO, a) - rank(CO, b) || he(a, b)));
  const t = ['all', ...vals('document_type')].sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : rank(TO, a) - rank(TO, b) || he(a, b)));
  $('filters').innerHTML = '<div class="chips">' + g.map(v => chip('g', v, v === 'all' ? 'כל השכבות' : G[v] || v, S.g === v)).join('') + '</div>' +
    '<div class="chips">' + c.map(v => chip('c', v, v === 'all' ? 'כל התחומים' : C[v] || v, S.c === v)).join('') + '</div>' +
    '<div class="chips">' + t.map(v => chip('t', v, v === 'all' ? 'כל הסוגים' : T[v] || v, S.t === v)).join('') + '</div>';
  document.querySelectorAll('[data-k]').forEach(b => b.onclick = () => { S[b.dataset.k] = b.dataset.v; render(); });
}

function filtered() {
  const q = S.q.trim().toLowerCase();
  return S.files.filter(f => {
    if (S.g !== 'all') {
      const gs = Array.isArray(f.grades) ? f.grades : [];
      if (f.grade !== S.g && !gs.includes(S.g)) return false;
    }
    if (S.c !== 'all' && f.primary_category !== S.c) return false;
    if (S.t !== 'all' && f.document_type !== S.t) return false;
    if (!q) return true;
    const hay = [title(f), f.file_name, f.path, f.author, f.year, f.primary_category, f.document_type, gradeLabel(f), categoryLabel(f), typeLabel(f), ...(f.tags || []), ...topics(f)].join(' ').toLowerCase();
    return hay.includes(q);
  });
}

function files() {
  const arr = filtered().sort(compareFiles);
  $('ttl').textContent = S.q ? 'תוצאות חיפוש מסודרות' : 'קבצים במאגר';
  $('meta').textContent = `${count(arr.length)} · מיון: שכבה › תחום › נושא`;
  if (!arr.length) {
    $('app').className = '';
    $('app').innerHTML = '<div class="empty">לא נמצאו קבצים</div>';
    return;
  }
  const groups = new Map();
  arr.forEach(f => { const k = groupLabel(f); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(f); });
  $('app').className = 'groups';
  $('app').innerHTML = [...groups].sort(([a], [b]) => compareGroups(a, b)).map(([k, items]) => `<section class="group"><div class="ghead"><span>${esc(k)}</span><span>${count(items.length)}</span></div><div class="grid">${items.map(card).join('')}</div></section>`).join('');
  document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => open(b.dataset.view));
}

function card(f) {
  const u = url(f);
  const e = ext(f);
  const labels = [gradeLabel(f), categoryLabel(f), typeLabel(f), e ? '.' + e : ''].filter(Boolean);
  const ts = topics(f).slice(0, 4);
  const isRepo = repo(f);
  const viewAction = isRepo
    ? `<button class="act view" data-view="${esc(f.id)}">👁 צפייה מוטמעת</button>`
    : `<a class="act view" href="${esc(u)}" target="_blank">↗ פתח קישור</a>`;
  const openAction = u ? `<a class="act" href="${esc(u)}" target="_blank">↗ פתח</a>` : '';
  const dlAction = downloadButton(f);
  return `<article class="file"><div class="body"><div class="ft"><div class="ico">${I[e] || '📄'}</div><div class="title">${esc(title(f))}</div></div><div class="tags">${labels.map(x => `<span class="tag">${esc(x)}</span>`).join('')}</div>${ts.length ? `<div class="tags">${ts.map(x => `<span class="tag topic">${esc(x)}</span>`).join('')}</div>` : ''}<div class="meta">${isRepo ? '📁 קובץ פנימי · הורדה ישירה' : '🔗 קישור חיצוני'} ${f.year && f.year !== 'unknown' ? ' · ' + esc(f.year) : ''}</div></div><div class="acts">${viewAction}${openAction}${dlAction}</div></article>`;
}

function open(id) {
  const f = S.files.find(x => x.id === id);
  if (!f) return;
  const u = url(f);
  const canDownload = downloadable(f);
  $('mt').textContent = title(f);
  $('ms').textContent = canDownload ? `${groupLabel(f)} · הורדה ישירה זמינה` : groupLabel(f);
  $('mo').href = u;
  $('mo').target = '_blank';
  $('mo').rel = 'noopener noreferrer';
  if (canDownload) {
    $('md').href = downloadUrl(f);
    $('md').download = downloadName(f);
    $('md').textContent = '⬇ הורדה מהירה';
    $('md').title = 'הורדה ישירה ומהירה של הקובץ';
    $('md').classList.remove('disabled');
    $('md').removeAttribute('aria-disabled');
  } else {
    $('md').removeAttribute('href');
    $('md').removeAttribute('download');
    $('md').textContent = 'אין הורדה ישירה';
    $('md').title = 'אין קישור הורדה ישיר לקובץ זה';
    $('md').classList.add('disabled');
    $('md').setAttribute('aria-disabled', 'true');
  }
  $('viewer').src = 'about:blank';
  $('viewer').title = 'תצוגה מוטמעת: ' + title(f);
  $('viewer').setAttribute('loading', 'eager');
  $('modal').style.display = 'block';
  document.body.style.overflow = 'hidden';
  setTimeout(() => { $('viewer').src = viewUrl(f); }, 50);
}

function close() {
  $('modal').style.display = 'none';
  $('viewer').src = 'about:blank';
  document.body.style.overflow = '';
}

init();
