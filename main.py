
from fastapi import FastAPI, HTTPException
import httpx
from quality_analyzer import analyze_python_code
import subprocess

app = FastAPI(
    title="RepoInsight AI",
    description="A GitHub Repository Analyzer",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to RepoInsight AI!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/analyze/{owner}/{repo}")
async def analyze_repository(owner: str, repo: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RepoInsight-AI",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers,
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Repository not found or not public.",
                )

            if response.status_code == 403:
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit may have been reached.",
                )

            response.raise_for_status()
            data = response.json()

            language_response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/languages",
                headers=headers,
            )
            language_response.raise_for_status()
            languages = language_response.json()

        except HTTPException:
            raise
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="GitHub request timed out. Please try again.",
            )
        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=502,
                detail="GitHub returned an unsuccessful response.",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Could not connect to GitHub. Check your internet.",
            )

    return {
        "repository": data["full_name"],
        "description": data["description"],
        "url": data["html_url"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "default_branch": data["default_branch"],
        "languages": languages,
    }

@app.get("/readme/{owner}/{repo}")
async def analyze_readme(owner: str, repo: str):
    """Analyze the README of a public GitHub repository."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RepoInsight-AI",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="README not found or repository is not public.",
                )

            if response.status_code == 403:
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit may have been reached.",
                )

            response.raise_for_status()

            # GitHub returns README content when requested as raw text.
            readme_response = await client.get(
                url,
                headers={
                    **headers,
                    "Accept": "application/vnd.github.raw+json",
                },
            )
            readme_response.raise_for_status()
            content = readme_response.text

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="GitHub request timed out. Please try again.",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="GitHub returned an unsuccessful response.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub. Check your internet.",
        )

    lines = content.splitlines()

    headings = [
        line.lstrip("#").strip()
        for line in lines
        if line.startswith("#")
    ]

    word_count = len(content.split())

    sections_to_check = [
        "installation",
        "usage",
        "features",
        "contributing",
        "license",
    ]

    content_lower = content.lower()

    sections_found = [
        section
        for section in sections_to_check
        if section in content_lower
    ]

    return {
        "repository": f"{owner}/{repo}",
        "readme_found": True,
        "word_count": word_count,
        "line_count": len(lines),
        "headings": headings,
        "sections_found": sections_found,
        "readme_preview": content[:1000],
    }

@app.get("/structure/{owner}/{repo}")
async def analyze_structure(owner: str, repo: str):
    """Analyze the file and folder structure of a public GitHub repository."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RepoInsight-AI",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Repository or directory not found.",
                )

            if response.status_code == 403:
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit may have been reached.",
                )

            response.raise_for_status()
            items = response.json()

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="GitHub request timed out. Please try again.",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="GitHub returned an unsuccessful response.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub. Check your internet.",
        )

    files = [
        item["name"] for item in items
        if item["type"] == "file"
    ]

    folders = [
        item["name"] for item in items
        if item["type"] == "dir"
    ]

    important_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "Dockerfile",
        ".gitignore",
        "tests",
    ]

    available_names = {item["name"].lower() for item in items}

    detected_files = [
        name for name in important_files
        if name.lower() in available_names
    ]

    return {
        "repository": f"{owner}/{repo}",
        "total_items": len(items),
        "file_count": len(files),
        "folder_count": len(folders),
        "files": files,
        "folders": folders,
        "important_project_files_found": detected_files,
    }

from pydantic import BaseModel


class CodeSample(BaseModel):
    code: str


@app.post("/quality/python")
def check_python_quality(sample: CodeSample):
    try:
        return analyze_python_code(sample.code)
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Code analysis timed out.",
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
