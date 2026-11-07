import { createRequire } from 'node:module'; const require = createRequire('/home/claude/.npm-global/lib/node_modules/'); const { chromium } = require('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport:{ width:1200, height:630 } });
await p.goto('file://' + process.argv[2] + '/og.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({ path:process.argv[2] + '/og-new.jpg', type:'jpeg', quality:90 }); await b.close();
