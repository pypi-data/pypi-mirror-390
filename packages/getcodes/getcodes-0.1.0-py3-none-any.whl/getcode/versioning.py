from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from typing import Optional

from . import __version__ as CURRENT_VERSION


PYPI_JSON_URL = "https://pypi.org/pypi/getcodes/json"


def get_current_version() -> str:
    return CURRENT_VERSION


def get_latest_version(timeout: float = 5.0) -> Optional[str]:
    try:
        req = urllib.request.Request(PYPI_JSON_URL, headers={"User-Agent": "getcode-cli/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("info", {}).get("version")
    except Exception:
        return None


def _in_venv() -> bool:
    return hasattr(sys, "real_prefix") or sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def upgrade_self() -> subprocess.CompletedProcess:
    # Build a safe pip command
    cmd = [sys.executable, "-m", "pip", "install", "-U", "getcodes"]
    # Prefer user install when not in venv
    if not _in_venv() and os.name != "nt":
        cmd.append("--user")
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
