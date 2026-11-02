---
name: apply-jobs
description: Find, tailor and submit job applications from DreamWork (dreamworkhq.com) matches. Optionally screens for H-1B sponsorship (LCA history + job-description blockers), filters by location and pay, writes a JD-tailored one-page resume and cover letter per job, fills Ashby/Greenhouse/Lever forms through the Playwright browser extension, verifies submission, and logs to ~/job-hunt/applied.csv. Use when the user says "apply to N jobs", "/apply-jobs", "continue job applications", or asks to tailor a resume for a specific posting.
---

# Apply to jobs (DreamWork → tailored resume → ATS submit)

Everything lives in `~/job-hunt/`. Argument: number of applications to submit this run (default 10).
In the steps below, `<HOME>` means the user's absolute home directory (run `echo $HOME`); browser tools need absolute paths.

**Read before starting:**
- `references/profile.md`: who the candidate is, the facts you may claim, the standard form answers, the visa facts. Never claim anything not listed there. If it still contains `<placeholders>`, stop and ask the user to fill it in (and `~/job-hunt/profile.py`) first.
- `references/tailoring.md`: how to tailor the resume to each job description (required, not optional).
- `references/form-quirks.md`: ATS-specific gotchas learned the hard way. Read it before the first form.

## Non-negotiable rules (edit these to the user's own preferences)

1. **H-1B gate (only if `profile.md` says the candidate needs sponsorship).** Apply only if the company has H-1B LCA filings on record (h1bdata.info) **and** the job description doesn't refuse sponsorship or require citizenship, green card, clearance or ITAR. Sanity-check matched employer names: prefix search causes false hits (e.g. "Camber" matched Camber Pharmaceuticals). If the legal name differs (Chubb → ACE American Insurance), add it to `ALIASES` in `screen.py`. If the candidate does not need sponsorship, run `screen.py` with `--no-h1b`.
2. **Location.** Only the locations listed in `profile.md` (the defaults in `fetch_dreamwork.js` are NYC metro or fully remote US; edit the `nyc`/`usRemote` filters and pay floors there).
3. **Pay.** Prefer the highest-paying fits. Desired-salary answer comes from `profile.py` `FORM.salary`.
4. **Tailor every resume to its job description.** A handful of generic templates is too shallow. See `references/tailoring.md`.
5. **Truthful answers only.** Work-authorization and sponsorship answers exactly as `profile.md` states. EEO questions = decline. Don't invent metrics.
6. **The user delegated fully.** Run end to end without check-ins, but report clearly at the end. If a form asks something not covered by `profile.md` that materially changes the candidacy, skip that job and report it rather than guess.

## Pipeline

### 1. Fetch matches (browser must be logged in to DreamWork)
- Load the Playwright extension tools: `ToolSearch` query `playwright-extension`, max_results 30.
- `browser_navigate` → `https://www.dreamworkhq.com/`
- `browser_evaluate` with the function body from `~/job-hunt/fetch_dreamwork.js` and `filename: <HOME>/job-hunt/data/dreamwork.json`. It pre-filters by location, pay and recency (last 75 days) and fetches full descriptions.
- **Keyword search** (e.g. specific roles): `GET /api/listings?search=<q>&limit=25&offset=<n>`. It returns at most 25 per page, so page by 25 until empty. `recommended` only returns personal matches. If the browser tool can't write to `~/job-hunt`, save to its own output dir and copy into `~/job-hunt/data/`.
- DreamWork's own auto-apply (`/api/turbo-apply`) is a paid tier (returns 402 without it). Apply on each employer's ATS directly.

### 2. Screen
```bash
cd ~/job-hunt && python3 screen.py data/dreamwork.json          # with H-1B gate
cd ~/job-hunt && python3 screen.py data/dreamwork.json --no-h1b # without
```
This prints the ELIGIBLE list (NYC first, then pay, then H-1B depth) and the REJECTED list with reasons, writes `data/candidates.json`, caches H-1B lookups in `data/h1b_cache.json`, and skips anything already in `applied.csv`.
- Rows marked **CHECK** have ambiguous H-1B matches. Verify the employer is the same company (domain, HQ city, or a search with the legal name), then add the DreamWork name to `VERIFIED` in `screen.py`. If the hits belong to a different company, add it to `FALSE_MATCH`. Never apply to an unverified CHECK row.
- Prefer ATS platforms that automate cleanly: **ashby, greenhouse, lever**. Workday, Oracle Cloud, iCIMS and SuccessFactors need an account login; skip them unless the user has set one up.
- Pick N, plus 2–3 backups (some forms fail).

### 3. Tailor (per job)
Read the job's `description` from `data/candidates.json`, then write `~/job-hunt/tailor/<YYYY-MM-DD>_<Company>_<Role>.json` following `references/tailoring.md` (schema: `tailor/EXAMPLE_Acme_Senior_Platform_Engineer.json`). Then:
```bash
python3 prep.py tailor/<slug>.json
```
This builds the resume PDF and cover letter in `out/<slug>/`, **fails if the resume isn't one page** (trim and rerun), and writes `fill_now.js`. Glance at the rendered PDF (`pdftoppm -png -r 75 -f 1 -l 1 <pdf> /tmp/p`, then Read the PNG) for the first job of each run.

### 4. Fill
`mcp__playwright-extension__browser_run_code_unsafe` with `filename: <HOME>/job-hunt/fill_now.js`.
- The tool echoes the ~200KB script, so its output always overflows to a file. Read the result with `~/job-hunt/res.sh`, which prints FILLED and SKIPPED.
- For every SKIPPED item: if it's required, answer it by hand (see the form quirks for dropdowns, Yes/No buttons and checkbox groups) using `profile.md` facts. Write job-specific free text yourself, grounded in the candidate's real work.
- Re-check anything listed as filled that looks wrong (e.g. "How did you hear" picking the wrong option, or a question answered with an off-topic story).

### 5. Submit and verify
`browser_run_code_unsafe` with `filename: <HOME>/job-hunt/submit.js`. Success means the returned JSON shows **`server: "ok"`** (Ashby) or **`confirm: "Thank you for applying."` and a `/confirmation` URL** (Greenhouse). Anything else is a failure. Read `server` / `errs`, fix the named fields, and resubmit. Never log a job as submitted without one of those signals.

### 6. Log
```bash
python3 log.py tailor/<slug>.json SUBMITTED ["note about anything imperfect"]
python3 log.py tailor/<slug>.json SKIPPED "reason"
```

### 7. Report to the user
A table of every submission (company, role, pay, location, H-1B count), what was skipped and why, any imperfect answers, and the new resume paths. Offer the next batch from the remaining eligible list.

## Files

| Path | Purpose |
|---|---|
| `profile.py` | **The candidate's data**: contact, form answers, resume pillars/experience, default stories |
| `resume.py` | Resume renderer (HTML → PDF via headless Chrome); accepts per-job overrides |
| `prep.py` | Tailor JSON → resume PDF + cover PDF + `fill_now.js` |
| `fill_template.js` | Generic form filler (rules for every standard question) |
| `submit.js` | Clicks the real submit button, verifies server/confirmation |
| `screen.py` | JD blockers + optional H-1B LCA lookup + dedupe → `data/candidates.json` |
| `fetch_dreamwork.js` | In-browser DreamWork API pull + location/pay prefilter |
| `log.py`, `applied.csv` | Application log (the dedupe source) |
| `res.sh` | Pretty-print the last fill result |

When you learn a new form quirk or the user states a new rule, update the matching reference file so the next run benefits.
