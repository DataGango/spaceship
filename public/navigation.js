(() => {
  const script = document.currentScript;
  const base = new URL('./', script.src);
  const pages = [
    ['index.html', 'Dashboard'],
    ['mission-lab.html', 'Mission Lab'],
    ['drone-survey.html', 'Drone Survey'],
    ['quantum-frontier.html', 'Quantum Frontier'],
  ];
  const current = pages.find(([file]) => location.pathname.endsWith('/' + file)) || pages[0];
  const header = document.querySelector('header');
  if (!header) return;
  document.querySelector('.desk-nav')?.remove();
  header.className = 'workspace-header';
  header.replaceChildren();
  const brand = document.createElement('a');
  brand.className = 'workspace-brand';
  brand.href = new URL('index.html', base).href;
  brand.setAttribute('aria-label', 'Astra Institute dashboard');
  const emblem = document.createElement('span');
  emblem.className = 'workspace-emblem';
  emblem.textContent = 'A';
  emblem.setAttribute('aria-hidden', 'true');
  const name = document.createElement('span');
  name.textContent = 'Astra Institute';
  const subtitle = document.createElement('small');
  subtitle.textContent = 'Research Observatory';
  name.append(subtitle);
  brand.append(emblem, name);
  const nav = document.createElement('nav');
  nav.className = 'workspace-navigation';
  nav.setAttribute('aria-label', 'Primary navigation');
  for (const [file, label] of pages) {
    const link = document.createElement('a');
    link.href = new URL(file, base).href;
    link.textContent = label;
    if (file === current[0]) link.setAttribute('aria-current', 'page');
    nav.append(link);
  }
  header.append(brand, nav);
  const context = document.createElement('div');
  context.className = 'workspace-context';
  const back = document.createElement('a');
  back.href = brand.href;
  back.className = 'workspace-back';
  back.textContent = 'Back';
  back.setAttribute('aria-label', 'Back to previous workspace page or dashboard');
  back.addEventListener('click', event => {
    if (!document.referrer || history.length <= 1) return;
    const previous = new URL(document.referrer);
    if (previous.origin === base.origin && pages.some(([file]) => previous.pathname === new URL(file, base).pathname || (file === 'index.html' && previous.pathname === base.pathname))) {
      event.preventDefault();
      history.back();
    }
  });
  const breadcrumbs = document.createElement('nav');
  breadcrumbs.setAttribute('aria-label', 'Breadcrumb');
  const home = document.createElement('a');
  home.href = brand.href;
  home.textContent = 'Dashboard';
  if (current[0] === 'index.html') home.setAttribute('aria-current', 'page');
  breadcrumbs.append(home);
  if (current[0] !== 'index.html') {
    const label = document.createElement('span');
    label.textContent = ' / ' + current[1];
    label.setAttribute('aria-current', 'page');
    breadcrumbs.append(label);
  }
  context.append(back, breadcrumbs);
  header.after(context);
})();