# ATS form quirks (learned on the first run, 2026-10-19)

## Playwright extension in general
- **File uploads:** `setInputFiles` is blocked ("Not allowed"). `fill_template.js` injects the PDFs via a DataTransfer object and dispatches change events, which works on Ashby and Greenhouse.
- **Background tab:** clicks wait forever for "stable". Call `page.bringToFront()` first; the template does this.
- **Use real clicks, not `element.click()` in JS.** A JS click can flip the UI without updating the app's saved state: the form looks complete but the server reports "Missing entry". The template uses real clicks with a JS fallback.
- **Blur text fields after filling** (press Tab). Ashby saves values on blur.
- `browser_run_code_unsafe` echoes the whole script, so output always overflows to a file. Use `~/job-hunt/res.sh`.
- A select-all shortcut didn't clear an input on macOS, which produced "YesYes". To replace a value, use `locator.fill()`, not keyboard select-all plus typing.

## Ashby (jobs.ashbyhq.com/<co>/<id>/application)
- Wait for `#_systemfield_email`.
- **Yes/No questions** are two `<button>`s backed by a hidden checkbox. Clicking the already-pressed answer does nothing, and the UI can show "Yes" while the server has null. The template clicks the opposite answer first, then the intended one.
- **Multi-select checkbox groups** (`fieldset`): "Which office(s)" → New York; "How did you hear" → Job board. The template handles priority order (job board before "other").
- **Location** is an autocomplete: type the city (`FORM.city_search`) and click the option.
- Some yes/no-looking questions are actually free-text inputs. Check `browser_find` when the server reports a missing field.
- **Verify via the server response:** `submit.js` captures `ApiSubmit…FormAction`. `errorMessages` names the exact missing fields. Success is `server: "ok"` and the page shows "Success" or "Thanks".

## Greenhouse (job-boards.greenhouse.io/<co>/jobs/<id>, or /embed/job_app?for=<co>&token=<id>)
- Wait for `#first_name`. File inputs have ids `resume` and `cover_letter` (labelled "attach").
- **Company sites that wrap Greenhouse** (e.g. harness.io/company/jobs/apply?gh_jid=…) redirect. Use `https://job-boards.greenhouse.io/embed/job_app?for=<board>&token=<gh_jid>` directly.
- **Dropdowns are react-select comboboxes:** click the input, read options **scoped to `aria-controls`** (`[id="<listbox>"] [role=option]`), and click the match. Without scoping, the phone country-code list ("Afghanistan +93…") bleeds in.
- "Country*" next to Phone is the phone country picker; pick "United States +1".
- Sponsorship, education and quiz questions are often dropdowns. Education options look like PhD / MBA / MS/MA / BS/BA; set `FORM.education_regex` to match yours.
- Some boards include a technical quiz (Legion: Pod vs Container → "A Pod is a logical grouping of one or more Containers"; URL-path routing → ALB; observability pillars → Metrics, Logs, Traces). Answer correctly.
- **Submit:** the page has a top "Apply" anchor button. `submit.js` targets "Submit application". Success is a `/confirmation` URL with "Thank you for applying."

## Lever (jobs.lever.co/<co>/<id>/apply)
Not exercised yet. Expect standard inputs plus an "Additional information" textarea, and possibly hCaptcha. If a captcha blocks it, skip and report.

## Not automatable without the user
Workday, Oracle Cloud HCM, iCIMS, SuccessFactors and SmartRecruiters (sometimes) need an account or login. Skip them and list them for the user, unless they've logged in already in the extension browser.
