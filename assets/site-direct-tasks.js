(() => {
  function ensureSplitShell() {
    let details = document.getElementById('details');
    if (details) return details;
    const panel = document.querySelector('#modal .panel');
    const viewerWrap = document.querySelector('#modal .vw');
    if (!panel || !viewerWrap) return null;
    const split = document.createElement('div');
    split.className = 'split-view';
    panel.insertBefore(split, viewerWrap);
    split.appendChild(viewerWrap);
    details = document.createElement('aside');
    details.id = 'details';
    details.className = 'details';
    details.setAttribute('aria-label', 'פרטי המשימה');
    split.appendChild(details);
    return details;
  }
  function row(k, v) { return v ? `<div class="detail-row"><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>` : ''; }
  function yn(v) { return v === true ? 'כן' : v === false ? 'לא' : 'לא ידוע'; }
  function realCredit(v) { return v && v !== 'unknown' ? String(v).trim() : ''; }
  function creditText(f) { const parts = []; const editor = realCredit(f.editor); const credit = realCredit(f.credit); if (editor) parts.push(`בעריכת ${editor}`); if (credit) parts.push(credit); return parts.join(' · '); }
  function detailsHtml(f) {
    const u = url(f);
    const tags = topics(f).map(t => `<span class="tag topic">${esc(t)}</span>`).join('');
    const openLink = u ? `<a class="act view" href="${esc(u)}" target="_blank" rel="noopener noreferrer">↗ פתח בכרטיסייה</a>` : '<button class="act view disabled" type="button" aria-disabled="true">אין קישור פעיל</button>';
    const dl = downloadButton(f) || '<button class="act down disabled" type="button" aria-disabled="true">אין הורדה ישירה</button>';
    return `<aside class="detail-panel" aria-label="פרטים ופעולות"><h3>פרטי המשימה</h3><p class="detail-title">${esc(title(f))}</p>${tags ? `<div class="tags detail-tags">${tags}</div>` : ''}<dl class="detail-table">${row('שכבה', activeGradeLabel(f))}${row('תחום', categoryLabel(f))}${row('נושא', mainTopic(f))}${row('סוג', typeLabel(f))}${row('יחידות', activeGradeKey(f) === 'high-school' ? unitLabel(f) : '')}${row('שנה', f.year && f.year !== 'unknown' ? f.year : '')}${row('מחבר', f.author && f.author !== 'unknown' ? f.author : '')}${row('קרדיט', creditText(f))}${row('שם קובץ', f.file_name || '')}${row('הטמעה', yn(f.can_embed))}${row('הדפסה', yn(f.print_ready))}</dl><div class="detail-actions">${openLink}${dl}</div></aside>`;
  }
  filters = function() {
    const g = GRADE_BUTTONS.filter(grade => S.files.some(f => hasGrade(f, grade)));
    const searching = !!S.q.trim();
    $('filters').innerHTML = S.g === 'all' && !searching ? gradeGateway(g) : searching ? backButton(UI.back) + sortBar() : S.c === 'all' ? backButton(UI.backToGrades) + gradeHub() + highSchoolHub() : backButton(UI.backToDomains) + sortBar();
    document.querySelectorAll('[data-grade-go]').forEach(b => b.onclick = () => { S.g = b.dataset.gradeGo || 'all'; S.u = 'all'; S.c = 'all'; S.t = 'all'; S.exam = 'all'; S.topic = ''; S.q = ''; $('q').value = ''; render(); });
    document.querySelectorAll('[data-domain]').forEach(b => b.onclick = () => { S.c = b.dataset.domain || 'all'; S.t = 'all'; S.exam = 'all'; S.topic = ''; render(); });
    document.querySelectorAll('[data-unit]').forEach(b => b.onclick = () => { S.u = b.dataset.unit || 'all'; S.topic = ''; render(); });
    document.querySelectorAll('[data-sort]').forEach(b => b.onclick = () => { S.sort = b.dataset.sort || 'smart'; render(); });
    document.querySelectorAll('[data-back]').forEach(b => b.onclick = () => { if (S.q.trim()) { S.q = ''; $('q').value = ''; } else if (S.c !== 'all') { S.c = 'all'; S.topic = ''; } else if (S.g !== 'all') S.g = 'all'; render(); });
  };
  files = function() {
    const searching = !!S.q.trim();
    const gradeName = G[S.g] || S.g;
    if (S.g === 'all' && !searching) { setEmpty('', UI.homeHint); return; }
    if (!searching && S.c === 'all') { setEmpty(`${UI.gradeTitlePrefix}${gradeName}`, UI.chooseDomain); return; }
    S.topic = '';
    const arr = filtered().sort(compareFiles);
    $('ttl').textContent = searching ? UI.searchResultsTitle : `${C[S.c] || S.c} · ${gradeName}`;
    $('meta').textContent = `${count(arr.length)} · מיון: שכבה › תחום › קבצים · ${SORTS[S.sort] || SORTS.smart}`;
    if (!arr.length) { $('app').className = ''; $('app').innerHTML = `<div class="empty">${UI.noResults}</div>`; return; }
    const groups = new Map();
    for (const f of arr) { const k = groupLabel(f); if (!groups.has(k)) groups.set(k, { label: k, sortKey: groupKey(f), items: [] }); groups.get(k).items.push(f); }
    $('app').className = 'groups task-list';
    $('app').innerHTML = [...groups.values()].sort(compareGroups).map(g => `<section class="group"><div class="ghead"><span>${esc(g.label)}</span><span>${count(g.items.length)}</span></div><div class="grid task-grid">${g.items.map(card).join('')}</div></section>`).join('');
    document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => open(b.dataset.view));
  };
  card = function(f) {
    const e = ext(f);
    const tags = topics(f).slice(0, 3).map(x => `<span class="tag topic">${esc(x)}</span>`).join('');
    return `<article class="file task-row"><div class="body"><div class="ft"><div class="ico">${I[e] || '📄'}</div><div class="task-copy"><button class="task-title act view" type="button" data-view="${esc(f.id)}"><span class="title">${esc(title(f))}</span></button>${tags ? `<div class="tags">${tags}</div>` : ''}</div></div></div></article>`;
  };
  open = function(id) {
    const f = S.byId.get(id); if (!f) return;
    const u = url(f); const canDownload = downloadable(f);
    $('mt').textContent = title(f); $('ms').textContent = `תצוגה מוטמעת · ${groupLabel(f)}`;
    if (u) { $('mo').href = u; $('mo').target = '_blank'; $('mo').rel = 'noopener noreferrer'; $('mo').classList.remove('disabled'); $('mo').removeAttribute('aria-disabled'); } else { $('mo').removeAttribute('href'); $('mo').classList.add('disabled'); $('mo').setAttribute('aria-disabled', 'true'); }
    if (canDownload) { $('md').href = downloadUrl(f); $('md').download = downloadName(f); $('md').textContent = '⬇ הורדה מהירה'; $('md').classList.remove('disabled'); $('md').removeAttribute('aria-disabled'); } else { $('md').removeAttribute('href'); $('md').removeAttribute('download'); $('md').textContent = 'אין הורדה ישירה'; $('md').classList.add('disabled'); $('md').setAttribute('aria-disabled', 'true'); }
    const d = ensureSplitShell(); if (d) d.innerHTML = detailsHtml(f);
    $('viewer').src = 'about:blank'; $('viewer').title = 'תצוגה מוטמעת: ' + title(f); $('modal').style.display = 'block'; document.body.style.overflow = 'clip';
    setTimeout(() => { $('viewer').src = viewUrl(f); }, 50);
  };
  close = function() { $('modal').style.display = 'none'; $('viewer').src = 'about:blank'; const d = document.getElementById('details'); if (d) d.innerHTML = ''; document.body.style.overflow = ''; };
  try { if (S.files && S.files.length) render(); } catch {}
})();
