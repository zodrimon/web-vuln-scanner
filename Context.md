# CONTEXT.md — Web Vulnerability Scanner (WVS)

> **READ THIS FILE COMPLETELY BEFORE DOING ANY WORK.**
> This file is your persistent memory. Every time you (the AI agent inside
> Antigravity) start a new session on this project — including after an
> unexpected shutdown, power loss, or crash — you MUST:
> 1. Run the crash-recovery check in §12 FIRST (`git status` / `git diff` /
>    `git log`) before reading further. Power can be lost at any moment,
>    mid-function, mid-commit — this step is what makes that safe. Never
>    skip it, even if you're fairly sure the last session ended cleanly.
> 2. Read this entire CONTEXT.md file.
> 3. Read TASKS.md and find the first task that is not marked `[DONE]`
>    (cross-checked against what §12 just told you).
> 4. Continue from there. Do not restart, do not redesign, do not ask the
>    user clarifying questions — everything you need is in these two files.
> 5. While working, commit at every safe checkpoint, not just at the end
>    of a task (see §12) — this is what keeps a power cut from costing
>    more than a few minutes of work.
> 6. After finishing a task, update its status in TASKS.md (`[DONE]`) and
>    update the "Current State" section (§14) of this file, then
>    commit + push to GitHub before moving to the next task.
>
> The human (Rimon) is the architect/director. You are the implementer.
> Do not wait for approval between tasks — execute the plan.

---

## 1. Project Identity

- **Name:** Web Vulnerability Scanner (short name: `wvs`)
- **One-liner:** A modular, CLI-first mini web-app security scanner (a
  learning-grade mini Burp Suite + sqlmap + ffuf hybrid) built in Python.
- **Owner / architect:** Rimon (CSE student, AIUB; offensive-security
  learner — CEH/eJPT level, working toward CRTA/CRTO/OSEP).
- **Purpose:** Portfolio project + deep-dive learning tool for HTTP
  internals, crawling, injection detection, and report generation.
- **License:** MIT (add LICENSE file in Phase 0).
- **Repo visibility:** Public on GitHub.

## 2. Mission / Design Goals

1. **Correctness over cleverness.** Every detection module should be
   explainable — this is a learning tool, not a black box.
2. **Modular & pluggable.** New scanner types (SSRF, JWT, GraphQL, SSTI,
   command injection, etc.) must be addable later as self-contained
   modules without touching core code. Treat this as a plugin system from
   day one, even though Phase 1 only ships SQLi + XSS + brute-force.
3. **Cross-platform.** Must run identically on Linux, Windows, and macOS.
   No shell-specific commands, no hardcoded path separators, no OS-only
   libraries. Use `pathlib`, `os.path`, and pure-Python HTTP (`requests`).
4. **CLI-first.** No GUI. Everything is driven by `wvs` command + flags
   + an optional YAML config file. (A web UI may be considered as a
   future phase, added as a separate optional module — not now.)
5. **Safe by default.** The tool must not run against a target unless the
   user explicitly confirms authorization (see §13 Legal/Ethical Guard).
6. **Small, testable units.** Every capability is one function or one
   small class with a single responsibility, unit-testable in isolation.
   This is why TASKS.md is broken into very small tasks — one task should
   generally produce one function/class plus its test, not a whole module
   at once.

## 3. Architecture Overview

```
web-vuln-scanner/
├── README.md
├── CONTEXT.md                 <-- this file
├── TASKS.md                   <-- the task list
├── LICENSE
├── .gitignore
├── pyproject.toml             <-- packaging, console_script entry point "wvs"
├── requirements.txt
├── config/
│   └── default_config.yaml
├── wordlists/
│   └── common_dirs.txt        <-- small seed wordlist for brute-forcing
├── src/
│   └── wvs/
│       ├── __init__.py
│       ├── __main__.py        <-- `python -m wvs`
│       ├── cli.py             <-- argparse entry point, subcommands
│       ├── config.py          <-- config loader/validator (YAML + CLI overrides)
│       ├── constants.py       <-- version, banners, default timeouts, etc.
│       ├── core/
│       │   ├── __init__.py
│       │   ├── http_session.py    <-- shared requests.Session wrapper (UA, rate limit, retries)
│       │   ├── models.py          <-- dataclasses: Endpoint, Parameter, Finding, ScanResult
│       │   ├── logger.py          <-- logging setup (console + file, colored)
│       │   ├── authorization.py   <-- legal/ethical guard (see §13)
│       │   └── plugin_registry.py <-- scanner plugin discovery/registration
│       ├── crawler/
│       │   ├── __init__.py
│       │   ├── crawler.py         <-- BFS crawler, same-origin scope control
│       │   ├── link_parser.py     <-- extract <a>, <form>, <script src> via BeautifulSoup
│       │   ├── form_parser.py     <-- extract form fields/method/action
│       │   └── robots.py          <-- robots.txt parsing/respect (optional flag)
│       ├── scanners/
│       │   ├── __init__.py
│       │   ├── base_scanner.py    <-- abstract BaseScanner interface all plugins implement
│       │   ├── sqli/
│       │   │   ├── __init__.py
│       │   │   ├── payloads.py        <-- error-based + time-based payload lists
│       │   │   ├── error_based.py     <-- error-signature detection
│       │   │   └── time_based.py      <-- timing/delay detection
│       │   └── xss/
│       │       ├── __init__.py
│       │       ├── payloads.py        <-- reflected XSS payload list
│       │       └── reflected.py       <-- reflection detection logic
│       ├── bruteforce/
│       │   ├── __init__.py
│       │   ├── fuzzer.py          <-- threaded directory/file brute-forcer
│       │   └── status_filter.py   <-- response-code/size filtering logic
│       └── report/
│           ├── __init__.py
│           ├── report_builder.py  <-- aggregates Findings into a ScanReport object
│           ├── markdown_report.py <-- renders ScanReport -> .md
│           ├── html_report.py     <-- renders ScanReport -> .html (Jinja2 template)
│           └── templates/
│               └── report.html.j2
├── tests/
│   ├── test_http_session.py
│   ├── test_crawler.py
│   ├── test_sqli_error_based.py
│   ├── test_sqli_time_based.py
│   ├── test_xss_reflected.py
│   ├── test_fuzzer.py
│   └── test_report_builder.py
└── examples/
    └── sample_targets.md      <-- links to intentionally-vulnerable practice apps (DVWA, juice-shop, testphp.vulnweb.com)
```

## 4. Tech Stack & Conventions

- **Language:** Python 3.11+
- **Core libs:** `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, `Jinja2`,
  `colorama` (Windows-safe colored terminal output), `rich` optional for
  progress bars.
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor` for crawling
  and brute-forcing (thread-based, not async — keeps the code readable
  for a learning project). Always expose a `--threads` flag with a safe
  default (e.g. 10).
- **Testing:** `pytest`. Every scanner/detector function gets at least
  one positive and one negative test using `responses` or `requests-mock`
  to fake HTTP responses (no live network calls in unit tests).
- **Style:** PEP8, type hints on every function signature, docstrings
  (Google style) on every public function/class.
- **Packaging:** `pyproject.toml` with a console entry point so the tool
  installs as `wvs` (`pip install -e .` then `wvs --help`).
- **Line length:** 100 cols. Formatter: `black`. Linter: `ruff`.

## 5. Coding Standards (non-negotiable)

1. No bare `except:` — always catch specific exceptions.
2. No `print()` in library code — use the `core.logger` module everywhere
   except `cli.py` output formatting.
3. Every network call goes through `core.http_session` — never call
   `requests.get`/`requests.post` directly from a scanner module. This
   is what lets rate-limiting, retries, and the authorization guard live
   in one place.
4. Every scanner module subclasses `BaseScanner` and implements:
   `scan(endpoint: Endpoint) -> list[Finding]`.
5. Payload lists live in their own `payloads.py` file per scanner, never
   inline in the detection logic — makes them easy to extend later.
6. All file paths built with `pathlib.Path`, never string concatenation
   with `/` or `\`.
7. No target is ever scanned without passing through
   `core.authorization.confirm_authorized(target)` first.

## 6. Data Models (core/models.py) — reference shape

```python
@dataclass
class Endpoint:
    url: str
    method: str                # "GET" | "POST"
    params: dict[str, str]      # discovered query/form params
    source: str                 # "crawl" | "bruteforce"

@dataclass
class Finding:
    vuln_type: str              # "SQLi-Error" | "SQLi-Time" | "XSS-Reflected" | "Exposed-Path"
    severity: str                # "info" | "low" | "medium" | "high" | "critical"
    endpoint: Endpoint
    parameter: str | None
    payload: str | None
    evidence: str                # snippet of response / timing delta / status code
    description: str
    remediation: str

@dataclass
class ScanResult:
    target: str
    started_at: datetime
    finished_at: datetime
    endpoints_discovered: list[Endpoint]
    findings: list[Finding]
```
(Exact fields may be refined during TASK-004, but keep this shape.)

## 7. CLI Design (reference — refine during TASK-006..008)

```
wvs scan --target https://example.com --i-have-authorization \
          --modules sqli,xss,bruteforce \
          --threads 10 --depth 3 \
          --wordlist wordlists/common_dirs.txt \
          --output report.html --format html

wvs crawl-only --target https://example.com --i-have-authorization --output endpoints.json
wvs --version
wvs --help
```

## 8. Config File (config/default_config.yaml) — reference shape

```yaml
threads: 10
timeout_seconds: 8
rate_limit_per_second: 5
user_agent: "WVS/0.1 (+https://github.com/<user>/web-vuln-scanner)"
crawl:
  max_depth: 3
  same_origin_only: true
  respect_robots_txt: true
modules:
  - sqli
  - xss
  - bruteforce
sqli:
  time_delay_seconds: 5
bruteforce:
  wordlist: "wordlists/common_dirs.txt"
  extensions: ["", ".php", ".bak", ".txt"]
report:
  format: "html"     # html | markdown
  output_path: "wvs_report.html"
```

## 9. Cross-Platform Rules

- Never use `os.system`, shell `&&`, or platform-specific commands.
- Use `pathlib.Path` everywhere; never hardcode `/` or `\`.
- Colored terminal output must call `colorama.init()` on Windows.
- Threading, not `fork`-based multiprocessing (multiprocessing behaves
  differently on Windows — avoid it entirely for this project).
- File writes always use `encoding="utf-8"`.
- Line endings: rely on Git's `.gitattributes` (`* text=auto`) — do not
  hand-manage `\r\n` vs `\n`.

## 10. Git & GitHub Workflow

- Repo is initialized in Phase 0 (`git init`, `.gitignore`, first commit).
- Commit after **every completed task** in TASKS.md, not after whole
  phases — small, atomic commits with messages formatted as:
  `TASK-0XX: <short description>` (e.g. `TASK-014: implement error-based SQLi detector`).
- Push to `origin/main` after every commit (assume remote is already
  configured/authenticated in the Antigravity environment — if it is not,
  stop and create the repo via `gh repo create` if the GitHub CLI is
  available, otherwise leave a clear note in the commit log and continue
  working locally; do not block progress waiting for confirmation).
- Never force-push. Never rewrite history.
- Branch strategy: work directly on `main` for this solo learning project
  (no PR ceremony needed) unless told otherwise later.

## 11. Extensibility / Future Tech Plugins

This project WILL grow. Do not hardcode assumptions that block future
additions. Concretely:
- New scanners are added by dropping a new package under `scanners/`
  that subclasses `BaseScanner` and self-registers in
  `core/plugin_registry.py`. Candidates the user may ask for later:
  SSTI, command injection, SSRF, open redirect, JWT analysis, CORS
  misconfig, security-header auditing, GraphQL introspection.
- Report formats are pluggable too — `report_builder.py` produces a
  format-agnostic `ScanReport`, and each renderer (`markdown_report.py`,
  `html_report.py`, future `json_report.py`/`pdf_report.py`) just
  consumes that object.
- Keep `core/http_session.py` as the single choke point so future
  features (proxy support for Burp, auth/session-cookie handling, header
  injection) only need to change one file.

## 12. Power-Loss / Crash Resilience — Resume Protocol (mandatory, follow every session)

The machine, IDE, or power can die mid-task at any point. The workflow
below exists so no more than a few minutes of work is ever lost, and so
you never have to guess what state the repo is in.

**Rule: commit checkpoints, not just finished tasks.**
Do not treat "commit" as something that only happens at the end of a
task. Commit at every safe checkpoint *within* a task too — e.g. right
after a new function is written and passes its own test, before you move
on to wiring it into anything else. A task that touches 2 files should
usually be 1-2 commits, not one giant commit at the very end. Small,
frequent, working commits are the entire safety net here — use them
generously. Never leave more than ~10-15 minutes of un-committed work
sitting in the working tree.

**Startup sequence — run this before reading anything else, every single
session (fresh start, mid-task resume, different OS, doesn't matter):**

1. Run `git status`. If there are uncommitted changes:
   - Run `git diff` to see exactly what's there.
   - Compare it against TASKS.md to figure out which task it belongs to.
   - If the change looks complete and correct (function is finished, has
     a docstring, would plausibly pass its test) → finish it out: write/
     run its test, commit it properly, mark the task `[DONE]`, continue.
   - If the change looks partial/broken/half-written → do NOT try to
     guess the rest. Discard it (`git checkout -- .` / `git clean -fd`
     for untracked scratch files) and redo that one task cleanly from
     TASKS.md. Tasks are deliberately small, so redoing one is cheap —
     cheaper than trying to reconstruct unknown intent.
2. Run `git log --oneline -5` to confirm the last few commits match what
   CONTEXT.md §14 "Current State Tracker" says was last completed. If
   they don't match (tracker is stale), trust `git log`, not the tracker
   — update §14 to match reality before doing anything else.
3. Only after steps 1-2 are resolved: open TASKS.md, find the first task
   not marked `[DONE]`, and resume there.
4. If mid-way through a multi-part task (e.g. "TASK-020 part C") when
   work stopped, treat each lettered part as its own checkpoint — resume
   from the first unfinished part, not from the top of the task.

**Never assume you remember what you were doing.** Trust the filesystem
(`git status`/`git diff`/`git log`) and the two tracking files over any
memory of "what I was probably in the middle of." This protocol is what
makes that safe even after a hard power cut with zero warning.

**Push, don't just commit.** A commit that only exists locally is still
at risk if the disk itself is the thing that fails. Push to `origin/main`
after every checkpoint commit where a network connection is available —
don't batch pushes up for "later."

## 13. Legal / Ethical Use Guard (mandatory, implement in TASK-011)

- `core/authorization.py` must expose `confirm_authorized(target: str) -> bool`.
- The CLI requires either the `--i-have-authorization` flag OR an
  interactive typed confirmation before any request is sent to a target.
- README.md must contain a clear "Authorized use only" notice and point
  users toward legal practice targets (DVWA, OWASP Juice Shop,
  testphp.vulnweb.com, PortSwigger Web Security Academy) for testing this
  tool itself.
- This is a hard requirement, not optional polish — implement it early
  (Phase 1) so every later module builds on top of it.

## 14. Current State Tracker

> Update this section every session before stopping work, and read it
> first when resuming — but per §12, verify it against `git log` first,
> since the tracker can go stale if a session ends without a final update.

- **Last completed task:** TASK-045
- **Current phase:** Phase 7 — CLI Integration
- **Next task to pick up:** TASK-046
- **Last known-good commit hash:** 2b91a139b1adb0bd52153452c92b2ef4ae456d41
- **Known issues / blockers:** none
- **Notes for next session:** none