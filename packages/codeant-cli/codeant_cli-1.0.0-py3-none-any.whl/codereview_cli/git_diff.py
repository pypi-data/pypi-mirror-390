import subprocess
from typing import List

def changed_files(diff_base: str) -> List[str]:
    # Compare base...HEAD for a PR-like diff
    cmd = ["git", "diff", "--name-only", f"{diff_base}...HEAD"]
    try:
        out = subprocess.check_output(cmd, encoding="utf-8")
        files = [line.strip() for line in out.splitlines() if line.strip()]
        return files
    except subprocess.CalledProcessError:
        return []
