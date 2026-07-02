import json
import logging
from typing import List, Tuple
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.config import settings
from backend.models.schemas import Issue, SecurityAlert, Severity, Category

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert code review assistant. Analyze the provided code thoroughly and return a structured JSON response. Focus on:

1. **Code Quality Issues**: Naming conventions, code organization, duplication, complexity
2. **Bugs**: Logic errors, edge cases, type mismatches, off-by-one errors
3. **Security Vulnerabilities**: Hardcoded secrets, SQL injection, XSS, command injection, unsafe deserialization
4. **Performance Improvements**: Inefficient algorithms, unnecessary allocations, memory leaks
5. **Best Practices**: Idiomatic patterns, error handling, documentation, testing

Respond with valid JSON only (no markdown fences). Use this exact structure:
{
  "summary": "Brief overall assessment",
  "issues": [
    {
      "line": <int or null>,
      "severity": "critical" | "high" | "medium" | "low",
      "category": "code_quality" | "bug" | "security" | "performance" | "best_practice",
      "description": "Clear description of the issue",
      "suggestion": "How to fix it",
      "code_context": "Relevant code snippet if applicable"
    }
  ],
  "security_alerts": [
    {
      "line": <int or null>,
      "severity": "critical" | "high" | "medium" | "low",
      "vulnerability_type": "e.g. hardcoded_secret, sql_injection, xss",
      "description": "What vulnerability was found",
      "impact": "Potential impact of this vulnerability",
      "recommendation": "How to remediate",
      "code_context": "Relevant code snippet"
    }
  ],
  "suggestions": ["Actionable improvement suggestion 1", "..."],
  "language": "detected language"
}"""


def _parse_severity(val: str) -> Severity:
    mapping = {"critical": Severity.critical, "high": Severity.high, "medium": Severity.medium, "low": Severity.low}
    return mapping.get(val.lower(), Severity.medium)


def _parse_category(val: str) -> Category:
    mapping = {"code_quality": Category.code_quality, "bug": Category.bug, "security": Category.security, "performance": Category.performance, "best_practice": Category.best_practice}
    return mapping.get(val.lower(), Category.code_quality)


def _parse_response(response_text: str) -> dict:
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:] if lines[0].startswith("```") else lines)
        if text.endswith("```"):
            text = text[:-3].strip()
    return json.loads(text)


@retry(
    stop=stop_after_attempt(settings.review_max_retries),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
)
def _call_openai(code: str, language: str, file_name: str = None) -> dict:
    client = OpenAI(api_key=settings.openai_api_key)

    user_content = f"Language: {language}\n"
    if file_name:
        user_content += f"File: {file_name}\n"
    user_content += f"```\n{code}\n```"

    response = client.chat.completions.create(
        model=settings.openai_model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature,
        response_format={"type": "json_object"},
    )

    return _parse_response(response.choices[0].message.content)


def review_code(code: str, language: str, file_name: str = None) -> Tuple[str, List[Issue], List[SecurityAlert], List[str]]:
    if not settings.openai_api_key:
        return _fallback_static_analysis(code, language)

    try:
        result = _call_openai(code, language, file_name)
    except Exception as e:
        logger.warning(f"OpenAI review failed, falling back to static analysis: {e}")
        return _fallback_static_analysis(code, language)

    issues = []
    for i in result.get("issues", []):
        issues.append(Issue(
            line=i.get("line"),
            severity=_parse_severity(i.get("severity", "medium")),
            category=_parse_category(i.get("category", "code_quality")),
            description=i.get("description", ""),
            suggestion=i.get("suggestion", ""),
            code_context=i.get("code_context"),
        ))

    security_alerts = []
    for a in result.get("security_alerts", []):
        security_alerts.append(SecurityAlert(
            line=a.get("line"),
            severity=_parse_severity(a.get("severity", "medium")),
            vulnerability_type=a.get("vulnerability_type", "unknown"),
            description=a.get("description", ""),
            impact=a.get("impact", ""),
            recommendation=a.get("recommendation", ""),
            code_context=a.get("code_context"),
        ))

    return (
        result.get("summary", "Review completed."),
        issues,
        security_alerts,
        result.get("suggestions", []),
    )


def _fallback_static_analysis(code: str, language: str) -> Tuple[str, List[Issue], List[SecurityAlert], List[str]]:
    lines = code.split("\n")
    issues = []
    security_alerts = []
    suggestions = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "/*", "*", "\"\"\"")):
            continue

        if len(stripped) > 200:
            issues.append(Issue(
                line=i, severity=Severity.low, category=Category.code_quality,
                description=f"Very long line ({len(stripped)} chars). Consider breaking it up.",
                suggestion="Split this line into multiple lines for readability.",
                code_context=stripped[:100] + "...",
            ))

        lower = stripped.lower()
        if any(kw in lower for kw in ("password", "secret", "api_key", "api-key", "token", "credential")):
            eq_idx = stripped.find("=")
            if eq_idx != -1:
                val = stripped[eq_idx + 1:].strip().strip("\"'")
                if val and val not in ("your_", "placeholder", "none", "null", "true", "false"):
                    security_alerts.append(SecurityAlert(
                        line=i, severity=Severity.high,
                        vulnerability_type="hardcoded_secret",
                        description="Potential hardcoded secret detected.",
                        impact="Exposure of credentials in source code.",
                        recommendation="Move this to environment variables or a secret manager.",
                        code_context=stripped,
                    ))

        if "select " in lower and ("from " in lower) and not stripped.startswith(("#", "//")):
            if "?" not in stripped and "f'" not in stripped and "format(" not in stripped:
                security_alerts.append(SecurityAlert(
                    line=i, severity=Severity.critical,
                    vulnerability_type="sql_injection",
                    description="Possible SQL injection vulnerability.",
                    impact="Unauthorized data access or manipulation.",
                    recommendation="Use parameterized queries or an ORM.",
                    code_context=stripped,
                ))

        if "<script" in lower and ">" in stripped:
            security_alerts.append(SecurityAlert(
                line=i, severity=Severity.critical,
                vulnerability_type="xss",
                description="Potential XSS vulnerability.",
                impact="Cross-site scripting attack.",
                recommendation="Sanitize and escape user input.",
                code_context=stripped,
            ))

    if not issues and not security_alerts:
        suggestions.append("Consider adding input validation.")
        suggestions.append("Consider adding unit tests.")
        suggestions.append("Add error handling for edge cases.")

    summary = f"Static analysis found {len(issues)} issue(s) and {len(security_alerts)} security alert(s)."
    return summary, issues, security_alerts, suggestions
