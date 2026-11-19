// Renders JS career boards (Hologic NA, 3DR Labs Paylocity) and prints JSON [{source,title,location,url}].
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {});
  const p = await b.newPage({ ignoreHTTPSErrors: true });
  const out = [];
  // Hologic: crawl every listing page; each card = title + location + teaser, separated by "View details →"
  for (let pg = 0; pg < 40; pg++) {
    await p.goto(`https://na.careers.hologic.com/en/search?page=${pg}`, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
    await p.waitForTimeout(2000);
    const links = await p.$$eval('a', as => as.filter(a => /search\/\d{9,}/.test(a.href)).map(a => a.href));
    if (!links.length) break;
    const body = (await p.innerText('main').catch(() => p.innerText('body'))).replace(/\s+/g, ' ');
    const start = body.search(/\d+ Jobs found/);
    const chunks = body.slice(start).replace(/^\d+ Jobs found /, '').split('View details →').map(s => s.trim());
    [...new Set(links)].forEach((u, i) => {
      const c = chunks[i] || '';
      const m = c.match(/^(.*?)\s((?:[A-Z][\w .'-]+, )?(?:[A-Z][\w .'-]+, )?(?:United States|Canada|Mexico|United Kingdom|Germany|France|Japan|Korea, Republic of|Costa Rica|China|Australia|[A-Z][a-z]+)(?:\s|$))/);
      out.push({ source: 'Hologic', title: m ? m[1] : c.slice(0, 80), location: m ? m[2].trim() : '', url: u, text: c.slice(0, 300) });
    });
  }
  // 3DR Labs (Paylocity)
  await p.goto('https://recruiting.paylocity.com/recruiting/jobs/All/c8b7fb7f-4dd3-4dd6-8e3d-c4065ebdcca0/3DR-Labs-LLC', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await p.waitForTimeout(3000);
  const tdr = await p.$$eval('a', as => as.filter(a => /Details\/\d+/.test(a.href)).map(a => ({ url: a.href, title: a.innerText.replace(/\s+/g, ' ').trim() })));
  tdr.forEach(j => out.push({ source: '3DR Labs', title: j.title, location: 'Remote (3DR Labs)', url: j.url, text: '' }));
  console.log(JSON.stringify(out));
  await b.close();
})();
