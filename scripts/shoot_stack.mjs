import { chromium } from 'playwright';

const base = process.env.LANDING_URL ?? 'http://localhost:5173';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(base, { waitUntil: 'networkidle' });
const top = await page.evaluate(() => {
  const el = document.querySelector('.lp-stack');
  return el.getBoundingClientRect().top + window.scrollY;
});
const vh = 900;
for (const [name, y] of [
  ['stack-1', top + vh * 0.6],
  ['stack-2', top + vh * 1.5],
  ['stack-3', top + vh * 2.4],
]) {
  await page.evaluate((pos) => window.scrollTo({ top: pos, behavior: 'instant' }), y);
  await page.waitForTimeout(1300);
  await page.screenshot({ path: `scripts/shots/${name}.png` });
}
await browser.close();
console.log('done');
