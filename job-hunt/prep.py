#!/usr/bin/env python3
"""Build tailored resume + cover letter for one job and generate fill_now.js.

Usage: python3 prep.py tailor/<slug>.json
Output: out/<slug>/<Name>_Resume.pdf, <Name>_Cover_Letter.pdf, and ./fill_now.js
Fails loudly if the resume is not exactly one page.
"""
import json, sys, base64, html, subprocess, pathlib
import resume

ROOT = pathlib.Path(__file__).parent

from profile import NAME, FILE_PREFIX, FORM, DEFAULTS

def chrome_pdf(h, pdf):
    subprocess.run([resume.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", h.as_uri()], check=True, capture_output=True)

def cover(t, d):
    e = html.escape
    proof = t.get("cover_proof") or DEFAULTS["cover_proof"]
    body = (f"<p>Hello {e(t['co'])} team,</p>"
            f"<p>I am applying for the <b>{e(t['title'])}</b> role. {e(t['cover_hook'])}</p>"
            + "".join(f"<p>{e(p)}</p>" for p in proof) +
            f"<p>{e(DEFAULTS['cover_close'].format(co=t['co']))}</p>"
            f"<p>Best regards,<br>{e(NAME)}<br>{e(FORM['phone'])} · {e(FORM['email'])}</p>")
    h = d / f"{FILE_PREFIX}_Cover_Letter.html"; pdf = d / f"{FILE_PREFIX}_Cover_Letter.pdf"
    h.write_text("<!doctype html><html><head><meta charset='utf-8'><style>@page{size:Letter;margin:0.9in}"
                 "body{font-family:'Helvetica Neue',Arial;font-size:11pt;line-height:1.5;color:#1a1a1a}h1{font-size:18pt;margin:0}"
                 f".h{{color:#0b5cad;margin-bottom:24px}}</style></head><body><h1>{e(NAME.upper())}</h1><div class='h'>{e(resume.CONTACT)}</div>{body}</body></html>")
    chrome_pdf(h, pdf)
    return pdf

def main():
    tp = pathlib.Path(sys.argv[1])
    t = json.loads(tp.read_text())
    variant = {k: t[k] for k in ("headline", "tagline", "summary", "pillars", "skills", "pillar_text", "current_lead", "current_bullets") if k in t}
    variant.update(slug=t["slug"], dir=t["slug"])
    rpdf = resume.build(variant)
    pages = subprocess.run(["pdfinfo", str(rpdf)], capture_output=True, text=True).stdout
    n = next((l.split()[-1] for l in pages.splitlines() if l.startswith("Pages")), "?")
    if n != "1":
        sys.exit(f"RESUME IS {n} PAGES - shorten pillar_text/current_bullets/summary and rerun")
    cpdf = cover(t, rpdf.parent)

    u = t["url"]
    goto = (u.rstrip("/") + "/application") if "ashbyhq.com" in u else (u.rstrip("/") + "/apply" if "lever.co" in u else u)
    cfg = {
        "resume_b64": base64.b64encode(rpdf.read_bytes()).decode(), "resume_name": f"{FILE_PREFIX}_Resume.pdf",
        "cover_b64": base64.b64encode(cpdf.read_bytes()).decode(), "cover_name": f"{FILE_PREFIX}_Cover_Letter.pdf",
        "why": t["why"], "looking": t.get("looking", DEFAULTS["looking"]), "story": t.get("story", DEFAULTS["story"]),
        "agentstory": t.get("agentstory", DEFAULTS["agentstory"]), "extra": t.get("extra", []),
        "goto": goto, "profile": FORM, "ready": "#first_name" if "greenhouse" in u else None,
    }
    (ROOT / "fill_now.js").write_text((ROOT / "fill_template.js").read_text().replace("__CFG__", json.dumps(cfg)))
    print(f"OK {t['co']} | {t['title']}\n  resume: {rpdf}\n  cover:  {cpdf}\n  fill:   {ROOT / 'fill_now.js'} (goto {goto})")

if __name__ == "__main__":
    main()
