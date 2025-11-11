from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
CODELOAD_BASE = "https://codeload.github.com"


@dataclass
class RepoRef:
    owner: str
    repo: str
    branch: str = "main"

    @classmethod
    def from_env(cls) -> "RepoRef":
        repostr = os.environ.get("GETCODE_REPO", "GetSomeSleepBro/codes").strip()
        if "/" not in repostr:
            print(
                "Invalid GETCODE_REPO; expected 'owner/repo', defaulting to 'GetSomeSleepBro/codes'",
                file=sys.stderr,
            )
            repostr = "GetSomeSleepBro/codes"
        owner, repo = repostr.split("/", 1)
        branch = os.environ.get("GETCODE_BRANCH", "main").strip() or "main"
        return cls(owner=owner, repo=repo, branch=branch)


class GitHubAPIClient:
    def __init__(self, repo: Optional[RepoRef] = None, *, token: Optional[str] = None) -> None:
        self.repo = repo or RepoRef.from_env()
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN")

    def _headers(self) -> Dict[str, str]:
        h = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "getcode-cli/0.1",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _api_url(self, path: str) -> str:
        return f"{GITHUB_API}/repos/{self.repo.owner}/{self.repo.repo}/contents/{path}?ref={self.repo.branch}"

    def list_dir(self, path: str) -> List[dict]:
        url = self._api_url(path.strip("/"))
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"Path not found in repo: {path}") from e
            if e.code == 403:
                reset = e.headers.get("X-RateLimit-Reset")
                if reset:
                    try:
                        wait = max(0, int(reset) - int(time.time()))
                    except Exception:
                        wait = None
                else:
                    wait = None
                msg = "GitHub API rate limit exceeded. Set GITHUB_TOKEN to increase limits."
                if wait:
                    msg += f" Retry in ~{wait}s."
                raise RuntimeError(msg) from e
            raise
        if isinstance(data, dict) and data.get("type") == "file":
            # When a file path is provided, GitHub returns a single object
            return [data]
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected response for path {path!r}")
        return data

    def get_raw(self, content_obj: dict) -> bytes:
        # content_obj should have 'download_url'; fall back to RAW_BASE
        url = content_obj.get("download_url")
        if not url:
            # Build raw URL: /owner/repo/branch/path
            path = content_obj.get("path")
            if not path:
                raise ValueError("Content object must include 'download_url' or 'path'")
            url = f"{RAW_BASE}/{self.repo.owner}/{self.repo.repo}/{self.repo.branch}/{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "getcode-cli/0.1"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()


# Snapshot fallback using a ZIP archive from codeload
import atexit
import shutil
import tempfile
import zipfile


class SnapshotClient:
    def __init__(self, repo: Optional[RepoRef] = None) -> None:
        self.repo = repo or RepoRef.from_env()
        self._tmpdir: Optional[str] = None
        self._root: Optional[str] = None
        self._cleanup_registered = False

    def _register_cleanup(self):
        if not self._cleanup_registered:
            atexit.register(self._cleanup)
            self._cleanup_registered = True

    def _cleanup(self):
        try:
            if self._tmpdir and os.path.isdir(self._tmpdir):
                shutil.rmtree(self._tmpdir, ignore_errors=True)
        finally:
            self._tmpdir = None
            self._root = None

    def _ensure_snapshot(self):
        if self._root and os.path.isdir(self._root):
            return
        self._register_cleanup()
        self._tmpdir = tempfile.mkdtemp(prefix="getcode-snap-")
        zip_path = os.path.join(self._tmpdir, "repo.zip")
        url = f"{CODELOAD_BASE}/{self.repo.owner}/{self.repo.repo}/zip/refs/heads/{self.repo.branch}"
        req = urllib.request.Request(url, headers={"User-Agent": "getcode-cli/0.1"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(zip_path, "wb") as f:
            shutil.copyfileobj(resp, f)
        with zipfile.ZipFile(zip_path) as zf:
            # safe extract
            for member in zf.infolist():
                member_name = member.filename
                if os.path.isabs(member_name) or ".." in member_name.replace("\\", "/").split("/"):
                    continue
                zf.extract(member, self._tmpdir)
        # find root directory (first folder inside tmpdir)
        entries = [os.path.join(self._tmpdir, e) for e in os.listdir(self._tmpdir)]
        dirs = [e for e in entries if os.path.isdir(e)]
        if not dirs:
            raise RuntimeError("Snapshot extraction failed: no directory found")
        # pick the longest common path dir (usually repo-branch)
        self._root = max(dirs, key=lambda p: len(os.listdir(p)))

    def _abs(self, path: str) -> str:
        self._ensure_snapshot()
        rel = path.strip("/")
        return os.path.join(self._root, rel) if rel else self._root

    def list_dir(self, path: str) -> List[dict]:
        base = self._abs(path)
        if os.path.isfile(base):
            name = os.path.basename(base)
            return [{"name": name, "path": path.strip("/"), "type": "file"}]
        if not os.path.isdir(base):
            raise FileNotFoundError(f"Path not found in snapshot: {path}")
        out: List[dict] = []
        for name in sorted(os.listdir(base)):
            if name.startswith("."):
                continue
            ap = os.path.join(base, name)
            rel = os.path.relpath(ap, self._root).replace(os.sep, "/")
            out.append({
                "name": name,
                "path": rel,
                "type": "dir" if os.path.isdir(ap) else "file",
            })
        return out

    def get_raw(self, content_obj: dict) -> bytes:
        path = content_obj.get("path")
        if not path:
            raise ValueError("SnapshotClient requires 'path' in content object")
        ap = self._abs(path)
        if not os.path.isfile(ap):
            raise FileNotFoundError(f"File not found in snapshot: {path}")
        with open(ap, "rb") as f:
            return f.read()


class GitHubClient:
    """Resilient client: GitHub API first, then snapshot fallback (zip download)."""

    def __init__(self, repo: Optional[RepoRef] = None, *, token: Optional[str] = None) -> None:
        self.api = GitHubAPIClient(repo, token=token)
        self.snapshot = SnapshotClient(self.api.repo)

    @property
    def repo(self) -> RepoRef:
        return self.api.repo

    def list_dir(self, path: str) -> List[dict]:
        try:
            return self.api.list_dir(path)
        except Exception:
            # Fallback to snapshot on any API failure (rate limit, network, etc.)
            return self.snapshot.list_dir(path)

    def get_raw(self, content_obj: dict) -> bytes:
        # Prefer API download when available, else snapshot by path
        try:
            if content_obj.get("download_url"):
                return self.api.get_raw(content_obj)
        except Exception:
            pass
        # fallback using snapshot with path
        return self.snapshot.get_raw(content_obj)
