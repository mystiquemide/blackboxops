import { chromium } from 'playwright';

const base = process.env.LANDING_URL ?? 'http://localhost:5173';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto(`${base}/signin`, { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
await page.screenshot({ path: 'scripts/shots/auth.png' });

await page.evaluate(() => {
  localStorage.setItem('blackboxops.auth.token', 'demo-preview-token');
  localStorage.setItem('blackboxops.auth.user', JSON.stringify({ email: 'judge@blackboxops.demo', name: 'Judge Demo', provider: 'demo' }));
});
for (const route of ['dashboard', 'incidents', 'policies']) {
  await page.goto(`${base}/${route}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `scripts/shots/${route}.png` });
}
await browser.close();
console.log('done');
