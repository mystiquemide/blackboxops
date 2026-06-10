import { chromium } from 'playwright';

const base = process.env.LANDING_URL ?? 'http://localhost:5173';
const out = 'scripts/shots';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(base, { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
await page.screenshot({ path: `${out}/01-hero.png` });
for (const [name, y] of [
  ['02-statement', 1400],
  ['03-showcase-step1', 2600],
  ['04-showcase-step3', 4600],
  ['05-showcase-step4', 6200],
  ['06-stack-mid', 8200],
  ['07-arch', 10800],
  ['08-footer', 13400],
]) {
  await page.evaluate((top) => window.scrollTo({ top, behavior: 'instant' }), y);
  await page.waitForTimeout(1300);
  await page.screenshot({ path: `${out}/${name}.png` });
}
await browser.close();
console.log('done');
