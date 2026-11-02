async () => {
  // Paste this function into mcp__playwright-extension__browser_evaluate while on https://www.dreamworkhq.com/
  // (logged in), with filename=<HOME>/job-hunt/data/dreamwork.json
  // Pulls all recommended matches, pre-filters (NYC metro or US-remote, pay, recency), then fetches full descriptions.
  const all = [];
  for (let off = 0; off < 2000; off += 50) {
    const r = await (await fetch(`/api/listings/recommended?limit=50&offset=${off}&sort=relevance`)).json();
    const items = r.listings || [];
    all.push(...items);
    if (items.length < 50) break;
  }
  const cutoff = new Date(Date.now() - 75 * 864e5).toISOString();
  const nyc = (l) => ['NY', 'NJ'].includes(l.locationState) || /new york|nyc|brooklyn|manhattan|jersey city|hoboken/i.test(l.location || '');
  const usRemote = (l) => l.remoteType === 'remote' && (/united states|\bUSA?\b|\bUS\b/i.test(l.location || '') || (l.remoteEligibilityCountries || []).includes('US') || !!l.locationState);
  const keep = all.filter((l) => (l.postedAt || '') >= cutoff
    && (!l.salaryPeriod || /year/i.test(l.salaryPeriod)) && (!l.salaryCurrency || l.salaryCurrency === 'USD')
    && ((nyc(l) && (l.salaryMax || 0) >= 170000) || (usRemote(l) && (l.salaryMax || 0) >= 190000)));
  const out = [];
  for (let i = 0; i < keep.length; i += 10) {
    const batch = await Promise.all(keep.slice(i, i + 10).map(async (l) => {
      try { const d = (await (await fetch(`/api/listings/${l.id}`)).json()).listing || {}; return {...l, description: d.description || ''}; }
      catch { return {...l, description: ''}; }
    }));
    out.push(...batch);
  }
  return JSON.stringify({fetchedAt: new Date().toISOString(), totalMatches: all.length, listings: out.map((l) => ({
    id: l.id, title: l.title, co: l.companyName, domain: l.companyDomain, loc: l.location, state: l.locationState, remote: l.remoteType,
    min: l.salaryMin, max: l.salaryMax, salarySource: l.salarySource, url: l.sourceUrl, plat: l.platform, posted: l.postedAt,
    seniority: l.seniorityLevel, score: l.matchScore, tech: l.techStack, description: l.description }))});
}
