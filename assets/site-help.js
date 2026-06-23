(() => {
  function ensureAppIcon() {
    if (document.querySelector('link[rel="icon"][href="assets/icon.svg"]')) return;
    const icon = document.createElement('link');
    icon.rel = 'icon';
    icon.href = 'assets/icon.svg';
    icon.type = 'image/svg+xml';
    document.head.appendChild(icon);
  }

  function ensureAccessibilityBasics() {
    const search = document.getElementById('q');
    const clear = document.getElementById('clear');
    const app = document.getElementById('app');
    const header = document.querySelector('.top');
    const bar = document.querySelector('.bar');
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('mt');
    const modalSub = document.getElementById('ms');
    const close = document.getElementById('x');

    if (header && !header.getAttribute('role')) header.setAttribute('role', 'banner');
    if (bar && !bar.getAttribute('role')) bar.setAttribute('role', 'search');
    if (bar && !bar.getAttribute('aria-label')) bar.setAttribute('aria-label', 'חיפוש וסינון במאגר מתמטיקה');
    if (search && !search.getAttribute('aria-label')) search.setAttribute('aria-label', 'חיפוש במאגר לפי שם, נושא, כיתה או סוג קובץ');
    if (clear && !clear.getAttribute('aria-label')) clear.setAttribute('aria-label', 'נקה חיפוש וסינונים');
    if (app && !app.getAttribute('tabindex')) app.setAttribute('tabindex', '-1');
    if (app && !app.getAttribute('aria-live')) app.setAttribute('aria-live', 'polite');
    if (modal && modalTitle) modal.setAttribute('aria-labelledby', modalTitle.id);
    if (modal && modalSub) modal.setAttribute('aria-describedby', modalSub.id);
    if (close) close.setAttribute('aria-label', 'סגור חלון צפייה');
  }

  function ensureSkipLink() {
    if (document.getElementById('skip-to-maagar')) return;
    const skip = document.createElement('a');
    skip.id = 'skip-to-maagar';
    skip.className = 'skip-link';
    skip.href = '#app';
    skip.textContent = 'דלג לתוכן המאגר';
    skip.addEventListener('click', () => setTimeout(() => document.getElementById('app')?.focus(), 20));
    document.body.insertBefore(skip, document.body.firstChild);
  }

  function ensureHelpStyles() {
    if (document.getElementById('site-help-style')) return;
    const style = document.createElement('style');
    style.id = 'site-help-style';
    style.textContent = `
      .skip-link{position:fixed;right:12px;top:12px;z-index:1000;background:#ffffff;color:#07111f;border-radius:999px;padding:10px 14px;font:900 14px Arial,sans-serif;text-decoration:none;transform:translateY(-160%);transition:.16s ease;box-shadow:0 12px 32px #0008}
      .skip-link:focus{transform:translateY(0);outline:3px solid #93c5fd;outline-offset:2px}
      .help-panel-backdrop{position:fixed;inset:0;z-index:998;background:#020617aa;backdrop-filter:blur(8px);display:none;align-items:center;justify-content:center;padding:18px;overflow:auto}
      .help-panel-backdrop.open{display:flex}
      .help-panel{width:min(760px,96vw);max-height:86vh;overflow:auto;background:#0f172a;color:#e5e7eb;border:1px solid #ffffff22;border-radius:22px;box-shadow:0 24px 70px #0009;padding:22px;direction:rtl;font-family:Arial,sans-serif}
      .help-panel h2{margin:0 0 10px;font-size:24px;color:white}
      .help-panel p{line-height:1.7;color:#cbd5e1}
      .help-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));gap:12px;margin:16px 0}
      .help-card{background:#ffffff0b;border:1px solid #ffffff18;border-radius:16px;padding:14px;min-width:0;overflow-wrap:anywhere}
      .help-card b{display:block;color:#fff;margin-bottom:6px}
      .help-close{float:left;border:0;background:#ffffff18;color:white;border-radius:12px;padding:8px 12px;font-weight:800;cursor:pointer;min-height:40px}
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
    btn.setAttribute('aria-label', 'פתח עזרה מהירה לשימוש במאגר');
    btn.addEventListener('click', () => {
      ensureHelpStyles();
      ensureHelpPanel();
      document.getElementById('site-help-panel')?.classList.add('open');
    });
    bar.appendChild(btn);
  }

  function boot() {
    ensureAppIcon();
    ensureHelpStyles();
    ensureAccessibilityBasics();
    ensureSkipLink();
    ensureHelpPanel();
    ensureHelpButton();
  }

  document.addEventListener('DOMContentLoaded', boot);
  const observer = new MutationObserver(boot);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(boot, 500);
})();
