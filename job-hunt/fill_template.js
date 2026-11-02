async (page) => {
  const CFG = __CFG__;
  const P = CFG.profile;  // from profile.py FORM
  // Ordered rules: question regex -> {text} for free text, or {choose: [regex...]} for radio/select/checkbox
  const RULES = [
    [/preferred.*name|first name/i, {text: P.first}],
    [/last name|surname|family name/i, {text: P.last}],
    [/^\s*(full )?name\b|legal name/i, {text: P.full}],
    [/e-?mail/i, {text: P.email}],
    [/phone|mobile/i, {text: P.phone}],
    [/linkedin/i, {text: P.linkedin}],
    [/github/i, {text: P.github}],
    [/website|portfolio|personal (site|url)/i, {text: P.github}],
    [/type of visa|visa (type|status)|immigration status|when does it expire/i, {choose: [/^yes/i], text: P.visa_text}],
    [/sponsor/i, {choose: [P.needs_sponsorship ? /^yes/i : /^no/i], text: P.sponsorship_text}],
    [/authori[sz]ed|legally (able|eligible)|eligible to work|right to work/i, {choose: [/^yes/i], text: 'Yes'}],
    [/salary|compensation|pay expectation|desired pay/i, {text: P.salary}],
    [/how did you (hear|find)|source|referr?ed by|where did you/i, {text: P.hear, choose: [/job board/i, /online|website|internet|search/i, /^other/i]}],
    [/years of (professional |relevant )?experience|how many years/i, {text: P.years}],
    [/notice|start date|when can you start|availability to start/i, {text: P.notice}],
    [/which office|office\(s\)|preferred office|office location/i, {choose: [new RegExp(P.office_regex, 'i')]}],
    [/relocat|on-site in nyc|in office|office hub|located within/i, {choose: [new RegExp(P.office_regex + '|happy to work in office|^yes', 'i')], text: P.relocation}],
    [/hybrid|in[- ]office|on[- ]?site|commut|days a week|in person|new york|nyc/i, {choose: [/^yes/i], text: 'Yes'}],
    [/current (location|city)|where are you (located|based)|^location|city/i, {text: P.city}],
    [/current (company|employer)/i, {text: P.current_company}],
    [/current (title|role)/i, {text: P.current_title}],
    [/^country|country\*?$/i, {choose: [/^united states( of america)?$/i, /united states/i], text: 'United States'}],
    [/highest (level of )?education|degree/i, {choose: [new RegExp(P.education_regex, 'i')], text: P.education_text}],
    [/gender|pronoun/i, {choose: [/decline|prefer not|don.t wish|not to (say|disclose)/i]}],
    [/race|ethnic|hispanic|latino/i, {choose: [/decline|prefer not|don.t wish|not to (say|disclose)/i]}],
    [/veteran/i, {choose: [/decline|prefer not|don.t wish|not a (protected )?veteran|i am not/i]}],
    [/disabilit/i, {choose: [/decline|prefer not|don.t wish|do not want/i]}],
    [/sexual orientation|transgender|lgbt/i, {choose: [/decline|prefer not|don.t wish/i]}],
    [/privacy|consent|acknowledge|agree|certify|attest/i, {choose: [/yes|agree|acknowledge|i (do|have)|confirm|accept/i], check: true}],
  ];

  const qtext = async (el) => el.evaluate((i) => {
    if (['radio','checkbox'].includes(i.type)) {
      const grp = i.name ? [...document.getElementsByName(i.name)] : [i];
      const optTexts = new Set(grp.map((x) => ((x.id && document.querySelector(`label[for="${CSS.escape(x.id)}"]`)?.innerText) || x.closest('label')?.innerText || x.parentElement?.innerText || '').trim()));
      let p = i;
      for (let k = 0; k < 10; k++) {
        p = p.parentElement; if (!p) break;
        if (!grp.every((x) => p.contains(x))) continue;
        const lines = p.innerText.split('\n').map((t) => t.trim()).filter((t) => t && !optTexts.has(t));
        if (lines.length) return lines.join(' ');
      }
    }
    if (i.id) { const l = document.querySelector(`label[for="${CSS.escape(i.id)}"]`); if (l && !['radio','checkbox'].includes(i.type)) return l.innerText; }
    let p = i;
    for (let k = 0; k < 8; k++) {
      p = p.parentElement; if (!p) break;
      const l = p.querySelector(':scope > label, :scope > legend, :scope > div > label, :scope > fieldset > legend');
      if (l && l.innerText.trim() && !l.contains(i)) return l.innerText;
    }
    return i.getAttribute('aria-label') || i.placeholder || i.name || '';
  });
  const optText = async (el) => el.evaluate((i) => (i.closest('label')?.innerText || (i.id && document.querySelector(`label[for="${CSS.escape(i.id)}"]`)?.innerText) || i.parentElement?.innerText || i.value || '').trim());
  const EXTRA = (CFG.extra || []).map(([re, t]) => [new RegExp(re, 'i'), {text: t}]).concat([
    [/why (are you|do you want|.*interest)|what (interests|excites|draws)|why .*(join|work)/i, {text: CFG.why}],
    [/agent|llm|\bai\b.*(built|project|use case)|use case/i, {text: CFG.agentstory}],
    [/example from your|tell us about a time|describe a (time|project|situation)|proud of|accomplishment|challenging project/i, {text: CFG.story}],
    [/at least 18|over 18|18 years/i, {choose: [/^yes/i], text: 'Yes'}],
    [/looking for in (your|a) next|what would you like to avoid|ideal (role|job)/i, {text: CFG.looking}],
  ]);
  EXTRA.push([/at least 18|over 18|18 years/i, {choose: [/^yes/i], text: 'Yes'}]);
  const rule = (q) => (EXTRA.find(([re]) => re.test(q)) || RULES.find(([re]) => re.test(q)))?.[1];
  const filled = [], skipped = [];
  await page.bringToFront();
  const realClick = async (h) => { try { await h.click({timeout: 4000}); } catch { await h.evaluate((x) => x.click()); } };
  const labelOf = (inp) => inp.evaluateHandle((i) => (i.id && document.querySelector(`label[for="${CSS.escape(i.id)}"]`)) || i.closest('label') || i);
  if (CFG.goto) {
    await page.goto(CFG.goto);
    await page.waitForSelector(CFG.ready || 'input[type=email], #_systemfield_email, input[name*=email i]', {timeout: 40000, state: 'attached'});
    await page.waitForTimeout(2000);
  }

  // file uploads
  for (const f of await page.$$('input[type=file]')) {
    const q = ((await qtext(f)) + ' ' + ((await f.getAttribute('id')) || '') + ' ' + ((await f.getAttribute('name')) || '')).toLowerCase();
    if (/autofill/.test(q)) continue;
    const kind = /cover/.test(q) ? 'cover' : (/resume|cv/.test(q) ? 'resume' : null);
    if (!kind) { skipped.push(`FILE: ${q.slice(0, 120)}`); continue; }
    await f.evaluate((inp, [b64, name]) => {
      const bin = atob(b64); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      const dt = new DataTransfer(); dt.items.add(new File([u], name, {type: 'application/pdf'}));
      inp.files = dt.files; inp.dispatchEvent(new Event('input', {bubbles: true})); inp.dispatchEvent(new Event('change', {bubbles: true}));
    }, [CFG[kind + '_b64'], CFG[kind + '_name']]);
    filled.push(kind);
  }
  await page.waitForTimeout(1500);

  // text fields
  for (const el of await page.$$('input[type=text], input[type=email], input[type=tel], input[type=url], input[type=number], input:not([type]), textarea')) {
    if (!(await el.isVisible()) || (await el.getAttribute('role')) === 'combobox' || (await el.getAttribute('aria-autocomplete'))) continue;
    if ((await el.inputValue()).trim()) continue;
    const q = (await qtext(el)).trim().replace(/\s+/g, ' ');
    if (/recaptcha/i.test(q)) continue;
    const r = rule(q);
    if (r?.text) { await el.fill(r.text); await el.press('Tab').catch(() => {}); filled.push(`${q.slice(0, 60)} = ${r.text}`); }
    else skipped.push(`TEXT: ${q.slice(0, 200)}`);
  }

  // radios & checkboxes, grouped by name
  const groups = {};
  for (const el of await page.$$('input[type=radio], input[type=checkbox]:not(fieldset input)')) {
    const n = (await el.getAttribute('name')) || (await el.getAttribute('id'));
    (groups[n] ||= []).push(el);
  }
  for (const [n, els] of Object.entries(groups)) {
    if (await els[0].evaluate((i) => { let p = i; for (let k = 0; k < 6; k++) { p = p.parentElement; if ([...p.querySelectorAll('button')].filter((b) => /^(yes|no)$/i.test(b.innerText.trim())).length === 2) return true; } return false; })) continue;
    if (await els[0].evaluate((i) => [...document.getElementsByName(i.name)].some((x) => x.checked))) continue;
    let q = (await qtext(els[0])).trim().replace(/\s+/g, ' ');
    const opts = []; for (const e of els) opts.push(await optText(e));
    if (opts.length === 1 && q === opts[0]) { // lone checkbox: walk higher for question
      q = await els[0].evaluate((i) => { let p = i; for (let k = 0; k < 10; k++) { p = p.parentElement; if (p?.innerText?.length > 40) return p.innerText; } return ''; });
      q = q.replace(/\s+/g, ' ');
    }
    const r = rule(q);
    let done = false;
    if (r?.choose) {
      for (const re of r.choose) {
        const idx = opts.findIndex((o) => re.test(o));
        if (idx >= 0) { await realClick(await labelOf(els[idx])); filled.push(`${q.slice(0, 60)} = ${opts[idx]}`); done = true; break; }
      }
    }
    if (!done && r?.check && els.length === 1) { await realClick(await labelOf(els[0])); filled.push(`${q.slice(0, 60)} = [x]`); done = true; }
    if (!done) skipped.push(`CHOICE: ${q.slice(0, 160)} || ${opts.join(' / ').slice(0, 200)}`);
  }

  // native selects
  for (const s of await page.$$('select')) {
    if (!(await s.isVisible())) continue;
    const cur = await s.evaluate((x) => x.selectedIndex > 0);
    if (cur) continue;
    const q = (await qtext(s)).trim().replace(/\s+/g, ' ');
    const opts = await s.evaluate((x) => [...x.options].map((o) => o.text));
    const r = rule(q);
    let idx = -1; for (const re of (r?.choose || [])) { idx = opts.findIndex((o, k) => k > 0 && re.test(o)); if (idx >= 0) break; }
    if (idx > 0) { await s.selectOption({index: idx}); filled.push(`${q.slice(0, 60)} = ${opts[idx]}`); }
    else skipped.push(`SELECT: ${q.slice(0, 160)} || ${opts.join(' / ').slice(0, 200)}`);
  }

  // fieldset checkbox groups (multi-select)
  for (const fs of await page.$$('fieldset')) {
    const info = await fs.evaluate((f) => { const cbs = [...f.querySelectorAll('input[type=checkbox]')]; if (cbs.length < 2 || cbs.some((c) => c.checked)) return null; return {q: (f.querySelector('legend')?.innerText || f.innerText.split('\n')[0]).replace(/\s+/g, ' '), opts: cbs.map((c) => ((c.id && document.querySelector(`label[for="${CSS.escape(c.id)}"]`)?.innerText) || c.closest('label')?.innerText || c.parentElement?.innerText || '').trim())}; });
    if (!info) continue;
    const r = rule(info.q);
    let idx = -1; for (const re of (r?.choose || [])) { idx = info.opts.findIndex((o) => re.test(o)); if (idx >= 0) break; }
    if (idx < 0) { skipped.push(`MULTI: ${info.q.slice(0, 120)} || ${info.opts.join(' / ').slice(0, 200)}`); continue; }
    await realClick(await labelOf(await fs.evaluateHandle((f, i) => f.querySelectorAll('input[type=checkbox]')[i], idx)));
    filled.push(`${info.q.slice(0, 60)} = ${info.opts[idx]}`);
  }
  // Ashby-style Yes/No button pairs backed by a hidden checkbox
  for (const cb of await page.$$('input[type=checkbox]')) {
    const info = await cb.evaluate((i) => { if (i.closest('fieldset')) return null; let p = i; for (let k = 0; k < 4; k++) { p = p.parentElement; const bs = [...p.querySelectorAll('button')].filter((b) => /^(yes|no)$/i.test(b.innerText.trim())); if (bs.length === 2) { const q = p.innerText.replace(/\s+/g, ' ').replace(/\s*Yes\s*No\s*$/, ''); if (!q.trim()) continue; return {q, sel: bs.some((b) => /selected|active|_active|checked/i.test(b.className) || b.getAttribute('aria-pressed') === 'true')}; } } return null; });
    if (!info) continue;
    const r = rule(info.q);
    const want = r?.choose?.some((re) => re.test('Yes')) ? 'Yes' : (r?.choose?.some((re) => re.test('No')) ? 'No' : null);
    if (!want) { skipped.push(`YESNO: ${info.q.slice(0, 200)}`); continue; }
    const clickYN = async (w) => realClick(await cb.evaluateHandle((i, w) => { let p = i; for (let k = 0; k < 6; k++) { p = p.parentElement; const b = [...p.querySelectorAll('button')].find((b) => b.innerText.trim() === w); if (b) return b; } return i; }, w));
    await clickYN(want === 'Yes' ? 'No' : 'Yes'); await page.waitForTimeout(400); await clickYN(want); await page.waitForTimeout(400);
    filled.push(`${info.q.slice(0, 60)} = ${want}`);
  }
  // location autocompletes
  for (const c of await page.$$('input[role=combobox]')) {
    if ((await c.inputValue()).trim()) continue;
    const q = (await qtext(c)).trim().replace(/\s+/g, ' ');
    if (!/city|location|where .*(live|based|located)/i.test(q)) continue;
    await c.fill(P.city_search); await c.press('End').catch(() => {}); await page.waitForTimeout(2500);
    const ok = await page.evaluate(() => { const o = [...document.querySelectorAll('[role=option]')].find((o) => o.innerText.toLowerCase().includes(P.city_search.toLowerCase())) || document.querySelector('[role=option]'); if (o) { o.click(); return o.innerText; } return null; });
    if (ok) filled.push(`${q.slice(0, 60)} = ${ok.trim()}`); else skipped.push(`COMBO(no options): ${q}`);
  }
  // react-select style comboboxes (Greenhouse): open, read options, click best
  for (const c of await page.$$('input[role=combobox]')) {
    if (!(await c.isVisible())) continue;
    const has = await c.evaluate((x) => { const ctl = x.closest('[class*=control]') || x.parentElement?.parentElement; return !!ctl?.querySelector('[class*=singleValue], [class*=multiValue]'); });
    if (has) continue;
    const q = (await qtext(c)).trim().replace(/\s+/g, ' ');
    const r = rule(q);
    if (!r) { skipped.push(`COMBO: ${q.slice(0, 160)}`); continue; }
    await page.keyboard.press('Escape').catch(() => {});
    await realClick(c);
    if (r.text && !r.choose) { await c.type(/city|location/i.test(q) ? P.city_search : r.text, {delay: 30}); }
    await page.waitForTimeout(/city|location/i.test(q) ? 2500 : 700);
    const lb = await c.getAttribute('aria-controls');
    const opts = lb ? await page.$$(`[id="${lb}"] [role=option]`) : await page.$$('[role=listbox] [role=option]');
    const texts = []; for (const o of opts) texts.push((await o.innerText()).trim());
    let idx = -1;
    for (const re of (r.choose || [/./])) { idx = texts.findIndex((t) => re.test(t)); if (idx >= 0) break; }
    if (idx >= 0) { await realClick(opts[idx]); filled.push(`${q.slice(0, 60)} = ${texts[idx]}`); }
    else { await page.keyboard.press('Escape'); skipped.push(`COMBO(no match): ${q.slice(0, 120)} || ${texts.join(' / ').slice(0, 200)}`); }
    await page.waitForTimeout(300);
  }
  return JSON.stringify({filled, skipped}, null, 1);
}
