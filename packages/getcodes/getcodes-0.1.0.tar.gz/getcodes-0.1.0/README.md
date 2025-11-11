getcode (gc) — fetch code from GetSomeSleepBro/codes without cloning

Overview
- Simple, intuitive CLI to browse and fetch code from the GitHub repo online (no full clone).
- Defaults to latest version when multiple implementations (v1, v2, …) exist.
- Stdlib-only (urllib); optional GitHub token to avoid rate limits.

Install
- pip install getcodes
- Console scripts: `getcode` and `gc`.

Config
- Env vars:
  - `GETCODE_REPO` (default: `GetSomeSleepBro/codes`)
  - `GETCODE_BRANCH` (default: `main`)
  - `GITHUB_TOKEN` (optional; increases rate limits)

Basic Use
- List subjects:
  - `gc subjects`
- Quick shorthand:
  - `gc dbms` → list DBMS codes
  - `gc dbms ddl` → fetch best match for "ddl" in DBMS (copy/save based on default)
  - `gc DSA/v3/B6_BSTops.cpp` → fetch by repo path
- List codes in a subject (latest version by default):
  - `gc list DSA`
  - `gc list CNS --ext .py` (only Python)
  - `gc list DBMS --all-versions --full-path`
- Show summary info:
  - `gc info` (totals and latest version per subject)
  - `gc info --subject DSA --all-versions`
- Search filenames across subjects:
  - `gc search bst --ext .cpp`
  - `gc search tcp --subject CNS`
- Fetch by repo path:
  - `gc get DSA/v3/B6_BSTops.cpp --to ./codes`
- Fetch by subject + pattern or exact name (simple):
  - `gc get dbms ddl` (best match in DBMS)
  - `gc get cns sliding_window.py` (exact name in CNS)
- Fetch by subject + name (chooses latest version if multiple):
  - `gc get -s DSA -n B6_BSTops.cpp --to ./codes`
  - `gc get -s DSA -n B6_BSTops.cpp -v v2` (specific version)
- Fetch by subject + pattern (picks best match):
  - `gc dsa bst` (shorthand; default action applies)
  - `gc get -s DSA -m bst --to ./codes`
  - Copy instead of saving:
    - `gc dsa bst --copy` (shorthand)
    - or `gc get -s DSA -m bst --copy`
- Flatten save path (avoid nested folders):
  - `gc get DSA/v3/B6_BSTops.cpp --flatten`

Notes
- Version folders appear only when multiple implementations exist. The CLI shows only the latest by default; use `--all-versions` to see others.
- Listing recurses into nested folders (e.g., `CNS/programs`, `DBMS/sql`).
- If saving multiple files with `--flatten` and names collide, the CLI appends a suffix (e.g., `-v3`).
- Network errors or API rate limits print a friendly hint to set `GITHUB_TOKEN`.
- Automatic fallback: if the GitHub API is rate-limited/unavailable, the CLI downloads a temporary ZIP snapshot of the repo and serves listings/reads from it. The snapshot lives in a temp folder and is cleaned up automatically at process exit (including Ctrl+C).

Clipboard
- Copy text directly: add `--copy` (or `-c`) to `gc get` when fetching a single file.
- Make copy the default action instead of saving files:
  - `export GETCODE_DEFAULT_ACTION=copy`
- Clipboard uses built-in OS tools (macOS `pbcopy`, Windows `clip`) or stdlib `tkinter` when available.

Help
- `gc help` shows quick examples and tips right in the terminal.
