from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Sequence
import platform
import subprocess
import ctypes
import shutil

from .github_api import GitHubClient, RepoRef
from .core import (
    list_subjects,
    list_subject_contents,
    search_files,
    pick_target,
    match_target,
    subject_summary,
    SUBJECTS,
)
from .clipboard import copy_text
from .versioning import get_current_version, get_latest_version, upgrade_self


def _comma_list(v: Optional[str]) -> Optional[List[str]]:
    if not v:
        return None
    return [x.strip() for x in v.split(",") if x.strip()]


def cmd_subjects(args: argparse.Namespace) -> int:
    client = GitHubClient()
    subs = list_subjects(client)
    for s in subs:
        print(s)
    return 0


def _print_files(ver_map, *, full_path: bool = False) -> None:
    for ver, files in ver_map.items():
        if ver != "root":
            print(f"[{ver}]")
        for f in files:
            if full_path:
                print(f["path"])  # repo path
            else:
                print(f["name"])  # filename only
        if ver != "root" and files:
            print("")


def cmd_list(args: argparse.Namespace) -> int:
    client = GitHubClient()
    exts = _comma_list(args.ext)
    ver_map = list_subject_contents(
        client,
        args.subject,
        extensions=exts,
        all_versions=args.all_versions,
    )
    _print_files(ver_map, full_path=args.full_path)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    client = GitHubClient()
    exts = _comma_list(args.ext)
    files = search_files(
        client,
        args.pattern,
        subject=args.subject,
        extensions=exts,
        all_versions=args.all_versions,
    )
    for f in files:
        print(f["path"])  # path is most helpful for get
    return 0


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _is_admin_windows() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def cmd_get(args: argparse.Namespace) -> int:
    client = GitHubClient()
    dest = Path(args.to).expanduser().resolve()
    _ensure_dir(dest)

    saved = 0
    conflicts = 0

    # Mutually exclusive action flags
    if getattr(args, "copy", False) and getattr(args, "save", False):
        print("Use only one of --copy or --save", file=sys.stderr)
        return 2

    def _save(content_obj: dict, *, version_hint: Optional[str] = None) -> None:
        nonlocal saved, conflicts
        data = client.get_raw(content_obj)
        # Copy-to-clipboard mode
        default_action = os.environ.get("GETCODE_DEFAULT_ACTION", "save").lower()
        do_copy = bool(getattr(args, "copy", False)) or (
            default_action == "copy" and not getattr(args, "save", False)
        )
        if do_copy:
            try:
                text = data.decode("utf-8")
            except Exception:
                text = None
            if text is not None:
                if copy_text(text):
                    print("copied to clipboard")
                    saved += 1
                    return
                else:
                    print("copy failed; saving to file instead", file=sys.stderr)
        if args.flatten:
            name = content_obj["name"]
            target = dest / name
            if target.exists():
                conflicts += 1
                suffix = f"-{version_hint}" if version_hint else "-1"
                stem = target.stem
                ext = target.suffix
                target = dest / f"{stem}{suffix}{ext}"
        else:
            target = dest / content_obj["path"]
            _ensure_dir(target.parent)
        with open(target, "wb") as fh:
            fh.write(data)
        print(f"saved: {target}")
        saved += 1

    if args.path:
        # Support shorthand: `gc get <subject> <pattern-or-name>`
        if args.path and args.path[0].upper() in SUBJECTS and not any("/" in t for t in args.path):
            subj = args.path[0].upper()
            if len(args.path) < 2:
                print("Provide a pattern or filename after subject, e.g. 'gc get DSA bst'", file=sys.stderr)
                return 2
            # Combine remaining tokens as a pattern; prefer exact name when it looks like a filename
            tokens = args.path[1:]
            pattern = " ".join(tokens)
            candidate = tokens[-1]
            obj = None
            tried_exact = False
            if "." in candidate:
                tried_exact = True
                try:
                    obj = pick_target(client, subject=subj, name=candidate, version=args.version)
                except Exception:
                    obj = None
            if obj is None:
                obj = match_target(client, subject=subj, pattern=pattern, version=args.version)
            version_hint = args.version
            if not version_hint:
                parent = Path(obj.get("path", "")).parent.name
                version_hint = parent if parent.lower().startswith("v") else None
            _save(obj, version_hint=version_hint)
            if conflicts:
                print(f"note: {conflicts} filename conflict(s) resolved by suffixing.")
            return 0 if saved > 0 else 1

        # Treat provided args as repo paths
        for p in args.path:
            # GitHub API returns list when querying a file path, so we use list_dir
            objects = client.list_dir(p)
            # find first file object matching path
            match = None
            for obj in objects:
                if obj.get("type") == "file" and obj.get("path") == p:
                    match = obj
                    break
            if not match:
                print(f"not found or not a file: {p}", file=sys.stderr)
                continue
            _save(match)
    else:
        if not args.subject or not (args.name or args.match):
            print("Either provide repo PATH(s) or --subject with --name or --match", file=sys.stderr)
            return 2
        if args.name and args.match:
            print("Use only one of --name or --match", file=sys.stderr)
            return 2
        if args.name:
            obj = pick_target(client, subject=args.subject, name=args.name, version=args.version)
        else:
            obj = match_target(client, subject=args.subject, pattern=args.match, version=args.version)
        version_hint = args.version
        if not version_hint:
            # Derive from parent dir if it's a versioned one
            parent = Path(obj.get("path", "")).parent.name
            version_hint = parent if parent.lower().startswith("v") else None
        _save(obj, version_hint=version_hint)

    if conflicts:
        print(f"note: {conflicts} filename conflict(s) resolved by suffixing.")
    return 0 if saved > 0 else 1


def cmd_wifi(args: argparse.Namespace) -> int:
    # Windows-only
    if platform.system().lower() != "windows":
        print("wifi: supported only on Windows (PowerShell)", file=sys.stderr)
        return 2

    adapter = "Wi-Fi"
    toggle_script = (
        "$adapter = '" + adapter + "';"
        "$net = Get-NetAdapter -Name $adapter -ErrorAction SilentlyContinue;"
        "if (-not $net) { Write-Host \"Adapter not found: $adapter\"; exit 1 }"
        "if ($net.Status -eq 'Disabled') {"
        "  Enable-NetAdapter -Name $adapter -Confirm:$false; Write-Host 'Wi-Fi enabled'"
        "} else {"
        "  Disable-NetAdapter -Name $adapter -Confirm:$false; Write-Host 'Wi-Fi disabled'"
        "}"
        "exit 0"
    )

    def _run_ps(cmd: List[str]) -> int:
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.stdout:
                print(res.stdout.strip())
            if res.returncode != 0 and res.stderr:
                print(res.stderr.strip(), file=sys.stderr)
            return res.returncode
        except Exception as e:
            print(str(e), file=sys.stderr)
            return 1

    if _is_admin_windows():
        # Run directly
        rc = _run_ps(["powershell", "-NoProfile", "-Command", toggle_script])
        return 0 if rc == 0 else rc

    # Not admin: request elevation via UAC and launch the toggle
    print("Requesting Administrator permission via UAC...", file=sys.stderr)
    elevate = (
        "$script = @'" + toggle_script + "'@; "
        "Start-Process PowerShell -Verb RunAs -ArgumentList ('-NoProfile -Command "' + $script + '"')"
    )
    rc = _run_ps(["powershell", "-NoProfile", "-Command", elevate])
    if rc == 0:
        print("Launched elevated PowerShell to toggle Wi-Fi. This window can close.")
        return 0
    print("Failed to launch elevated PowerShell. Please run PowerShell as Administrator and re-run 'gc wifi'.", file=sys.stderr)
    return rc


def _bulk_save_files(client: GitHubClient, files: List[dict], dest: Path) -> int:
    count = 0
    for f in files:
        if f.get("type") != "file":
            continue
        data = client.get_raw(f)
        target = dest / f["path"]
        _ensure_dir(target.parent)
        with open(target, "wb") as fh:
            fh.write(data)
        print(f"saved: {target}")
        count += 1
    return count


def cmd_all(args: argparse.Namespace) -> int:
    client = GitHubClient()
    dest = Path(args.to or os.environ.get("GETCODE_DOWNLOAD_DIR", "getcodes")).expanduser().resolve()
    _ensure_dir(dest)

    total = 0
    if args.subject:
        # Download all files under a subject (recursive, all versions)
        ver_map = list_subject_contents(client, args.subject, all_versions=True)
        all_files: List[dict] = []
        for files in ver_map.values():
            all_files.extend(files)
        total = _bulk_save_files(client, all_files, dest)
        print(f"Downloaded {total} file(s) from {args.subject} into {dest}")
        return 0 if total > 0 else 1

    # Download entire repo tree
    stack = [""]
    files: List[dict] = []
    seen = set()
    while stack:
        cur = stack.pop()
        try:
            entries = client.list_dir(cur)
        except Exception as e:
            print(str(e), file=sys.stderr)
            return 1
        for e in entries:
            p = e.get("path") or e.get("name")
            if not p or p in seen:
                continue
            seen.add(p)
            if e.get("type") == "file":
                files.append(e)
            elif e.get("type") == "dir":
                stack.append(p)
    total = _bulk_save_files(client, files, dest)
    print(f"Downloaded {total} file(s) from repository into {dest}")
    return 0 if total > 0 else 1


def cmd_del(args: argparse.Namespace) -> int:
    target = Path(args.to or os.environ.get("GETCODE_DOWNLOAD_DIR", "getcodes")).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if target == cwd or str(target) in ("/", "\\"):
        print("Refusing to delete the current directory.", file=sys.stderr)
        return 2
    if not target.exists():
        print(f"Nothing to delete at {target}")
        return 0
    try:
        shutil.rmtree(target)
    except Exception as e:
        print(f"Failed to delete {target}: {e}", file=sys.stderr)
        return 1
    print(f"Deleted {target}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    client = GitHubClient()
    summaries = subject_summary(client)
    if args.subject:
        summ = next((s for s in summaries if s["subject"] == args.subject), None)
        if not summ:
            print(f"Subject not found: {args.subject}", file=sys.stderr)
            return 1
        print(f"Subject: {summ['subject']}")
        print(f"Total files: {summ['total']}")
        print(f"Latest: {summ['latest']} ({summ['latest_count']} files)")
        if args.all_versions:
            print("Versions:")
            for k, v in sorted(summ["versions"].items(), key=lambda kv: (kv[0] != 'root', kv[0])):
                print(f"  {k}: {v}")
        return 0
    # all subjects
    for s in summaries:
        print(f"{s['subject']}: total {s['total']}; latest {s['latest']} ({s['latest_count']})")
        if args.all_versions:
            vers = ", ".join(f"{k}:{v}" for k, v in sorted(s["versions"].items(), key=lambda kv: (kv[0] != 'root', kv[0])))
            print(f"  {vers}")
    return 0


def cmd_ver(args: argparse.Namespace) -> int:
    cur = get_current_version()
    print(f"getcode version: {cur}")
    if args.check or args.upgrade:
        latest = get_latest_version()
        if not latest:
            print("latest: unavailable (offline or PyPI unreachable)")
            if args.upgrade:
                print("tip: try 'python -m pip install -U getcode-cli'", file=sys.stderr)
            return 0
        print(f"latest: {latest}")
        if args.upgrade:
            if latest == cur:
                print("Already up to date.")
                return 0
            print("Upgrading...")
            res = upgrade_self()
            if res.returncode == 0:
                print("Upgrade successful. Restart your shell to use the new version if needed.")
                return 0
            print("Upgrade failed. Run this manually:")
            print(res.args if isinstance(res.args, list) else res.args)
            print(res.stderr, file=sys.stderr)
            return res.returncode
    return 0


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="getcode",
        description=(
            "Browse and fetch code from the GetSomeSleepBro/codes repo without cloning."
        ),
    )
    p.add_argument(
        "--repo",
        help="Override repo as owner/name (default from GETCODE_REPO env)",
    )
    p.add_argument(
        "--branch",
        help="Override branch (default from GETCODE_BRANCH env)",
    )
    p.add_argument(
        "--token",
        help="GitHub token (default from GITHUB_TOKEN env)",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("subjects", help="List available subjects")
    s1.set_defaults(func=cmd_subjects)

    s2 = sub.add_parser("list", help="List codes for a subject")
    s2.add_argument("subject", choices=SUBJECTS, type=str.upper)
    s2.add_argument("--ext", help="Comma-separated extensions filter, e.g. .py,.cpp")
    s2.add_argument("--all-versions", action="store_true", help="Show all versions if present")
    s2.add_argument("--full-path", action="store_true", help="Print full repo paths")
    s2.set_defaults(func=cmd_list)

    s3 = sub.add_parser("search", help="Search filenames across subjects")
    s3.add_argument("pattern", help="Case-insensitive substring pattern")
    s3.add_argument("--subject", choices=SUBJECTS, type=str.upper, help="Limit to a single subject")
    s3.add_argument("--ext", help="Comma-separated extensions filter, e.g. .py,.cpp")
    s3.add_argument("--all-versions", action="store_true", help="Search all versions")
    s3.set_defaults(func=cmd_search)

    s4 = sub.add_parser("get", help="Fetch file(s) by path or by name within a subject")
    s4.add_argument("path", nargs="*", help="Repo path(s) like DSA/v3/B6_BSTops.cpp")
    s4.add_argument("-s", "--subject", choices=SUBJECTS, type=str.upper, help="Subject name")
    s4.add_argument("-n", "--name", help="Exact filename to fetch within subject")
    s4.add_argument("-m", "--match", help="Pattern to match filename within subject")
    s4.add_argument("-v", "--version", help="Version directory like v3 (if applicable)")
    s4.add_argument("--to", default=".", help="Destination directory (default: current)")
    s4.add_argument("--flatten", action="store_true", help="Save without subject/version folders")
    s4.add_argument("-c", "--copy", action="store_true", help="Copy to clipboard instead of saving (UTF-8 text)")
    s4.add_argument("--save", action="store_true", help="Force saving even if copy is default")
    s4.set_defaults(func=cmd_get)

    s5 = sub.add_parser("info", help="Show summary of subjects and versions")
    s5.add_argument("--subject", choices=SUBJECTS, type=str.upper, help="Show details for one subject")
    s5.add_argument("--all-versions", action="store_true", help="Include per-version counts")
    s5.set_defaults(func=cmd_info)

    # help command with quick examples
    h = sub.add_parser("help", help="Show quick examples and tips")
    h.set_defaults(func=lambda _a: _print_help())

    # wifi toggle (Windows)
    s6 = sub.add_parser("wifi", help="Toggle Wi-Fi adapter on Windows (requires admin)")
    s6.set_defaults(func=cmd_wifi)

    # version (aliases: v, version)
    sv = sub.add_parser("v", help="Show version; optionally check or upgrade")
    sv.add_argument("--check", action="store_true", help="Check latest version on PyPI")
    sv.add_argument("--upgrade", action="store_true", help="Upgrade to latest via pip")
    sv.set_defaults(func=cmd_ver)

    sv2 = sub.add_parser("version", help="Show version; optionally check or upgrade")
    sv2.add_argument("--check", action="store_true", help="Check latest version on PyPI")
    sv2.add_argument("--upgrade", action="store_true", help="Upgrade to latest via pip")
    sv2.set_defaults(func=cmd_ver)

    # all: download entire repo or a subject
    sa = sub.add_parser("all", help="Download entire repo or one subject")
    sa.add_argument("subject", nargs="?", choices=SUBJECTS, type=str.upper, help="Subject to download (optional)")
    sa.add_argument("--to", help="Destination directory (default: ./getcodes)")
    sa.set_defaults(func=cmd_all)

    # del: delete downloads
    sd = sub.add_parser("del", help="Delete downloaded files (default: ./getcodes)")
    sd.add_argument("--to", help="Target directory to delete (default: ./getcodes)")
    sd.set_defaults(func=cmd_del)
    return p


def _print_help() -> int:
    print(
        "Examples:\n"
        "  g subjects\n"
        "  g info --subject DSA\n"
        "  g dbms            # list DBMS codes (shorthand)\n"
        "  g dbms ddl        # fetch best match for 'ddl' in DBMS (shorthand)\n"
        "  g DSA/v3/B6_BSTops.cpp  # fetch by repo path (shorthand)\n"
        "  g search bst --subject DSA\n"
        "  g get -s DSA -m bst --copy   # copy best match to clipboard\n"
        "  g get DSA/v3/B6_BSTops.cpp --to ./out\n\n"
        "Tips:\n"
        "  - Subjects are case-insensitive (e.g., dbms == DBMS).\n"
        "  - Use --all-versions to include older implementations.\n"
        "  - Use --ext to filter by extensions (e.g., .py,.cpp).\n\n"
        "Config:\n"
        "  export GETCODE_DEFAULT_ACTION=copy   # make copying the default\n"
        "  export GITHUB_TOKEN=...              # increase API limits\n\n"
        "Windows:\n"
        "  PowerShell has a built-in 'gc' alias (Get-Content). Use 'g' instead.\n"
    )
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    # Shorthand: `gc <subject> [pattern...]`
    # - With pattern: maps to `get -s <SUBJECT> -m "pattern"` (default action copy/save)
    # - Without pattern: maps to `list <SUBJECT>`
    # Shorthand: `gc <path>` where <path> contains '/' maps to `get <path>`
    raw = list(argv) if argv is not None else sys.argv[1:]
    subcmds = {"subjects", "list", "search", "get", "info", "help"}
    new_argv: Optional[List[str]] = None

    if raw and raw[0] not in subcmds and not raw[0].startswith("-"):
        # treat leading non-flag tokens that look like repo paths as get paths
        paths: List[str] = []
        rest_flags: List[str] = []
        for i, x in enumerate(raw):
            if x.startswith("-"):
                rest_flags = raw[i:]
                break
            paths.append(x)
        if any("/" in p for p in paths):
            new_argv = ["get"] + [p for p in paths if "/" in p] + rest_flags

    if new_argv is None and raw and not raw[0].startswith("-") and raw[0].upper() in SUBJECTS:
        subj = raw[0].upper()
        if len(raw) > 1:
            rest = raw[1:]
            copy_flag = any(x in ("--copy", "-c") for x in rest)
            save_flag = any(x == "--save" for x in rest)
            pattern_parts = [x for x in rest if x not in ("--copy", "-c", "--save")]
            pattern = " ".join(pattern_parts).strip()
            if not pattern:
                new_argv = ["list", subj]
            else:
                # Subject+pattern shorthand: if exactly one match, fetch it; otherwise list options
                client = GitHubClient()
                matches = search_files(client, pattern, subject=subj, all_versions=True)
                if len(matches) == 1:
                    path = matches[0].get("path")
                    new_argv = ["get", path]
                    if copy_flag:
                        new_argv.append("--copy")
                    if save_flag:
                        new_argv.append("--save")
                elif len(matches) == 0:
                    print(f"No matches found for '{pattern}' in {subj}")
                    return 1
                else:
                    print(f"Multiple matches for '{pattern}' in {subj}:")
                    for m in matches:
                        print(m.get("path"))
                    print("Tip: pick a path above and run 'g get <path>' or narrow your search.")
                    return 0
        else:
            new_argv = ["list", subj]

    p = make_parser()
    if new_argv is not None:
        argv = new_argv
    args = p.parse_args(argv)

    # Wire repo/branch/token overrides into env for simplicity
    if args.repo:
        os.environ["GETCODE_REPO"] = args.repo
    if args.branch:
        os.environ["GETCODE_BRANCH"] = args.branch
    if args.token:
        os.environ["GITHUB_TOKEN"] = args.token

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("aborted", file=sys.stderr)
        return 130
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
