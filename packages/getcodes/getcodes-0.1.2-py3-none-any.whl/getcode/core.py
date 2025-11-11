from __future__ import annotations

import os
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .github_api import GitHubClient


SUBJECTS = (
    "CNS",
    "DBMS",
    "DSA",
    "FDS",
    "MP",
    "OOPCG",
)


_ver_re = re.compile(r"^v(\d+)$", re.IGNORECASE)


def list_subjects(client: GitHubClient) -> List[str]:
    # List root and retain only known subjects
    entries = client.list_dir("")
    names = [e["name"] for e in entries if e.get("type") == "dir"]
    return [s for s in SUBJECTS if s in names]


def list_subject_contents(
    client: GitHubClient,
    subject: str,
    *,
    extensions: Optional[Sequence[str]] = None,
    all_versions: bool = False,
) -> Dict[str, List[dict]]:
    """
    Returns a mapping of version -> list[content_obj].
    If versioned directories exist (v1, v2, ...), groups by them.
    Otherwise returns a single key "root" with files in subject root.
    If all_versions is False and versioned dirs exist, returns only the latest version.
    """
    subject = subject.strip("/")
    if subject not in SUBJECTS:
        raise ValueError(f"Unknown subject: {subject}")

    def _filter(files: List[dict]) -> List[dict]:
        if not extensions:
            return files
        exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}
        out = []
        for f in files:
            if f.get("type") != "file":
                continue
            name = f.get("name", "")
            _, dot, ext = name.rpartition(".")
            if not dot:
                continue
            if f".{ext.lower()}" in exts:
                out.append(f)
        return out

    def _collect_files_recursive(base_path: str) -> List[dict]:
        stack = [base_path]
        collected: List[dict] = []
        while stack:
            cur = stack.pop()
            for e in client.list_dir(cur):
                t = e.get("type")
                if t == "file":
                    collected.append(e)
                elif t == "dir":
                    stack.append(e.get("path"))
        return collected

    entries = client.list_dir(subject)
    dirs = [e for e in entries if e.get("type") == "dir"]
    files = [e for e in entries if e.get("type") == "file"]

    # Detect versioned dirs
    versioned: List[Tuple[int, dict]] = []
    for d in dirs:
        m = _ver_re.match(d.get("name", ""))
        if m:
            versioned.append((int(m.group(1)), d))
    if versioned:
        versioned.sort(key=lambda x: x[0])
        ver_map: Dict[str, List[dict]] = {}
        if not all_versions:
            # Only include latest version
            _, latest_dir = versioned[-1]
            vname = latest_dir["name"]
            vfiles = _collect_files_recursive(latest_dir["path"])  # recurse
            ver_map[vname] = _filter(vfiles)
            return ver_map
        for num, d in versioned:
            vname = d["name"]
            vfiles = _collect_files_recursive(d["path"])  # recurse
            ver_map[vname] = _filter(vfiles)
        return ver_map
    # No versioning; collect recursively under subject
    all_files = _collect_files_recursive(subject)
    return {"root": _filter(all_files)}


def search_files(
    client: GitHubClient,
    pattern: str,
    *,
    subject: Optional[str] = None,
    extensions: Optional[Sequence[str]] = None,
    all_versions: bool = False,
) -> List[dict]:
    pat = pattern.lower()
    subjects = [subject] if subject else list_subjects(client)
    out: List[dict] = []
    for sub in subjects:
        ver_map = list_subject_contents(
            client, sub, extensions=extensions, all_versions=all_versions
        )
        for files in ver_map.values():
            for f in files:
                name = f.get("name", "").lower()
                if pat in name:
                    out.append(f)
    return out


def pick_target(
    client: GitHubClient,
    *,
    subject: str,
    name: str,
    version: Optional[str] = None,
) -> dict:
    """Pick a single file by exact name within a subject and optional version.
    If version is None and multiple exist, prefer latest version directory.
    """
    if version:
        ver_map = list_subject_contents(client, subject, all_versions=True)
        files = ver_map.get(version)
        if files is None:
            raise FileNotFoundError(f"Version {version} not found in {subject}")
        for f in files:
            if f.get("name") == name:
                return f
        raise FileNotFoundError(f"{name} not found in {subject}/{version}")
    # No version specified; search latest-first
    ver_map = list_subject_contents(client, subject, all_versions=True)
    # order versions by numeric descending, with 'root' last
    ordered_keys = sorted(
        [k for k in ver_map.keys() if k != "root"],
        key=lambda k: int(_ver_re.match(k).group(1)) if _ver_re.match(k) else -1,
        reverse=True,
    )
    if "root" in ver_map:
        ordered_keys.append("root")
    for k in ordered_keys:
        for f in ver_map[k]:
            if f.get("name") == name:
                return f
    raise FileNotFoundError(f"{name} not found in {subject}")


def match_target(
    client: GitHubClient,
    *,
    subject: str,
    pattern: str,
    version: Optional[str] = None,
) -> dict:
    pat = pattern.lower()

    def score(name: str) -> int:
        n = name.lower()
        if n == pat:
            return 100
        if n.startswith(pat):
            return 80
        if pat in n:
            return 60
        return -1

    if version:
        ver_map = list_subject_contents(client, subject, all_versions=True)
        files = ver_map.get(version)
        if files is None:
            raise FileNotFoundError(f"Version {version} not found in {subject}")
        candidates = sorted(
            ((score(f.get("name", "")), f) for f in files), key=lambda x: (-x[0], x[1].get("name", ""))
        )
        if not candidates or candidates[0][0] < 0:
            raise FileNotFoundError(f"No match for '{pattern}' in {subject}/{version}")
        return candidates[0][1]
    # search across versions, latest-first preference using key ordering
    ver_map = list_subject_contents(client, subject, all_versions=True)
    ordered_keys = sorted(
        [k for k in ver_map.keys() if k != "root"],
        key=lambda k: int(_ver_re.match(k).group(1)) if _ver_re.match(k) else -1,
        reverse=True,
    )
    if "root" in ver_map:
        ordered_keys.append("root")
    best: Optional[Tuple[int, dict, str]] = None  # (score, file, version)
    for k in ordered_keys:
        for f in ver_map[k]:
            sc = score(f.get("name", ""))
            if sc < 0:
                continue
            if best is None or sc > best[0] or (sc == best[0] and k != "root" and best[2] == "root"):
                best = (sc, f, k)
    if not best:
        raise FileNotFoundError(f"No match for '{pattern}' in {subject}")
    return best[1]


def subject_summary(client: GitHubClient) -> List[Dict[str, object]]:
    """Return per-subject summary: total files, latest version label and count, and version map."""
    subs = list_subjects(client)
    out: List[Dict[str, object]] = []
    for s in subs:
        ver_map = list_subject_contents(client, s, all_versions=True)
        total = sum(len(v) for v in ver_map.values())
        if len(ver_map) == 1 and "root" in ver_map:
            latest_label = "root"
            latest_count = len(ver_map["root"])
        else:
            keys = [k for k in ver_map.keys() if k != "root"]
            if keys:
                latest_label = sorted(keys, key=lambda k: int(_ver_re.match(k).group(1)), reverse=True)[0]
                latest_count = len(ver_map.get(latest_label, []))
            else:
                latest_label = "root"
                latest_count = len(ver_map.get("root", []))
        out.append(
            {
                "subject": s,
                "total": total,
                "latest": latest_label,
                "latest_count": latest_count,
                "versions": {k: len(v) for k, v in ver_map.items()},
            }
        )
    return out

