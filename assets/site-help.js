(() => {
  function ensureHelpStyles() {
    if (document.getElementById('site-help-style')) return;
    const style = document.createElement('style');
    style.id = 'site-help-style';
    style.textContent = `
      .help-panel-backdrop{position:fixed;inset:0;z-index:998;background:#020617aa;backdrop-filter:blur(8px);display:none;align-items:center;justify-content:center;padding:18px}
      .help-panel-backdrop.open{display:flex}
      .help-panel{width:min(760px,96vw);max-height:86vh;overflow:auto;background:#0f172a;color:#e5e7eb;border:1px solid #ffffff22;border-radius:22px;box-shadow:0 24px 70px #0009;padding:22px;direction:rtl;font-family:Arial,sans-serif}
      .help-panel h2{margin:0 0 10px;font-size:24px;color:white}
      .help-panel p{line-height:1.7;color:#cbd5e1}
      .help-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}
      .help-card{background:#ffffff0b;border:1px solid #ffffff18;border-radius:16px;padding:14px}
      .help-card b{display:block;color:#fff;margin-bottom:6px}
      .help-close{float:left;border:0;background:#ffffff18;color:white;border-radius:12px;padding:8px 12px;font-weight:800;cursor:pointer}
    `;
    document.head.appendChild(style);
  }

  function ensureHelpPanel() {
    if (document.getElementById('site-help-panel')) return;
    const backdrop = document.createElement('div');
    backdrop.id = 'site-help-panel';
    backdrop.className = 'help-panel-backdrop';
    backdrop.innerHTML = `
      <section class="help-panel" role="dialog" aria-modal="true" aria-label="עזרה מהירה למאגר">
        <button id="site-help-close" class="help-close" type="button">סגור ×</button>
        <h2>עזרה מהירה למאגר</h2>
        <p>המאגר מיועד לפתיחה מהירה של קבצי מתמטיקה לפי שכבה, תחום, נושא וסוג קובץ.</p>
        <div class="help-grid">
          <div class="help-card"><b>1. חיפוש</b><span>הקלד שם נושא, שכבה, סוג קובץ או מילת מפתח בשורת החיפוש.</span></div>
          <div class="help-card"><b>2. סינון</b><span>לחץ על שכבה, תחום או סוג קובץ כדי לצמצם את הרשימה.</span></div>
          <div class="help-card"><b>3. צפייה מוטמעת</b><span>לחץ על “צפייה מוטמעת” כדי לראות את הקובץ בלי לצאת מהאתר.</span></div>
          <div class="help-card"><b>4. הורדה</b><span>לחץ על “הורדה” כדי לשמור את הקובץ למחשב או לטלפון.</span></div>
          <div class="help-card"><b>5. שיתוף קובץ</b><span>השתמש בכפתור העתק קישור או WhatsApp בכרטיס או בחלון הצפייה.</span></div>
          <div class="help-card"><b>6. שיתוף תצוגה</b><span>אחרי חיפוש וסינון, לחץ “העתק תצוגה” כדי לשלוח בדיוק את אותה תצוגה.</span></div>
        </div>
        <p>טיפ: קישור לקובץ נפתח ישירות בקובץ. קישור לתצוגה שומר את החיפוש והסינון הנוכחיים.</p>
      </section>
    `;
    document.body.appendChild(backdrop);
    backdrop.addEventListener('click', (event) => {
      if (event.target === backdrop) backdrop.classList.remove('open');
    });
    document.getElementById('site-help-close')?.addEventListener('click', () => backdrop.classList.remove('open'));
  }

  function ensureHelpButton() {
    const bar = document.querySelector('.bar');
    if (!bar || document.getElementById('site-help-open')) return;
    const btn = document.createElement('button');
    btn.id = 'site-help-open';
    btn.type = 'button';
    btn.className = 'btn';
    btn.textContent = '❔ עזרה מהירה';
    btn.addEventListener('click', () => {
      ensureHelpStyles();
      ensureHelpPanel();
      document.getElementById('site-help-panel')?.classList.add('open');
    });
    bar.appendChild(btn);
  }

  function boot() {
    ensureHelpStyles();
    ensureHelpPanel();
    ensureHelpButton();
  }

  document.addEventListener('DOMContentLoaded', boot);
  const observer = new MutationObserver(boot);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(boot, 500);
})();
