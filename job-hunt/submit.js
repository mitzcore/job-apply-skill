async (page) => {
  const resp = page.waitForResponse(r => /ApiSubmit|\/applications|\/apply|submit/i.test(r.url()) && r.request().method() === 'POST', {timeout: 20000}).catch(() => null);
  const clicked = await page.evaluate(() => { const all = [...document.querySelectorAll('button, input[type=submit]')]; const txt = b => (b.innerText || b.value || '').trim(); const b = all.find(b => /^submit( (application|your application))?$/i.test(txt(b))) || all.find(b => /^send application$/i.test(txt(b))) || all.find(b => b.type === 'submit' && b.closest('form')); if (b) { b.click(); return b.innerText || b.value; } return null; });
  const r = await resp; let server = null;
  if (r) { try { const j = await r.json(); server = JSON.stringify(j).match(/"errorMessages":\[[^\]]*\]/)?.[0] || 'ok'; } catch { server = `status ${r.status()}`; } }
  await page.waitForTimeout(6000);
  const t = await page.evaluate(() => document.body.innerText);
  const m = t.match(/[^\n]*(thank|success|received|submitted|got it)[^\n]*/i);
  const errs = await page.evaluate(() => [...document.querySelectorAll('[role=alert], [class*=error i]')].map(e => e.innerText.trim()).filter(Boolean).slice(0, 6));
  return JSON.stringify({clicked, url: page.url(), server, confirm: m ? m[0].slice(0, 160) : null, errs});
}
