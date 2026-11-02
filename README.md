# apply-jobs: a Claude Code skill for tailored job applications

Claude Code pulls your matches from [DreamWork](https://www.dreamworkhq.com/), screens them (location, pay, optional H-1B sponsorship check), writes a **one-page resume and cover letter tailored to each job description**, fills the Ashby / Greenhouse / Lever form in your browser, verifies the submission, and logs it.

## Requirements
- macOS with Google Chrome (headless Chrome renders the PDFs; set `CHROME=/path/to/chrome` elsewhere)
- Python 3, Node (optional), `pdfinfo` / `pdftoppm` from poppler (`brew install poppler`)
- [Claude Code](https://claude.com/claude-code) with the **Playwright MCP browser extension** connected (tools named `mcp__playwright-extension__*`)
- A DreamWork account, logged in, in that browser

## Install
```bash
git clone https://github.com/<owner>/job-apply-skill.git
cd job-apply-skill
cp -r skill/apply-jobs ~/.claude/skills/
cp -r job-hunt ~/job-hunt
```

## Make it yours (required)
1. **`~/job-hunt/profile.py`**: your name, contact info, form answers, work-authorization answers, resume pillars, experience, and default stories. Replace every `<placeholder>`.
2. **`~/.claude/skills/apply-jobs/references/profile.md`**: the same facts in prose. The agent claims **only** what's written here.
3. **`~/job-hunt/fetch_dreamwork.js`**: edit the location filters (`nyc`, `usRemote`) and pay floors (170000 / 190000).
4. **`~/.claude/skills/apply-jobs/SKILL.md`**: adjust the "Non-negotiable rules" to your preferences.
5. Don't need visa sponsorship? The agent runs `screen.py --no-h1b` (say so in profile.md).

Check your master resume: `cd ~/job-hunt && python3 resume.py`, then open `out/<Name>_Master.pdf`.

## Use
In Claude Code: `/apply-jobs 5`, or "apply to 5 jobs", or "tailor my resume for <url>".

## Notes
- Answers are only as truthful as your profile. Review the first few submissions yourself.
- `references/form-quirks.md` holds hard-won ATS gotchas; the agent adds to it as it learns.
- `data/`, `out/` and `fill_now.js` are gitignored (they hold your job data and PDFs).
