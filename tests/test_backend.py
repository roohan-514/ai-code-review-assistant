import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.schemas import Severity, Category
from backend.services.analysis_service import (
    perform_static_analysis, detect_language, calculate_complexity,
    HARDCODED_SECRET_PATTERNS, SQL_INJECTION_PATTERNS, XSS_PATTERNS,
)
from backend.services.github_service import parse_pr_url, detect_language_from_path
from backend.services.review_service import _fallback_static_analysis

client = TestClient(app)


class TestHealthEndpoint:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert data["languages_supported"] > 0

    def test_languages(self):
        resp = client.get("/languages")
        assert resp.status_code == 200
        data = resp.json()
        assert "languages" in data
        assert len(data["languages"]) > 0


class TestCodeReviewEndpoint:
    def test_review_valid_code(self):
        payload = {"code": "def add(a, b):\n    return a + b", "language": "python"}
        resp = client.post("/review-code", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "issues" in data
        assert "security_alerts" in data
        assert "suggestions" in data

    def test_review_empty_code(self):
        resp = client.post("/review-code", json={"code": "", "language": "python"})
        assert resp.status_code == 422

    def test_review_with_security_issue(self):
        payload = {
            "code": 'password = "supersecret123"\napi_key = "abc123def"\nresult = execute("SELECT * FROM users WHERE id = " + user_input)',
            "language": "python",
        }
        resp = client.post("/review-code", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["security_alerts"]

    def test_review_js_code(self):
        payload = {"code": "function hello() { console.log('world'); }", "language": "javascript"}
        resp = client.post("/review-code", json=payload)
        assert resp.status_code == 200


class TestGitHubParsing:
    def test_parse_pr_url_valid(self):
        owner, repo, num = parse_pr_url("https://github.com/owner/repo/pull/42")
        assert owner == "owner"
        assert repo == "repo"
        assert num == 42

    def test_parse_pr_url_with_files(self):
        owner, repo, num = parse_pr_url("https://github.com/owner/repo/pull/42/files")
        assert owner == "owner"
        assert repo == "repo"
        assert num == 42

    def test_parse_pr_url_invalid(self):
        with pytest.raises(ValueError):
            parse_pr_url("https://github.com/owner/repo/issue/1")

    def test_detect_language_from_path(self):
        assert detect_language_from_path("main.py") == "python"
        assert detect_language_from_path("app.js") == "javascript"
        assert detect_language_from_path("component.tsx") == "typescript"
        assert detect_language_from_path("unknown.xyz") == "unknown"


class TestAnalysisService:
    def test_detect_language(self):
        assert detect_language("def foo(): pass") == "python"
        assert detect_language("function foo() {}") == "javascript"
        assert detect_language("") == "python"
        assert detect_language("", hint="go") == "go"

    def test_static_analysis_normal(self):
        code = "def foo():\n    pass\n"
        issues, sec, stats = perform_static_analysis(code, "python")
        assert stats["total_lines"] == 3
        assert stats["code_lines"] == 2
        assert stats["blank_lines"] == 1

    def test_static_analysis_hardcoded_secret(self):
        code = 'password = "my_secret_key_1234"\n'
        issues, sec, stats = perform_static_analysis(code, "python")
        assert len(sec) > 0
        assert any(s.vulnerability_type == "hardcoded_secret" for s in sec)

    def test_static_analysis_sql_injection(self):
        code = 'cursor.execute("SELECT * FROM users WHERE id = " + user_input)'
        issues, sec, stats = perform_static_analysis(code, "python")
        assert len(sec) > 0
        assert any(s.vulnerability_type == "sql_injection" for s in sec)

    def test_static_analysis_xss(self):
        code = 'element.innerHTML = user_input'
        issues, sec, stats = perform_static_analysis(code, "javascript")
        assert any(s.vulnerability_type == "xss" for s in sec)

    def test_complexity_simple(self):
        result = calculate_complexity("def foo():\n    if x:\n        pass\n")
        assert result["functions"] == 1
        assert result["branching"] >= 1

    def test_complexity_loops(self):
        result = calculate_complexity("for i in range(10):\n    print(i)\nwhile True:\n    break\n")
        assert result["loops"] >= 2


class TestFallbackService:
    def test_fallback_analysis(self):
        code = "x = 1\n"
        summary, issues, sec, suggestions = _fallback_static_analysis(code, "python")
        assert isinstance(summary, str)
        assert isinstance(issues, list)
        assert isinstance(sec, list)
        assert isinstance(suggestions, list)

    def test_fallback_long_line(self):
        code = "x = " + "a" * 201 + "\n"
        summary, issues, sec, suggestions = _fallback_static_analysis(code, "python")
        assert any("long line" in i.description.lower() for i in issues)
