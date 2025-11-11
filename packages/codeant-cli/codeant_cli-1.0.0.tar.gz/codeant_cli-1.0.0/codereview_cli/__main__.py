import typer
from rich.console import Console
from codereview_cli.review import run_review
from codereview_cli.config import load_config

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def init():
    """
    Create a starter codereview.yml in the current directory.
    """
    sample = """\
rules:
  - prohibit_hardcoded_secrets: true
severity_gate:
  block_on: ["HIGH"]
privacy:
  mode: "remote"   # remote|local
language: ["java"] # extensions inferred: .java
"""
    with open("codereview.yml", "w", encoding="utf-8") as f:
        f.write(sample)
    console.print("[green]Created codereview.yml[/]")

@app.command()
def review(
    ext: str = typer.Option(".java", help="File extension to include (e.g. .java)"),
    server: str = typer.Option("", help="(Optional) review API server URL"),
    model: str = typer.Option("gpt-4o", help="Model name (placeholder for now)"),
    output: str = typer.Option("report.md", help="Markdown report path"),
    json_out: str = typer.Option("report.json", help="JSON report path"),
    diff_base: str = typer.Option("origin/main", help="Base ref for git diff"),
):
    """
    Run an AI-assisted review on changed files and write reports.
    """
    cfg = load_config("codereview.yml")
    run_review(cfg, ext=ext, model=model, server=server,
               md_path=output, json_path=json_out, diff_base=diff_base)

if __name__ == "__main__":
    app()
