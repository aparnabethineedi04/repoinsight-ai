
# RepoInsight AI 🔍

**An AI-inspired GitHub repository analysis tool built with Python and FastAPI.**

RepoInsight AI helps developers explore public GitHub repositories by analyzing repository metadata, README documentation, project structure, and Python code quality through a simple REST API.

## ✨ Features

- **Repository Analyzer:** Retrieves repository descriptions, stars, forks, open issues, default branch, and programming-language statistics.
- **README Analyzer:** Extracts README headings, counts words and lines, detects common documentation sections, and provides a preview.
- **Project Structure Analyzer:** Lists root-level files and folders and identifies important project files.
- **Python Code Quality Analyzer:** Uses Ruff to detect Python code-quality issues and reports rule codes, messages, line numbers, column numbers, and issue counts.
- **Health Check:** Provides an endpoint to verify that the API is running.

## 🛠️ Tech Stack

- Python
- FastAPI
- Uvicorn
- HTTPX
- Ruff
- Git and GitHub

## 📋 Prerequisites

- Python 3.11 or newer recommended
- Git
- Internet connection for public GitHub repository analysis

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/aparnabethineedi04/repoinsight-ai.git
cd repoinsight-ai
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install fastapi "uvicorn[standard]" httpx ruff
```

### 4. Start the API server

```bash
python -m uvicorn main:app --reload
```

## 📖 API Documentation

Once the server is running, open:

- **Interactive Swagger UI:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome or API status |
| GET | `/health` | Checks API health |
| GET | `/analyze/{owner}/{repo}` | Analyzes GitHub repository metadata |
| GET | `/readme/{owner}/{repo}` | Analyzes README documentation |
| GET | `/structure/{owner}/{repo}` | Inspects repository root structure |
| POST | `/quality/python` | Checks submitted Python code with Ruff |

## 🧪 Example Requests

### Analyze a repository

```text
GET /analyze/fastapi/fastapi
```

Returns repository metadata, including stars, forks, open issues, and languages.

### Analyze a README

```text
GET /readme/fastapi/fastapi
```

Returns README headings, word and line counts, detected sections, and a preview.

### Inspect project structure

```text
GET /structure/fastapi/fastapi
```

Returns root-level files, folders, and detected project files.

### Check Python code quality

Send a POST request to `/quality/python` with this JSON body:

```json
{
  "code": "import os\nx=1\nprint(x)\n"
}
```

Example response:

```json
{
  "issue_count": 2,
  "error_count": 1,
  "warning_count": 1,
  "issues": [
    {
      "code": "I001",
      "message": "Import block is un-sorted or un-formatted",
      "line": 1,
      "column": 1
    },
    {
      "code": "F401",
      "message": "`os` imported but unused",
      "line": 1,
      "column": 8
    }
  ]
}
```

*The example illustrates the current project's severity-counting logic; classifications are based on Ruff rule-code prefixes.*

## 📁 Project Structure

```text
repoinsight-ai/
├── main.py
├── quality_analyzer.py
├── README.md
└── .gitignore
```

## 🔮 Future Improvements

- Add an interactive web dashboard.
- Generate downloadable analysis reports.
- Improve README quality scoring.
- Add automated tests and continuous integration.
- Support additional code-quality analyzers.

## 👩‍💻 Author

**Likhitha Sri Aparna**

GitHub: [@aparnabethineedi04](https://github.com/aparnabethineedi04)

---

Built as a hands-on project to explore Python, REST APIs, GitHub integration, and automated code analysis.
