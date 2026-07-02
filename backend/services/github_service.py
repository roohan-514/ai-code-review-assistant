import re
import httpx
import logging
from typing import List, Dict, Tuple
from urllib.parse import urlparse

from backend.config import settings

logger = logging.getLogger(__name__)

GITHUB_RAW_URL_PATTERN = re.compile(
    r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)(/files)?"
)


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    match = GITHUB_RAW_URL_PATTERN.match(url.rstrip("/"))
    if not match:
        raise ValueError(
            "Invalid GitHub PR URL. Expected format: "
            "https://github.com/owner/repo/pull/123"
        )
    owner, repo, pr_number = match.group(1), match.group(2), int(match.group(3))
    return owner, repo, pr_number


def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    diff_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}.diff"
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    with httpx.Client(timeout=30.0) as client:
        resp = client.get(diff_url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
        return resp.text


def parse_diff(diff_text: str) -> List[Dict]:
    files = []
    current_file = None
    current_diff_lines = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file:
                files.append({
                    "file_path": current_file,
                    "diff": "\n".join(current_diff_lines),
                    "changes": _parse_hunks("\n".join(current_diff_lines)),
                })
            current_file = line.split(" b/")[-1] if " b/" in line else line.split()[-1]
            current_diff_lines = [line]
        else:
            current_diff_lines.append(line)

    if current_file:
        files.append({
            "file_path": current_file,
            "diff": "\n".join(current_diff_lines),
            "changes": _parse_hunks("\n".join(current_diff_lines)),
        })

    return files


def _parse_hunks(diff_text: str) -> List[Dict]:
    hunks = []
    for hunk_match in re.finditer(
        r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@.*?(?=(?:\n@@ |\Z))",
        diff_text,
        re.DOTALL,
    ):
        start_line = int(hunk_match.group(1))
        hunk_body = hunk_match.group(0)
        lines = []
        for line in hunk_body.split("\n")[1:]:
            if line.startswith("+") and not line.startswith("+++"):
                lines.append({"type": "addition", "content": line[1:], "line": start_line})
                start_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                lines.append({"type": "deletion", "content": line[1:]})
            elif line.startswith(" "):
                lines.append({"type": "context", "content": line[1:], "line": start_line})
                start_line += 1
        hunks.append({"start_line": int(hunk_match.group(1)), "lines": lines})
    return hunks


def detect_language_from_path(file_path: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".jsx": "javascript",
        ".ts": "typescript", ".tsx": "typescript", ".java": "java",
        ".go": "go", ".rs": "rust", ".cpp": "cpp", ".c": "c",
        ".cs": "csharp", ".rb": "ruby", ".php": "php",
        ".swift": "swift", ".kt": "kotlin", ".scala": "scala",
        ".html": "html", ".htm": "html", ".css": "css",
        ".sql": "sql", ".sh": "bash", ".bash": "bash",
        ".yaml": "yaml", ".yml": "yaml", ".json": "json",
        ".md": "markdown", ".dockerfile": "dockerfile",
    }
    _, ext = file_path.rsplit(".", 1) if "." in file_path else ("", "")
    return ext_map.get("." + ext, "unknown")


def fetch_pr_files_info(owner: str, repo: str, pr_number: int) -> List[Dict]:
    diff_text = get_pr_diff(owner, repo, pr_number)
    return parse_diff(diff_text)
