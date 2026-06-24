const G = { '7': 'כיתה ז׳', '8': 'כיתה ח׳', '9': 'כיתה ט׳', 'high-school': 'חטיבה עליונה', unknown: 'לא ידוע' };
const C = { algebra: 'אלגברה', geometry: 'גיאומטריה', summaries: 'עבודות סיכום', exams: 'מבחנים', uncategorized: 'שונות', unknown: 'לא מסווג' };
const T = { worksheet: 'דף עבודה', 'summary-work': 'סיכום/עבודה', exam: 'מבחן', link: 'קישור', 'digital-task': 'דיגיטלי', 'printable-task': 'להדפסה', 'embedded-resource': 'מוטמע', mixed: 'מעורב', unknown: 'לא ידוע' };
const U = { '3-unit': '3 יחידות', '4-unit': '4 יחידות', '5-unit': '5 יחידות', unknown: 'לא ידוע' };
const I = { pdf: '📕', doc: '📘', docx: '📘', ppt: '📙', pptx: '📙', xls: '📗', xlsx: '📗' };
const GO = { '7': 10, '8': 20, '9': 30, 'high-school': 40, unknown: 99 };
const CO = { algebra: 10, geometry: 20, summaries: 30, exams: 40, uncategorized: 90, unknown: 99 };
const TO = { worksheet: 10, 'summary-work': 20, exam: 30, 'digital-task': 40, 'printable-task': 50, 'embedded-resource': 60, link: 70, mixed: 80, unknown: 99 };
const UO = { '3-unit': 10, '4-unit': 20, '5-unit': 30, unknown: 99 };
const EO = { pdf: 10, doc: 20, docx: 21, ppt: 30, pptx: 31, xls: 40, xlsx: 41, png: 50, jpg: 51, jpeg: 52 };
const SORTS = { smart: 'מיון חכם', recent: 'חדש → ישן', title: 'לפי שם', type: 'לפי סוג' };
const GRADE_BUTTONS = ['7', '8', '9', 'high-school'];
const UNIT_BUTTONS = [['all', 'כל הרמות'], ['3-unit', '3 יחידות'], ['4-unit', '4 יחידות'], ['5-unit', '5 יחידות']];
const DOMAIN_BUTTONS = [['all', 'כל הקבצים'], ['algebra', 'אלגברה'], ['geometry', 'גיאומטריה'], ['summaries', 'עבודות סיכום'], ['exams', 'מבחנים']];
const EXAM_BUCKETS = { all: 'כל המבחנים', end: 'מבחני סוף שנה', mid: 'מבחני אמצע שנה', start: 'מבחני תחילת שנה', skill: 'מבחני מיומנות' };
const GATEWAY_HINTS = { '7': 'אלגברה, גיאומטריה, עבודות סיכום ומבחנים לכיתה ז׳', '8': 'חומרים מסודרים לפי תחום ונושא לכיתה ח׳', '9': 'הכנה מסודרת, מבחנים וחומרי עומק לכיתה ט׳', 'high-school': 'כניסה לפי יחידות לימוד וחומרים לחטיבה עליונה' };

let S = { files: [], byId: new Map(), q: '', g: 'all', u: 'all', c: 'all', t: 'all', exam: 'all', sort: 'smart' };
let renderTimer = 0;

const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const he = (a, b) => String(a || '').localeCompare(String(b || ''), 'he', { numeric: true, sensitivity: 'base' });
const rank = (map, value) => Object.prototype.hasOwnProperty.call(map, value) ? map[value] : 95;
const safeList = value => Array.isArray(value) ? value : [];

function rawTitle(f) { return f.display_title_clean || f.title || f.file_name || 'קובץ ללא שם'; }
function title(f) { return f._title || rawTitle(f); }
function topics(f) { return f._topics || safeList(f.topics).filter(t => t && t !== 'unknown'); }
function mainTopic(f) { return f._mainTopic || topics(f)[0] || 'ללא נושא מסווג'; }
function gradeKey(f) { return f._grade || f.grade || 'unknown'; }
function categoryKey(f) { return f._category || f.primary_category || 'unknown'; }
function typeKey(f) { return f._type || f.document_type || 'unknown'; }
function unitKey(f) { return f._unit || f.unit_level || 'unknown'; }
function gradeLabel(f) { return f._gradeLabel || G[gradeKey(f)] || gradeKey(f); }
function categoryLabel(f) { return f._categoryLabel || C[categoryKey(f)] || categoryKey(f); }
function typeLabel(f) { return f._typeLabel || T[typeKey(f)] || typeKey(f); }
function unitLabel(f) { return f._unitLabel || U[unitKey(f)] || unitKey(f); }
function ext(f) {
  if (f._ext) return f._ext;
  const e = String(f.extension || '').replace(/^\./, '').toLowerCase();
  if (e) return e;
  const m = String(f.file_name || f.path || '').toLowerCase().match(/\.([a-z0-9]+)$/);
  return m ? m[1] : '';
}
function repo(f) { return f._repo === true || (f.source_type === 'repo-file' && !!f.path); }
function url(f) { return repo(f) ? `./${f.path}` : (f.source_url || ''); }
function abs(u) { try { return new URL(u, location.href).href; } catch { return u; } }
function viewUrl(f) {
  const u = url(f);
  const e = ext(f);
  if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(e) && location.protocol.startsWith('http')) return 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(abs(u));
  return u;
}
function count(n) { return n === 1 ? 'קובץ אחד' : n + ' קבצים'; }
function downloadable(f) { return repo(f) && !!f.path && !!f.file_name && f.download_ready === true; }
function downloadName(f) { return f.file_name || `${f.id || 'maagar-file'}.${ext(f) || 'pdf'}`; }
function downloadUrl(f) { return downloadable(f) ? url(f) : ''; }
function downloadButton(f) {
  if (!downloadable(f)) return '';
  return `<a class="act down fast-download" href="${esc(downloadUrl(f))}" download="${esc(downloadName(f))}" data-download="${esc(f.id)}" title="הורדה ישירה ומהירה של הקובץ">⬇ הורדה מהירה</a>`;
}
function yearValue(f) {
  if (f._yearValue !== undefined) return f._yearValue;
  const y = Number(String(f.year || '').replace(/[^0-9]/g, ''));
  return Number.isFinite(y) && y > 0 ? y : 0;
}
function hasGrade(f, grade) { return grade === 'all' || f.grade === grade || safeList(f.grades).includes(grade); }
function activeGradeKey(f) { return S.g !== 'all' && hasGrade(f, S.g) ? S.g : gradeKey(f); }
function activeGradeLabel(f) { return G[activeGradeKey(f)] || gradeLabel(f); }
function groupLabel(f) {
  if (activeGradeKey(f) === 'high-school') return `${activeGradeLabel(f)} · ${unitLabel(f)} · ${categoryLabel(f)} · ${mainTopic(f)}`;
  return `${activeGradeLabel(f)} · ${categoryLabel(f)} · ${mainTopic(f)}`;
}
function groupKey(f) { return [rank(GO, activeGradeKey(f)), activeGradeKey(f) === 'high-school' ? rank(UO, unitKey(f)) : 0, rank(CO, categoryKey(f)), mainTopic(f)]; }
function compareKey(a, b) {
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (typeof a[i] === 'number' && typeof b[i] === 'number') { const n = a[i] - b[i]; if (n) return n; }
    else { const n = he(a[i], b[i]); if (n) return n; }
  }
  return a.length - b.length;
}
function compareFiles(a, b) {
  if (S.sort === 'recent') return (b._yearValue || 0) - (a._yearValue || 0) || compareKey(a._smartKey, b._smartKey);
  if (S.sort === 'title') return he(title(a), title(b)) || compareKey(a._smartKey, b._smartKey);
  if (S.sort === 'type') return rank(TO, typeKey(a)) - rank(TO, typeKey(b)) || rank(EO, ext(a)) - rank(EO, ext(b)) || compareKey(a._smartKey, b._smartKey);
  return compareKey(groupKey(a), groupKey(b)) || compareKey(a._smartKey, b._smartKey);
}
function compareGroups(a, b) { return compareKey(a.sortKey, b.sortKey); }
function examText(f) { return `${title(f)} ${f.file_name || ''} ${topics(f).join(' ')} ${safeList(f.tags).join(' ')}`.toLowerCase(); }
function isExam(f) { return categoryKey(f) === 'exams' || typeKey(f) === 'exam' || /מבחן|מבחני|בוחן|מיפוי|מיומנות|מחצית/.test(examText(f)); }
function examBucket(f) {
  const text = examText(f);
  if (/מיומנות|מיומנויות|skill/.test(text)) return 'skill';
  if (/סוף|מסכם|סיכום שנה|final|end/.test(text)) return 'end';
  if (/אמצע|מחצית|mid/.test(text)) return 'mid';
  if (/תחילת|תחילה|מיפוי|פתיחה|start|diagnostic/.test(text)) return 'start';
  return 'all';
}
function searchableText(f) { return [title(f), f.file_name, f.path, f.author, f.year, f.unit_level, f.primary_category, f.document_type, gradeLabel(f), unitLabel(f), categoryLabel(f), typeLabel(f), ...(f.tags || []), ...topics(f), isExam(f) ? EXAM_BUCKETS[examBucket(f)] : ''].join(' ').toLowerCase(); }
function enrichFile(file, index) {
  const e = ext(file);
  const ts = safeList(file.topics).filter(t => t && t !== 'unknown');
  const enriched = { ...file };
  enriched._idx = index;
  enriched._title = rawTitle(file);
  enriched._topics = ts;
  enriched._mainTopic = ts[0] || 'ללא נושא מסווג';
  enriched._grade = file.grade || 'unknown';
  enriched._unit = file.unit_level || 'unknown';
  enriched._category = file.primary_category || 'unknown';
  enriched._type = file.document_type || 'unknown';
  enriched._gradeLabel = G[enriched._grade] || enriched._grade;
  enriched._unitLabel = U[enriched._unit] || enriched._unit;
  enriched._categoryLabel = C[enriched._category] || enriched._category;
  enriched._typeLabel = T[enriched._type] || enriched._type;
  enriched._ext = e;
  enriched._repo = file.source_type === 'repo-file' && !!file.path;
  enriched._yearValue = yearValue(file);
  enriched._examBucket = examBucket(enriched);
  enriched._groupKey = [rank(GO, enriched._grade), rank(UO, enriched._unit), rank(CO, enriched._category), enriched._mainTopic];
  enriched._smartKey = [rank(GO, enriched._grade), rank(UO, enriched._unit), rank(CO, enriched._category), enriched._mainTopic, rank(TO, enriched._type), enriched._yearValue || 9999, rank(EO, e), enriched._title, index];
  enriched._search = searchableText(enriched);
  return enriched;
}
function prepareFiles(files) { S.files = files.map(enrichFile); S.byId = new Map(S.files.map(f => [f.id, f])); }
function renderSoon(delay = 80) { clearTimeout(renderTimer); renderTimer = setTimeout(render, delay); }
async function init() {
  try {
    const r = await fetch('metadata/index.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('metadata ' + r.status);
    const d = await r.json();
    prepareFiles(Array.isArray(d.files) ? d.files : []);
    bind();
    render();
  } catch (e) {
    $('app').innerHTML = '<div class="empty">שגיאה בטעינת metadata/index.json<br>' + esc(e.message) + '</div>';
  }
}
function bind() {
  $('q').oninput = e => { S.q = e.target.value; renderSoon(120); };
  $('clear').onclick = () => { S.q = ''; S.g = 'all'; S.u = 'all'; S.c = 'all'; S.t = 'all'; S.exam = 'all'; S.sort = 'smart'; $('q').value = ''; render(); };
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
  $('stats').innerHTML = [[total, 'קבצים'], [rep, 'לצפייה'], [downloads, 'להורדה'], [tops, 'נושאים']].map(x => `<div class="stat box"><b>${x[0]}</b><div class="sub">${x[1]}</div></div>`).join('');
}
function vals(field) { return [...new Set(S.files.map(f => f[field]).filter(Boolean))]; }
function chip(key, val, label, on) { return `<button class="chip ${on ? 'on' : ''}" data-k="${key}" data-v="${esc(val)}">${esc(label)}</button>`; }
function gradeButton(grade) { return `<button class="chip grade-go ${S.g === grade ? 'on' : ''}" data-grade-go="${grade}">מתמטיקה ל${esc(G[grade] || grade)}</button>`; }
function gradeGatewayCard(grade) {
  const total = S.files.filter(f => hasGrade(f, grade)).length;
  const exams = S.files.filter(f => hasGrade(f, grade) && isExam(f)).length;
  const label = grade === 'high-school' ? 'חטיבה עליונה' : `מתמטיקה ל${G[grade] || grade}`;
  return `<button class="grade-entry" data-grade-go="${esc(grade)}"><span class="grade-entry-kicker">כניסה לשכבה</span><strong>${esc(label)}</strong><span>${esc(GATEWAY_HINTS[grade] || 'חומרים מסודרים למורים')}</span><em>${count(total)} · ${exams ? exams + ' מבחנים' : 'מבחנים לפי סינון'}</em></button>`;
}
function gradeGateway(grades) {
  if (S.g !== 'all' || S.q.trim()) return '';
  return `<section class="grade-gateway"><div class="grade-gateway-head"><h2>בחר שכבה להתחלה מהירה</h2><p>שער כניסה יוקרתי ונוח למורים. אחרי בחירת שכבה תראה כפתורים קצרים לפי תחום ומבחנים.</p></div><div class="grade-entry-grid">${grades.map(gradeGatewayCard).join('')}</div></section>`;
}
function domainButton(value, label) { return `<button class="chip domain-chip ${S.c === value || (value === 'all' && S.c === 'all') ? 'on' : ''}" data-domain="${esc(value)}">${esc(label)}</button>`; }
function unitButton(value, label) { return `<button class="chip unit-chip ${S.u === value ? 'on' : ''}" data-unit="${esc(value)}">${esc(label)}</button>`; }
function examButton(value, label) { return `<button class="chip exam-chip ${S.exam === value ? 'on' : ''}" data-exam="${esc(value)}">${esc(label)}</button>`; }
function sortChip(value, label) { return `<button class="chip sort-chip ${S.sort === value ? 'on' : ''}" data-sort="${esc(value)}">${esc(label)}</button>`; }
function highSchoolHub() {
  if (S.g !== 'high-school') return '';
  const units = UNIT_BUTTONS.filter(([value]) => value === 'all' || S.files.some(f => hasGrade(f, 'high-school') && unitKey(f) === value));
  return `<section class="unit-hub"><h2>חטיבה עליונה לפי יחידות</h2><p>בחר רמת לימוד. הסינון נעשה לפי unit_level ב־metadata, בלי לשכפל קבצים.</p><div class="chips unitbar"><span class="sort-title">יחידות:</span>${units.map(([v, label]) => unitButton(v, label)).join('')}</div></section>`;
}
function gradeHub() {
  if (S.g === 'all') return '';
  const domain = '<div class="chips domainbar"><span class="sort-title">' + esc(G[S.g] || 'שכבה') + ':</span>' + DOMAIN_BUTTONS.map(([v, label]) => domainButton(v, label)).join('') + '</div>';
  const exams = (S.c === 'exams' || S.t === 'exam') ? '<div class="chips exambar"><span class="sort-title">מבחנים:</span>' + Object.entries(EXAM_BUCKETS).map(([v, label]) => examButton(v, label)).join('') + '</div>' : '';
  return `<section class="grade-hub"><h2>מתמטיקה ל${esc(G[S.g] || S.g)}</h2><p>בחר תחום. הכפתורים כאן קצרים כי הכותרת כבר מציינת את השכבה.</p>${domain}${exams}</section>`;
}
function filters() {
  const g = GRADE_BUTTONS.filter(grade => S.files.some(f => hasGrade(f, grade)));
  const c = ['all', ...vals('primary_category')].sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : rank(CO, a) - rank(CO, b) || he(a, b)));
  const t = ['all', ...vals('document_type')].sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : rank(TO, a) - rank(TO, b) || he(a, b)));
  $('filters').innerHTML = gradeGateway(g) + '<div class="chips gradebar"><button class="chip ' + (S.g === 'all' ? 'on' : '') + '" data-grade-go="all">כל המאגר</button>' + g.map(gradeButton).join('') + '</div>' + gradeHub() + highSchoolHub() + '<div class="chips">' + c.map(v => chip('c', v, v === 'all' ? 'כל התחומים' : C[v] || v, S.c === v)).join('') + '</div>' + '<div class="chips">' + t.map(v => chip('t', v, v === 'all' ? 'כל הסוגים' : T[v] || v, S.t === v)).join('') + '</div>' + '<div class="chips sortbar"><span class="sort-title">מיון נוח:</span>' + Object.entries(SORTS).map(([value, label]) => sortChip(value, label)).join('') + '</div>';
  document.querySelectorAll('[data-grade-go]').forEach(b => b.onclick = () => { S.g = b.dataset.gradeGo || 'all'; S.u = 'all'; S.c = 'all'; S.t = 'all'; S.exam = 'all'; render(); });
  document.querySelectorAll('[data-unit]').forEach(b => b.onclick = () => { S.u = b.dataset.unit || 'all'; render(); });
  document.querySelectorAll('[data-domain]').forEach(b => b.onclick = () => { S.c = b.dataset.domain || 'all'; S.t = S.c === 'exams' ? 'exam' : 'all'; S.exam = 'all'; render(); });
  document.querySelectorAll('[data-exam]').forEach(b => b.onclick = () => { S.exam = b.dataset.exam || 'all'; render(); });
  document.querySelectorAll('[data-k]').forEach(b => b.onclick = () => { S[b.dataset.k] = b.dataset.v; if (b.dataset.k === 'c' && S.c !== 'exams') S.exam = 'all'; render(); });
  document.querySelectorAll('[data-sort]').forEach(b => b.onclick = () => { S.sort = b.dataset.sort || 'smart'; render(); });
}
function filtered() {
  const q = S.q.trim().toLowerCase();
  return S.files.filter(f => {
    if (!hasGrade(f, S.g)) return false;
    if (S.g === 'high-school' && S.u !== 'all' && unitKey(f) !== S.u) return false;
    if (S.c !== 'all') { if (S.c === 'exams') { if (!isExam(f)) return false; } else if (categoryKey(f) !== S.c) return false; }
    if (S.t !== 'all' && typeKey(f) !== S.t && !(S.t === 'exam' && isExam(f))) return false;
    if (S.exam !== 'all' && examBucket(f) !== S.exam) return false;
    return !q || f._search.includes(q);
  });
}
function files() {
  const arr = filtered().sort(compareFiles);
  const gradeTitle = S.g === 'all' ? 'קבצים במאגר' : `מתמטיקה ל${G[S.g] || S.g}`;
  $('ttl').textContent = S.q ? 'תוצאות חיפוש מסודרות' : gradeTitle;
  $('meta').textContent = `${count(arr.length)} · מיון: שכבה › תחום › נושא · ${SORTS[S.sort] || SORTS.smart}`;
  if (!arr.length) { $('app').className = ''; $('app').innerHTML = '<div class="empty">לא נמצאו קבצים</div>'; return; }
  const groups = new Map();
  for (const f of arr) { const k = groupLabel(f); if (!groups.has(k)) groups.set(k, { label: k, sortKey: groupKey(f), items: [] }); groups.get(k).items.push(f); }
  $('app').className = 'groups';
  $('app').innerHTML = [...groups.values()].sort(compareGroups).map(g => `<section class="group"><div class="ghead"><span>${esc(g.label)}</span><span>${count(g.items.length)}</span></div><div class="grid">${g.items.map(card).join('')}</div></section>`).join('');
  document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => open(b.dataset.view));
}
function infoLine(f) {
  const bits = [];
  if (f.author && f.author !== 'unknown') bits.push(`מחבר: ${esc(f.author)}`);
  if (f.year && f.year !== 'unknown') bits.push(`שנה: ${esc(f.year)}`);
  const gs = safeList(f.grades).length ? safeList(f.grades).map(x => G[x] || x).join(', ') : gradeLabel(f);
  if (gs && gs !== 'לא ידוע') bits.push(`שכבות: ${esc(gs)}`);
  if (unitKey(f) !== 'unknown') bits.push(`רמה: ${esc(unitLabel(f))}`);
  if (categoryLabel(f) && categoryLabel(f) !== 'לא מסווג') bits.push(`תחום: ${esc(categoryLabel(f))}`);
  if (typeLabel(f) && typeLabel(f) !== 'לא ידוע') bits.push(`סוג: ${esc(typeLabel(f))}`);
  if (isExam(f) && examBucket(f) !== 'all') bits.push(`קטגוריית מבחן: ${esc(EXAM_BUCKETS[examBucket(f)])}`);
  if (f.source_type) bits.push(`מקור: ${esc(repo(f) ? 'קובץ במאגר' : 'קישור חיצוני')}`);
  return bits.length ? `<div class="file-details">${bits.map(x => `<span>${x}</span>`).join('')}</div>` : '';
}
function card(f) {
  const u = url(f);
  const e = ext(f);
  const labels = [activeGradeLabel(f), activeGradeKey(f) === 'high-school' ? unitLabel(f) : '', categoryLabel(f), typeLabel(f), e ? '.' + e : ''].filter(Boolean);
  const ts = topics(f).slice(0, 4);
  const isRepo = repo(f);
  const viewAction = isRepo ? `<button class="act view" data-view="${esc(f.id)}">👁 צפייה מוטמעת</button>` : (u ? `<a class="act view" href="${esc(u)}" target="_blank">↗ פתח קישור</a>` : '<button class="act view disabled" aria-disabled="true">אין קישור פעיל</button>');
  const openAction = u ? `<a class="act" href="${esc(u)}" target="_blank">↗ פתח</a>` : '';
  const dlAction = downloadButton(f);
  return `<article class="file"><div class="body"><div class="ft"><div class="ico">${I[e] || '📄'}</div><div class="title">${esc(title(f))}</div></div><div class="tags">${labels.map(x => `<span class="tag">${esc(x)}</span>`).join('')}</div>${ts.length ? `<div class="tags">${ts.map(x => `<span class="tag topic">${esc(x)}</span>`).join('')}</div>` : ''}${infoLine(f)}<div class="meta">${isRepo ? '📁 קובץ פנימי · הורדה ישירה' : '🔗 קישור חיצוני'} ${f.year && f.year !== 'unknown' ? ' · ' + esc(f.year) : ''}</div></div><div class="acts">${viewAction}${openAction}${dlAction}</div></article>`;
}
function open(id) {
  const f = S.byId.get(id);
  if (!f) return;
  const u = url(f);
  const canDownload = downloadable(f);
  $('mt').textContent = title(f);
  $('ms').textContent = canDownload ? `${groupLabel(f)} · הורדה ישירה זמינה` : groupLabel(f);
  $('mo').href = u;
  $('mo').target = '_blank';
  $('mo').rel = 'noopener noreferrer';
  if (canDownload) { $('md').href = downloadUrl(f); $('md').download = downloadName(f); $('md').textContent = '⬇ הורדה מהירה'; $('md').title = 'הורדה ישירה ומהירה של הקובץ'; $('md').classList.remove('disabled'); $('md').removeAttribute('aria-disabled'); }
  else { $('md').removeAttribute('href'); $('md').removeAttribute('download'); $('md').textContent = 'אין הורדה ישירה'; $('md').title = 'אין קישור הורדה ישיר לקובץ זה'; $('md').classList.add('disabled'); $('md').setAttribute('aria-disabled', 'true'); }
  $('viewer').src = 'about:blank';
  $('viewer').title = 'תצוגה מוטמעת: ' + title(f);
  $('viewer').setAttribute('loading', 'eager');
  $('modal').style.display = 'block';
  document.body.style.overflow = 'hidden';
  setTimeout(() => { $('viewer').src = viewUrl(f); }, 50);
}
function close() { $('modal').style.display = 'none'; $('viewer').src = 'about:blank'; document.body.style.overflow = ''; }
init();
