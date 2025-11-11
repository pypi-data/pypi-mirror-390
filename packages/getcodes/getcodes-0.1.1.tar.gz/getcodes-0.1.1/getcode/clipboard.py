from __future__ import annotations

import os
import platform
import subprocess
from typing import Optional


def _try_proc_copy(cmd: list, data: bytes) -> bool:
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate(input=data, timeout=5)
        return p.returncode == 0
    except Exception:
        return False


def _try_tk_copy(text: str) -> bool:
    try:
        import tkinter  # type: ignore
        r = tkinter.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()  # now it stays on the clipboard after the window is closed
        r.destroy()
        return True
    except Exception:
        return False


def copy_text(text: str) -> bool:
    """Copy text to the system clipboard using stdlib or built-in OS tools.
    Returns True on success, False otherwise.
    """
    data = text.encode("utf-8")
    system = platform.system().lower()
    # Prefer OS-native utilities when available; otherwise try tkinter
    if system == "darwin":  # macOS
        if _try_proc_copy(["pbcopy"], data):
            return True
        return _try_tk_copy(text)
    if system == "windows":
        if _try_proc_copy(["clip"], data):
            return True
        return _try_tk_copy(text)
    # Linux/other: tkinter first; if not available, try wl-copy/xclip if present
    if _try_tk_copy(text):
        return True
    # best-effort fallbacks (may not be installed; not Python libs)
    for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
        if _try_proc_copy(cmd, data):
            return True
    return False

