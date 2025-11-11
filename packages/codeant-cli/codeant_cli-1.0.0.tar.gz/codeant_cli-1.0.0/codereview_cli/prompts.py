SYSTEM_PROMPT = (
    "You are a senior code reviewer. Return concise, actionable findings.\n"
    "Only include real issues. Do not invent lines.\n"
    "Output must be JSON with fields: file, line, severity (HIGH|MEDIUM|LOW), "
    "issue, suggestion."
)

USER_PROMPT_TEMPLATE = """\
Review the following file. Consider security, robustness, and maintainability.

FILE_PATH: {path}

CONTENT: {content}

Return JSON list only.
"""
