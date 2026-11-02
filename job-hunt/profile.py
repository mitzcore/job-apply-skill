"""YOUR PROFILE: the only file you need to edit.

Everything personal lives here: contact info, form answers, resume content, default stories.
resume.py, prep.py and fill_template.js all read from it. Replace every <...> placeholder.
Only put TRUE claims here; the agent is told never to claim anything not in this file
and in ~/.claude/skills/apply-jobs/references/profile.md.
"""

NAME = "Jane Doe"                      # as it should appear on the resume
FILE_PREFIX = NAME.replace(" ", "_")   # PDFs are named e.g. Jane_Doe_Resume.pdf
CONTACT = "New York, NY · (555) 555-5555 · jane@example.com · github.com/janedoe"

# Answers used by the ATS form filler (fill_template.js)
FORM = {
    "first": "Jane", "last": "Doe", "full": NAME,
    "email": "jane@example.com", "phone": "(555) 555-5555",
    "linkedin": "https://www.linkedin.com/in/janedoe", "github": "https://github.com/janedoe",
    "city": "New York, NY",                 # free-text "current location"
    "city_search": "New York",              # typed into location autocompletes
    "salary": "$180,000", "years": "10", "hear": "DreamWork job board",
    "notice": "2 weeks notice",
    "office_regex": "new york|nyc|manhattan",  # preferred office option
    "relocation": "Based in New York; no relocation needed.",
    "current_company": "<Current Company>", "current_title": "<Current Title>",
    "education_regex": "bachelor|bs/ba|b\\.s",  # option to pick in education dropdowns
    "education_text": "Bachelor's degree (Computer Science)",
    # Work authorization. Set these to match YOUR situation exactly.
    "needs_sponsorship": False,
    "sponsorship_text": "No",               # e.g. "Yes - will require H-1B transfer sponsorship"
    "visa_text": "US citizen",              # e.g. "Currently on H-1B (valid through ...); will require H-1B transfer."
}

# --- Resume content ---
# Expertise pillars: id -> (title, one-line proof). Tailor JSONs pick and reorder these by id.
PILLARS = {
    "k8s": ("Kubernetes at Scale", "<one-line proof with a concrete number>"),
    "cicd": ("CI/CD & GitOps", "<one-line proof>"),
    "iac": ("Infrastructure Automation", "<one-line proof>"),
    "cost": ("Cost & Efficiency Engineering", "<one-line proof>"),
    "sec": ("Cloud Security & Governance", "<one-line proof>"),
    "obs": ("Observability & Reliability", "<one-line proof>"),
    "llm": ("LLM Platforms", "<one-line proof>"),
    "data": ("Data Pipelines", "<one-line proof>"),
    "lead": ("Technical Leadership", "<one-line proof>"),
    "dev": ("Developer Experience", "<one-line proof>"),
}

# Numbers strip under the summary: (big number, label). 3-4 entries.
NUMBERS = [("20+", "production clusters"), ("50+", "cloud accounts"), ("10 yrs", "production infrastructure")]

# EXPERIENCE[0] is your current role; tailor JSONs can override its lead/bullets
# with "current_lead" / "current_bullets".
EXPERIENCE = [
    {"title": "<Current Title>", "co": "<Current Company>", "loc": "New York, NY",
     "dates": "Jan 2020 – Present",
     "lead": "<one-line summary of the role>",
     "bullets": ["<achievement 1>", "<achievement 2>", "<achievement 3>"]},
    {"title": "<Previous Title>", "co": "<Previous Company>", "loc": "<City>",
     "dates": "2016 – 2019", "lead": "",
     "bullets": ["<achievement 1>", "<achievement 2>"]},
]
EARLIER = "<Older Title>, <Company>, 2012 – 2016"
EDUCATION = "<Degree>, <School>"

MASTER = {
    "slug": "Master",
    "headline": "<Your Headline, e.g. Senior Platform Engineer>",
    "tagline": "<phrase> · <phrase> · <phrase>",
    "summary": "<About 3 lines: what you do, your hard numbers, your point of view.>",
    "pillars": list(PILLARS),  # all pillars in default order
    "skills": "<Tool> · <Tool> · <Tool>",
}

# --- Default free-text answers and cover letter (tailor JSONs can override each) ---
DEFAULTS = {
    "story": "<A 'tell us about a time' story: problem, what you did, result.>",
    "agentstory": "<An AI / automation project you built, if relevant.>",
    "looking": "<What you are looking for in your next role, and what you want to avoid.>",
    "cover_proof": [
        "<Paragraph 1 of proof: biggest relevant achievement.>",
        "<Paragraph 2 of proof.>",
        "<Paragraph 3 of proof.>",
    ],
    "cover_close": "I am based in New York and would welcome a conversation about where I can help {co} most.",
}
