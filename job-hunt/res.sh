#!/bin/sh
f=$(ls -t $HOME/.claude/projects/*/*/tool-results/mcp-playwright-extension-browser_run_code_unsafe-*.txt | head -1)
python3 - "$f" <<'PY'
import sys,json
s=open(sys.argv[1]).read(); s=s[:s.find('### Ran Playwright')]
s=s[s.find('"'):s.rfind('"')+1]
try:
    d=json.loads(json.loads(s))
    print('FILLED',len(d['filled']));[print(' -',x[:120]) for x in d['filled']]
    print('SKIPPED');[print(' -',x[:240]) for x in d['skipped']]
except Exception as e: print(s[:3000])
PY
