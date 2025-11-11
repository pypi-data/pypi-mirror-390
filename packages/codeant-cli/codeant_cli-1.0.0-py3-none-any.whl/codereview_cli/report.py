from typing import List, Dict
from pathlib import Path
import json

SEVERITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}

def write_json(findings: List[Dict], path: str):
    Path(path).write_text(json.dumps({"findings": findings}, indent=2), encoding="utf-8")

def write_markdown(findings: List[Dict], path: str):
    lines = ["### 🤖 AI Code Review", ""]
    if not findings:
        lines += ["No issues found. ✅"]
    else:
        for f in findings:
            sev = f.get("severity", "LOW").upper()
            em = SEVERITY_EMOJI.get(sev, "🟡")
            lines.append(f"- {em} **{sev}** — {f['issue']} (`{f['file']}:{f.get('line', '-')}`)")
            if sug := f.get("suggestion"):
                lines.append(f"  - _Suggestion:_ {sug}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
