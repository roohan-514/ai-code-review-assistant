import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models.schemas import (
    CodeReviewRequest, PRReviewRequest, ReviewResponse,
    Issue, SecurityAlert, HealthResponse, Severity,
)
from backend.services.review_service import review_code
from backend.services.github_service import (
    parse_pr_url, fetch_pr_files_info, detect_language_from_path,
)
from backend.services.analysis_service import (
    detect_language, perform_static_analysis, calculate_complexity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Code Review Assistant",
    description="AI-powered code review with OpenAI, static analysis, and GitHub PR integration.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        model=settings.openai_model_name,
        languages_supported=len(settings.supported_languages),
    )


@app.get("/languages")
async def languages():
    return {"languages": settings.supported_languages}


@app.post("/review-code", response_model=ReviewResponse)
async def review_code_endpoint(request: CodeReviewRequest):
    try:
        language = detect_language(request.code, request.language)
        issues, sec_alerts, stats = perform_static_analysis(request.code, language)

        summary, ai_issues, ai_sec_alerts, suggestions = review_code(
            request.code, language, request.file_name
        )

        all_issues = issues + ai_issues
        all_sec = sec_alerts + ai_sec_alerts

        critical = sum(1 for i in all_issues if i.severity == Severity.critical) + sum(1 for s in all_sec if s.severity == Severity.critical)
        high = sum(1 for i in all_issues if i.severity == Severity.high) + sum(1 for s in all_sec if s.severity == Severity.high)
        medium = sum(1 for i in all_issues if i.severity == Severity.medium) + sum(1 for s in all_sec if s.severity == Severity.medium)
        low = sum(1 for i in all_issues if i.severity == Severity.low) + sum(1 for s in all_sec if s.severity == Severity.low)

        return ReviewResponse(
            summary=summary,
            total_issues=len(all_issues) + len(all_sec),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            issues=all_issues,
            security_alerts=all_sec,
            suggestions=suggestions,
            language=language,
        )
    except Exception as e:
        logger.exception("Error reviewing code")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review-pr", response_model=ReviewResponse)
async def review_pr_endpoint(request: PRReviewRequest):
    try:
        owner, repo, pr_number = parse_pr_url(request.pr_url)
        changed_files = fetch_pr_files_info(owner, repo, pr_number)

        if not changed_files:
            raise HTTPException(status_code=404, detail="No changed files found in PR.")

        combined_diff = ""
        analyzed_files = []
        all_issues = []
        all_sec = []
        all_suggestions = []
        detected_languages = set()
        total_summary_parts = []

        for f in changed_files:
            path = f["file_path"]
            lang = detect_language_from_path(path)
            detected_languages.add(lang)
            analyzed_files.append(f"{path} ({lang})")
            diff_content = f["diff"]

            combined_diff += f"\n--- {path} ---\n{diff_content}\n"

            issues, sec_alerts, stats = perform_static_analysis(diff_content, lang)
            all_issues.extend(issues)
            all_sec.extend(sec_alerts)

        primary_lang = detected_languages.pop() if detected_languages else "unknown"

        if combined_diff:
            summary, ai_issues, ai_sec_alerts, suggestions = review_code(
                combined_diff, primary_lang, f"PR #{pr_number}"
            )
            all_issues.extend(ai_issues)
            all_sec.extend(ai_sec_alerts)
            all_suggestions = suggestions
        else:
            summary = "No code changes to analyze."
            all_suggestions = []

        critical = sum(1 for i in all_issues if i.severity == Severity.critical) + sum(1 for s in all_sec if s.severity == Severity.critical)
        high = sum(1 for i in all_issues if i.severity == Severity.high) + sum(1 for s in all_sec if s.severity == Severity.high)
        medium = sum(1 for i in all_issues if i.severity == Severity.medium) + sum(1 for s in all_sec if s.severity == Severity.medium)
        low = sum(1 for i in all_issues if i.severity == Severity.low) + sum(1 for s in all_sec if s.severity == Severity.low)

        return ReviewResponse(
            summary=summary,
            total_issues=len(all_issues) + len(all_sec),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            issues=all_issues,
            security_alerts=all_sec,
            suggestions=all_suggestions,
            language=primary_lang,
            analyzed_files=analyzed_files,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error reviewing PR")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
