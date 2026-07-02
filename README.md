# AI Code Review Assistant

![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai)
![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

An AI-powered code review assistant that analyzes code quality, finds bugs, detects security vulnerabilities, and suggests improvements. Integrates with GitHub Pull Requests for automated reviews.

---

## Features

- **AI-Powered Code Review** - Leverages OpenAI GPT-4o to analyze code with deep contextual understanding
- **GitHub PR Integration** - Review any GitHub pull request by URL, with per-file analysis
- **Security Vulnerability Detection** - Identifies hardcoded secrets, SQL injection, XSS, command injection, and more
- **Multi-Language Support** - Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP, SQL, HTML, CSS, and more
- **Static Analysis** - Built-in pattern-based security scanning as fallback
- **Interactive UI** - Modern React frontend with severity badges, categorized results, and detailed issue exploration
- **Docker Deployment** - One-command deployment with Docker Compose

## Tech Stack

| Component    | Technology                                     |
|-------------|------------------------------------------------|
| Backend     | Python 3.11, FastAPI, OpenAI API, HTTPX        |
| Frontend    | React 18, React Router, Tailwind CSS, Vite     |
| AI          | OpenAI GPT-4o (configurable)                   |
| Analysis    | Static pattern analysis + AI-powered review    |
| Deployment  | Docker, Docker Compose                         |

## How It Works

```
User Input (Code or PR URL)
       |
       v
[FastAPI Backend]
       |
       +---> [Static Analysis] ---> Pattern matching, complexity metrics
       |
       +---> [GitHub Service] ---> Fetch PR diff, extract changed files
       |
       +---> [OpenAI Review] ---> Structured analysis with retry logic
       |
       v
[Structured Review Response]
       |
       v
[React Frontend] ---> Tabbed results: Issues, Security, Suggestions
```

## Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/roohan-514/ai-code-review-assistant.git
cd ai-code-review-assistant

# 2. Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and add your OpenAI API key

# 3. Run with Docker Compose
docker-compose up --build
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`.

## Manual Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the server
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Variables

| Variable              | Required | Default    | Description                        |
|----------------------|----------|------------|------------------------------------|
| `OPENAI_API_KEY`     | Yes      | -          | OpenAI API key                     |
| `OPENAI_MODEL_NAME`  | No       | `gpt-4o`   | OpenAI model name                  |
| `OPENAI_MAX_TOKENS`  | No       | `4096`     | Maximum tokens for response        |
| `OPENAI_TEMPERATURE` | No       | `0.3`      | Response creativity (0-1)          |
| `GITHUB_TOKEN`       | No       | -          | GitHub token (for private repos)   |
| `REVIEW_MAX_RETRIES` | No       | `3`        | Max retries for OpenAI calls       |
| `HOST`               | No       | `0.0.0.0`  | Backend host                       |
| `PORT`               | No       | `8000`     | Backend port                       |

## API Documentation

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "model": "gpt-4o",
  "languages_supported": 19
}
```

### Get Supported Languages

```http
GET /languages
```

Response:
```json
{
  "languages": ["python", "javascript", "typescript", ...]
}
```

### Review Code Snippet

```http
POST /review-code
Content-Type: application/json

{
  "code": "def add(a, b):\n    return a + b",
  "language": "python",
  "file_name": "math_utils.py"
}
```

### Review GitHub Pull Request

```http
POST /review-pr
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/42"
}
```

### Review Response Schema

```json
{
  "summary": "Overall assessment of the code.",
  "total_issues": 5,
  "critical_count": 1,
  "high_count": 2,
  "medium_count": 1,
  "low_count": 1,
  "issues": [
    {
      "line": 15,
      "severity": "high",
      "category": "bug",
      "description": "Off-by-one error in range()",
      "suggestion": "Use range(len(arr)) instead of range(len(arr) + 1)",
      "code_context": "for i in range(len(arr) + 1):"
    }
  ],
  "security_alerts": [
    {
      "line": 42,
      "severity": "critical",
      "vulnerability_type": "sql_injection",
      "description": "Possible SQL injection vulnerability",
      "impact": "Unauthorized database access",
      "recommendation": "Use parameterized queries",
      "code_context": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_input}\")"
    }
  ],
  "suggestions": [
    "Add type hints for better code documentation",
    "Consider using dataclasses for data containers"
  ],
  "language": "python",
  "analyzed_files": ["src/main.py (python)"]
}
```

## Usage Guide

### Reviewing a Code Snippet

1. Navigate to the **Review PR** page
2. Click **Paste Code**
3. Select the programming language
4. Paste your code
5. Click **Review Code**
6. Explore results in the Issues, Security, and Suggestions tabs

### Reviewing a GitHub Pull Request

1. Navigate to the **Review PR** page
2. Click **Review PR**
3. Enter a GitHub PR URL (e.g. `https://github.com/owner/repo/pull/42`)
4. Click **Review PR**
5. View per-file analysis and categorized results

## Supported Languages

Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP, Swift, Kotlin, Scala, HTML, CSS, SQL, Bash, YAML, JSON

## Example Review Output

When reviewing a PR, the tool produces:

- **Summary** - High-level assessment of the code changes
- **Issues Tab** - Code quality, bugs, and best practice violations with severity levels
- **Security Tab** - Vulnerability alerts with impact analysis and remediation steps
- **Suggestions Tab** - Actionable improvement recommendations

Each issue card shows:
- Severity badge (Critical/High/Medium/Low)
- Category label
- Line number
- Description
- Code context (expandable)
- Fix suggestion

## Project Structure

```
ai-code-review-assistant/
├── README.md
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── main.py                  # FastAPI entry point with routing
│   ├── config.py                # Configuration management
│   ├── services/
│   │   ├── review_service.py    # OpenAI-powered code review
│   │   ├── github_service.py    # GitHub PR integration
│   │   └── analysis_service.py  # Static analysis & security scanning
│   └── models/
│       └── schemas.py           # Pydantic data models
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── Dockerfile
│   ├── src/
│   │   ├── App.jsx              # Root component with routing
│   │   ├── App.css              # Global styles & Tailwind
│   │   ├── main.jsx             # Entry point
│   │   ├── pages/
│   │   │   ├── Home.jsx         # Landing page
│   │   │   ├── ReviewPR.jsx     # Code/PR review page
│   │   │   └── History.jsx      # Review history
│   │   ├── components/
│   │   │   ├── Navbar.jsx       # Navigation
│   │   │   ├── CodeInput.jsx    # Code editor area
│   │   │   ├── ReviewResult.jsx # Results display
│   │   │   ├── IssueCard.jsx    # Issue display card
│   │   │   └── SecurityAlert.jsx # Security alert card
│   │   └── services/
│   │       └── api.js           # API client
│   └── public/
└── tests/
    └── test_backend.py          # Backend test suite
```

## Docker Deployment

### Production Deployment

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

Create `backend/.env` with your configuration:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_NAME=gpt-4o
GITHUB_TOKEN=ghp_your-token-here
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT
