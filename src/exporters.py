import json
from datetime import datetime, timezone


def summary_to_markdown(summary: str, title: str = "PDF Summary") -> str:
    return f"# {title}\n\n{summary.strip()}\n"


def summary_to_json(summary: str, source_file: str) -> str:
    payload = {
        "source_file": source_file,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }

    return json.dumps(payload, indent=2)

print("hello world")
