# Tailoring a resume to one job description

Positioning: lead with **expertise areas, not job duties** (adjust to the user's own goal). Short, clear and distinctive. The layout (built by `resume.py`) is: name → headline → tagline → contact → 3-line summary → numbers strip (`NUMBERS` in profile.py) → **Areas of Expertise** (10 pillars, two columns, one proof line each) → compact Experience → Toolkit & Education. One page, always.

## Pillar ids
Use the ids defined in `~/job-hunt/profile.py` `PILLARS`. Use all of them (about 10), ordered by relevance; drop the least relevant if you add a role-specific one.

## Process for each job
1. **Extract the job's focus.** Read the full description and write `jd_focus`: its 3–5 real priorities in its own words (e.g. "paved paths, self-service, SLOs, replacing toil").
2. **headline:** the job's own title plus the candidate's angle, e.g. "Senior Platform Engineer · Platform & AI Infrastructure", "Senior SRE · Kubernetes & Reliability", "Forward-Deployed AI & Platform Architect". Avoid titles that sound far more senior or junior than the posting.
3. **tagline:** 3–4 phrases separated by " · ", using the job description's wording.
4. **summary:** about 3 lines (keep it under ~330 characters). Lead with the job's top need, then the hard numbers, then one line of the candidate's point of view. No buzzword soup.
5. **pillars:** order by relevance to the job; the first 4 should mirror `jd_focus`.
6. **pillar_text:** rewrite the proof line for the top 4–6 pillars in the job's vocabulary, keeping each under ~150 characters and only using facts from `profile.md`. Unlisted pillars keep their defaults.
7. **current_lead + current_bullets (3):** (overrides `EXPERIENCE[0]` in profile.py) angle the current role toward the job: e.g. SRE roles get reliability and incidents; platform roles get paved paths and self-service; AI-infra roles get LLM platform work. Keep each bullet to one line (~110 characters).
8. **skills:** put the job's stack first, but **only tools in profile.md**, and use the job's spelling (e.g. "EKS" vs "Kubernetes"). Never add unlisted tools just because the job wants them.
9. **cover_hook:** 1–2 sentences on what *this* team needs and why that's the candidate's exact work. `cover_proof` (3 paragraphs) can be overridden if the default proof doesn't fit.
10. **why:** a 3–4 sentence answer to "why us", specific to the company's product or mission and tied to a real piece of the candidate's work.
11. **extra:** `[[regex, answer], …]` for job-specific free-text questions you can anticipate from the description.

Then run `python3 prep.py tailor/<slug>.json`. If it reports 2 pages, trim the summary, pillar_text and bullets (longest first) and rerun.

## Quality bar
Tailored resumes must read noticeably differently. Compare against the master resume (`python3 resume.py` builds `out/<Name>_Master.pdf`): if only the headline changed, it isn't tailored. Example of the expected depth: `~/job-hunt/tailor/EXAMPLE_Acme_Senior_Platform_Engineer.json` (schema only; real ones need real content).

## Archetype cheat sheet (starting points, not final text)
| Role type | Lead pillars | Current-role angle |
|---|---|---|
| Platform / infra | k8s, cicd, dev, iac | paved paths, self-service, toil removal |
| SRE | k8s, obs, cost, sec | reliability, upgrades, capacity, observability |
| AI / ML infra | llm, data, k8s, cost | LLM platform, routing, cost attribution |
| Principal / head of | lead, k8s, cicd, iac | company-wide transformations |
