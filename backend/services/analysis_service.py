import re
from typing import Tuple, List, Dict

from backend.models.schemas import Issue, SecurityAlert, Severity, Category


HARDCODED_SECRET_PATTERNS = [
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"](?!your_|placeholder|None|null)[^'\"]+['\"]", "hardcoded_password"),
    (r"(?i)(api_key|api-key|apikey|secret|token|credential)\s*[=:]\s*['\"](?!your_|placeholder|None|null)[^'\"]+['\"]", "hardcoded_secret"),
    (r"(?i)(private_key|privatekey|access_key)\s*[=:]\s*['\"](?!your_|placeholder|None|null)[^'\"]+['\"]", "hardcoded_credential"),
]

SQL_INJECTION_PATTERNS = [
    r"execute\s*\(\s*['\"].*?(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER).*?['\"]\s*[+%]",
    r"cursor\.execute\s*\(\s*['\"].*?\{[^}]*\}.*?['\"]",
    r"raw\(.*?\{[^}]*\}",
    r"\.query\(\s*['\"].*?\%.*?['\"].*?%",
]

XSS_PATTERNS = [
    r"innerHTML\s*=",
    r"outerHTML\s*=",
    r"document\.write\s*\(",
    r"dangerouslySetInnerHTML",
    r"v-html\s*=",
]

COMMAND_INJECTION_PATTERNS = [
    r"os\.system\s*\(.*?[+%]",
    r"subprocess\.(call|Popen|run)\s*\(.*?shell\s*=\s*True",
    r"exec\s*\(.*?[+%]",
    r"eval\s*\(.*?[+%]",
]


def _check_line(line: str, line_num: int, patterns: List[Tuple[str, str]], vuln_type: str) -> List[SecurityAlert]:
    alerts = []
    for pattern, label in patterns:
        if re.search(pattern, line):
            alerts.append(SecurityAlert(
                line=line_num,
                severity=Severity.high if "critical" not in label else Severity.critical,
                vulnerability_type=label,
                description=f"Potential {vuln_type} detected: {label}",
                impact=line[:100],
                recommendation="Review and address this security concern immediately.",
                code_context=line.strip(),
            ))
    return alerts


def perform_static_analysis(code: str, language: str) -> Tuple[List[Issue], List[SecurityAlert], Dict]:
    lines = code.split("\n")
    issues = []
    security_alerts = []
    stats = {
        "total_lines": len(lines),
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
    }

    comment_prefixes = ("#", "//", "--", ";")
    multi_line_comment = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if not stripped:
            stats["blank_lines"] += 1
            continue

        if language in ("python",) and stripped.startswith('"""'):
            multi_line_comment = not multi_line_comment
            stats["comment_lines"] += 1
            continue
        if multi_line_comment:
            stats["comment_lines"] += 1
            continue

        if language in ("html", "css") and ("/*" in stripped or "<!--" in stripped):
            multi_line_comment = True
            stats["comment_lines"] += 1
            continue
        if multi_line_comment:
            stats["comment_lines"] += 1
            if "*/" in stripped or "-->" in stripped:
                multi_line_comment = False
            continue

        if any(stripped.startswith(p) for p in comment_prefixes):
            stats["comment_lines"] += 1
            continue

        stats["code_lines"] += 1

        if language in ("python",) and len(stripped) > 120:
            issues.append(Issue(
                line=i, severity=Severity.low, category=Category.code_quality,
                description=f"Line {i} exceeds 120 characters ({len(stripped)}).",
                suggestion="Break this line into multiple lines.",
                code_context=stripped[:80],
            ))

        complexity = stripped.count("if ") + stripped.count("for ") + stripped.count("while ") + stripped.count("except ")
        if complexity > 3:
            pass

        alerts = _check_line(stripped, i, [(p, "hardcoded_secret") for p, _ in HARDCODED_SECRET_PATTERNS], "hardcoded secret")
        security_alerts.extend(alerts)

        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, stripped):
                security_alerts.append(SecurityAlert(
                    line=i, severity=Severity.critical,
                    vulnerability_type="sql_injection",
                    description="Possible SQL injection vulnerability.",
                    impact="Unauthorized database access or data manipulation.",
                    recommendation="Use parameterized queries or an ORM.",
                    code_context=stripped,
                ))

        for pattern in XSS_PATTERNS:
            if re.search(pattern, stripped):
                security_alerts.append(SecurityAlert(
                    line=i, severity=Severity.high,
                    vulnerability_type="xss",
                    description="Potential XSS vulnerability.",
                    impact="Cross-site scripting attack on users.",
                    recommendation="Use safe DOM APIs instead (textContent, etc.).",
                    code_context=stripped,
                ))

        for pattern in COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, stripped):
                security_alerts.append(SecurityAlert(
                    line=i, severity=Severity.critical,
                    vulnerability_type="command_injection",
                    description="Potential command injection vulnerability.",
                    impact="Remote code execution.",
                    recommendation="Avoid shell=True; use safe APIs with argument lists.",
                    code_context=stripped,
                ))

    return issues, security_alerts, stats


def detect_language(code: str, hint: str = None) -> str:
    if hint and hint.lower() in (
        "python", "javascript", "typescript", "java", "go", "rust",
        "cpp", "csharp", "ruby", "php", "swift", "kotlin", "scala",
        "html", "css", "sql", "bash", "yaml", "json"
    ):
        return hint.lower()

    if re.search(r'^\s*(import |from |def |class |print\(|if __name__)', code, re.MULTILINE):
        return "python"
    if re.search(r'^\s*(const |let |var |import |export |function |=>|require\(|console\.)', code, re.MULTILINE):
        return "javascript"
    if re.search(r'^\s*(interface |type |enum |const |let |:\s*(string|number|boolean))', code, re.MULTILINE):
        return "typescript"
    if re.search(r'^\s*(public|private|class |import java\.|@)',
                 code, re.MULTILINE):
        return "java"
    if re.search(r'^\s*(func |package |import "fmt")', code, re.MULTILINE):
        return "go"
    if re.search(r'<!DOCTYPE html|<html|<head|<body|<div|<script', code, re.MULTILINE):
        return "html"
    if re.search(r'^\s*(SELECT |INSERT |UPDATE |DELETE |CREATE |ALTER )', code, re.MULTILINE | re.IGNORECASE):
        return "sql"

    return "python"


def calculate_complexity(code: str) -> Dict:
    lines = code.split("\n")
    branching = 0
    loops = 0
    functions = 0
    classes = 0

    for line in lines:
        stripped = line.strip()
        if any(kw in stripped for kw in ("if ", "elif ", "else:", "? ")):
            branching += 1
        if any(kw in stripped for kw in ("for ", "while ")):
            loops += 1
        if stripped.startswith("def ") or stripped.startswith("function ") or stripped.startswith("func "):
            functions += 1
        if stripped.startswith("class "):
            classes += 1

    return {
        "branching": branching,
        "loops": loops,
        "functions": functions,
        "classes": classes,
        "estimated_cyclomatic": max(1, branching + loops + 1),
    }
