from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Category(str, Enum):
    code_quality = "code_quality"
    bug = "bug"
    security = "security"
    performance = "performance"
    best_practice = "best_practice"


class Issue(BaseModel):
    line: Optional[int] = None
    severity: Severity
    category: Category
    description: str
    suggestion: str
    code_context: Optional[str] = None


class SecurityAlert(BaseModel):
    line: Optional[int] = None
    severity: Severity
    vulnerability_type: str
    description: str
    impact: str
    recommendation: str
    code_context: Optional[str] = None


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="The code snippet to review")
    language: str = Field(default="python", description="Programming language of the code")
    file_name: Optional[str] = Field(default=None, description="Optional file name for context")


class PRReviewRequest(BaseModel):
    pr_url: str = Field(..., description="Full GitHub pull request URL")


class ReviewResponse(BaseModel):
    summary: str
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    issues: List[Issue]
    security_alerts: List[SecurityAlert]
    suggestions: List[str]
    language: str
    analyzed_files: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str
    model: str
    languages_supported: int
