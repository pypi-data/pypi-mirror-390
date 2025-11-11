from pathlib import Path
from typing import List
from rich.console import Console
from codereview_cli.config import Config
from codereview_cli.git_diff import changed_files
from codereview_cli.llm import analyze_files_with_llm
from codereview_cli.report import write_markdown, write_json

console = Console()

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def run_review(cfg: Config, ext: str, model: str, server: str,
               md_path: str, json_path: str, diff_base: str):
    console.rule("[bold cyan]codereview-cli")
    files = [f for f in changed_files(diff_base) if f.endswith(ext)]
    if not files:
        console.print("[yellow]No matching changed files. Skipping.[/]")
        write_markdown([], md_path)
        write_json([], json_path)
        return

    console.print(f"[green]Reviewing {len(files)} file(s)[/]")
    payload = [{"path": f, "content": _read(Path(f))} for f in files]

    # MVP: ignore server; call local analyzer stub.
    findings = analyze_files_with_llm(payload, model=model)

    write_markdown(findings, md_path)
    write_json(findings, json_path)
    console.print(f"[cyan]Wrote {md_path} and {json_path}[/]")

    # Optional: fail gate if configured
    gate = set(map(str.upper, cfg.severity_gate.block_on))
    if any(f["severity"].upper() in gate for f in findings):
        console.print("[red]Blocking due to severity gate.[/]")
        raise SystemExit(1)
