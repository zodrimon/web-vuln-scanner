# TASKS.md — Web Vulnerability Scanner (WVS)

> Work top to bottom. Each task is intentionally small (usually one
> function/class + its test). Do NOT batch multiple tasks into one giant
> generation — finish one, mark it `[DONE]`, commit + push, then move on.
> Before starting, run the crash-recovery check in CONTEXT.md §12
> (`git status`/`git diff`/`git log`) — this matters even at the very
> start of a session, since power can be lost mid-task with zero warning
> and the working tree may hold unfinished work from last time. Then
> read CONTEXT.md in full, find the first task below that is not
> `[DONE]`, and resume there. Do not ask the user questions — if
> something is ambiguous, make the most sensible choice consistent with
> CONTEXT.md and note your assumption in the commit message or a
> `# NOTE:` comment.
>
> Commit checkpoints as you go within a task, not only when a task is
> fully finished — see CONTEXT.md §12. For multi-part tasks (labeled
> "part A/B/C"), each part is its own checkpoint: commit after each part
> so a crash mid-task only loses the current part, not the whole task.
>
> Status legend: `[ ]` not started · `[WIP]` in progress · `[DONE]` complete

---

## PHASE 0 — Project Scaffolding & Git Setup

- [DONE] **TASK-001** — Create the full directory structure exactly as shown
  in CONTEXT.md §3 (empty `__init__.py` files where needed, empty
  placeholder files elsewhere). Do not write logic yet.
- [DONE] **TASK-002** — Create `.gitignore` (Python, venv, `__pycache__`,
  `.pytest_cache`, `*.egg-info`, IDE folders, `wvs_report.*` output
  files, `.env`) and `.gitattributes` (`* text=auto`).
- [DONE] **TASK-003** — Create `LICENSE` (MIT, author "Rimon") and a first-
  draft `README.md` with: project title, one-liner, install instructions
  (`pip install -e .`), usage example, and the "Authorized use only"
  legal notice from CONTEXT.md §13.
- [DONE] **TASK-004** — Create `pyproject.toml`: project metadata, Python
  `>=3.11` requirement, dependencies (`requests`, `beautifulsoup4`,
  `lxml`, `PyYAML`, `Jinja2`, `colorama`, `rich`), dev-dependencies
  (`pytest`, `requests-mock`, `black`, `ruff`), and console entry point
  `wvs = "wvs.cli:main"`.
- [DONE] **TASK-005** — Create `requirements.txt` mirroring the runtime deps
  from TASK-004 (for users who don't want editable install).
- [DONE] **TASK-006** — `git init` (if not already a repo), stage everything,
  commit as `TASK-001..006: project scaffolding`, create the GitHub repo
  (via `gh repo create web-vuln-scanner --public --source=. --remote=origin`
  if `gh` CLI is available; otherwise instruct via README how to add the
  remote) and push to `main`.

## PHASE 1 — Core Infrastructure

- [DONE] **TASK-007** — `constants.py`: `VERSION`, `TOOL_NAME`, `BANNER`
  (ASCII banner string), `DEFAULT_TIMEOUT`, `DEFAULT_THREADS`,
  `DEFAULT_USER_AGENT`.
- [ ] **TASK-008** — `core/logger.py`: `get_logger(name: str) -> Logger`
  factory. Console handler with `colorama`-safe colored levels + optional
  file handler when `--log-file` is passed. One test verifying log level
  filtering.
- [ ] **TASK-009** — `core/models.py`: implement the `Endpoint`,
  `Finding`, and `ScanResult` dataclasses per CONTEXT.md §6, with
  `to_dict()` serialization methods on each (needed later for JSON/report
  export). Unit test for `to_dict()` round-tripping.
- [ ] **TASK-010** — `config.py`: `load_config(path: Path | None) -> dict`
  that loads `config/default_config.yaml`, deep-merges any user-supplied
  YAML override, then deep-merges CLI-flag overrides on top. Validate
  required keys exist; raise a clear `ConfigError` if not. Unit test with
  a sample override file.
- [ ] **TASK-011** — `core/authorization.py`: implement
  `confirm_authorized(target: str, flag_provided: bool) -> bool` per
  CONTEXT.md §13 (checks `--i-have-authorization` flag first, else
  prompts `y/N` interactively, else returns False in non-interactive
  contexts). Unit test for both flag-provided and flag-missing paths
  (mock `input()`).
- [ ] **TASK-012** — `core/http_session.py`: `WvsSession` class wrapping
  `requests.Session` — sets User-Agent, per-request timeout, automatic
  retry (via `urllib3.Retry`) on 5xx/connection errors, and a token-
  bucket rate limiter respecting `rate_limit_per_second` from config.
  Expose `.get()` and `.post()` convenience methods that both funnel
  through one internal `_request()`. Unit test with `requests-mock`
  verifying headers, timeout, and rate-limit delay behavior.
- [ ] **TASK-013** — `core/plugin_registry.py`: `register_scanner(cls)`
  decorator and `get_registered_scanners() -> list[type[BaseScanner]]`
  used so `scanners/__init__.py` can auto-discover all scanner plugins
  without the CLI hardcoding imports. Unit test with two dummy scanner
  classes.
- [ ] **TASK-014** — Commit + push: `TASK-007..013: core infrastructure`.

## PHASE 2 — Crawler

- [ ] **TASK-015** — `crawler/link_parser.py`: `extract_links(html: str, base_url: str) -> set[str]`
  using BeautifulSoup — pulls `href` from `<a>`, `src` from `<script>`
  and `<img>`, resolves relative URLs via `urllib.parse.urljoin`. Unit
  test with sample HTML fixture.
- [ ] **TASK-016** — `crawler/form_parser.py`: `extract_forms(html: str, base_url: str) -> list[Endpoint]`
  — parses every `<form>`, its `method` (default GET), resolved `action`
  URL, and all `<input>/<select>/<textarea>` field names as an
  `Endpoint.params` dict. Unit test with a fixture form.
- [ ] **TASK-017** — `crawler/robots.py`: `is_allowed(url: str, user_agent: str) -> bool`
  wrapping `urllib.robotparser`, gracefully returning `True` if
  `robots.txt` is missing/unreachable. Unit test mocking a robots.txt
  response.
- [ ] **TASK-018** — `crawler/crawler.py` part A: `Crawler.__init__` —
  accepts `WvsSession`, `max_depth`, `same_origin_only`,
  `respect_robots_txt`, and initializes visited-set + queue state.
- [ ] **TASK-019** — `crawler/crawler.py` part B: `Crawler._is_in_scope(url) -> bool`
  — same-origin check using `urllib.parse.urlparse` comparing scheme+netloc.
  Unit test with in-scope/out-of-scope URL pairs.
- [ ] **TASK-020** — `crawler/crawler.py` part C: `Crawler.crawl(start_url) -> list[Endpoint]`
  — BFS loop using `link_parser` + `form_parser`, respecting `max_depth`,
  scope, and robots.txt, threaded fetch via `ThreadPoolExecutor`,
  de-duplicating visited URLs. Integration test against a small fake
  in-memory HTML site (via `requests-mock`) verifying depth limiting and
  dedup.
- [ ] **TASK-021** — Commit + push: `TASK-015..020: crawler module`.

## PHASE 3 — SQL Injection Detection

- [ ] **TASK-022** — `scanners/base_scanner.py`: abstract `BaseScanner`
  with `name: str`, `severity_default: str`, and abstract method
  `scan(self, endpoint: Endpoint, session: WvsSession) -> list[Finding]`.
- [ ] **TASK-023** — `scanners/sqli/payloads.py`: define
  `ERROR_BASED_PAYLOADS: list[str]` (classic single-quote/comment
  breakers) and `TIME_BASED_PAYLOADS: dict[str, str]` keyed by DB engine
  guess (MySQL `SLEEP()`, PostgreSQL `pg_sleep()`, MSSQL `WAITFOR DELAY`)
  with a placeholder for delay seconds.
- [ ] **TASK-024** — `scanners/sqli/error_based.py` part A:
  `DB_ERROR_SIGNATURES: dict[str, list[str]]` — regex/substring
  signatures per DB engine (MySQL, PostgreSQL, MSSQL, SQLite, Oracle)
  drawn from common driver error strings.
- [ ] **TASK-025** — `scanners/sqli/error_based.py` part B:
  `detect_error_signature(response_text: str) -> str | None` — returns
  the matched DB engine name or `None`. Unit test against fixture error
  strings for each engine.
- [ ] **TASK-026** — `scanners/sqli/error_based.py` part C:
  `ErrorBasedSqliScanner(BaseScanner)` — for each parameter on the
  endpoint, injects each payload from `ERROR_BASED_PAYLOADS`, sends the
  request via the session, runs `detect_error_signature` on the body,
  and emits a `Finding` (severity `high`) on match. Register via
  `@register_scanner`. Integration test with `requests-mock` simulating
  a vulnerable and a non-vulnerable parameter.
- [ ] **TASK-027** — `scanners/sqli/time_based.py` part A:
  `measure_baseline_latency(session, endpoint) -> float` — sends a clean
  request and records response time, run twice and averaged to reduce
  noise.
- [ ] **TASK-028** — `scanners/sqli/time_based.py` part B:
  `TimeBasedSqliScanner(BaseScanner)` — for each parameter, injects each
  payload from `TIME_BASED_PAYLOADS` with a configured delay (default 5s),
  compares observed latency against baseline + delay threshold, emits a
  `Finding` (severity `critical`) if the delay is observed consistently
  (require confirmation via a second request before flagging, to reduce
  false positives from network jitter). Register via `@register_scanner`.
  Unit test with `requests-mock` using a `response_delay`/callback to
  simulate slow vs normal responses.
- [ ] **TASK-029** — Commit + push: `TASK-022..028: SQLi detection modules`.

## PHASE 4 — Reflected XSS Detection

- [ ] **TASK-030** — `scanners/xss/payloads.py`: `REFLECTED_XSS_PAYLOADS: list[str]`
  — a small set of unique, easily-fingerprinted marker payloads (e.g.
  `<wvsXSSmarker>alert(1)</wvsXSSmarker>` style with a random-ish token
  per run to reduce false positives from cached/static content).
- [ ] **TASK-031** — `scanners/xss/reflected.py` part A:
  `generate_marker() -> str` — returns a unique per-scan token to embed
  in payloads so reflection detection can't be fooled by unrelated
  page content.
- [ ] **TASK-032** — `scanners/xss/reflected.py` part B:
  `is_reflected_unescaped(response_text: str, marker: str) -> bool` —
  checks whether the raw marker/payload appears unescaped (i.e. not
  HTML-entity-encoded) in the response body.
- [ ] **TASK-033** — `scanners/xss/reflected.py` part C:
  `ReflectedXssScanner(BaseScanner)` — for each parameter, injects each
  payload (with marker) via GET and POST as applicable, checks
  `is_reflected_unescaped`, emits a `Finding` (severity `medium`) on
  match with the reflected snippet as evidence. Register via
  `@register_scanner`. Integration test with `requests-mock` simulating
  reflected vs. escaped output.
- [ ] **TASK-034** — Commit + push: `TASK-030..033: reflected XSS detection`.

## PHASE 5 — Directory / File Brute-Forcing

- [ ] **TASK-035** — create `wordlists/common_dirs.txt` — a seed list of
  ~150-300 common paths/files (admin, backup, config, .git, .env,
  robots.txt, api, uploads, etc.) — small and self-contained so the repo
  doesn't depend on external wordlist downloads.
- [ ] **TASK-036** — `bruteforce/status_filter.py`: `should_report(status_code: int, response_size: int, ignore_codes: set[int], baseline_404_size: int | None) -> bool`
  — filters out expected 404s and configurable ignored status codes;
  optionally detects "soft 404" pages by comparing response size against
  a measured baseline for a known-bogus path. Unit test covering both
  hard-404 and soft-404 cases.
- [ ] **TASK-037** — `bruteforce/fuzzer.py` part A:
  `load_wordlist(path: Path) -> list[str]` — reads a wordlist file,
  strips blank lines/comments (`#`).
- [ ] **TASK-038** — `bruteforce/fuzzer.py` part B:
  `build_candidate_urls(base_url: str, words: list[str], extensions: list[str]) -> list[str]`
  — cartesian product of words x extensions, joined onto `base_url`.
- [ ] **TASK-039** — `bruteforce/fuzzer.py` part C:
  `DirectoryFuzzer` class — threaded (`ThreadPoolExecutor`) requester
  that fetches every candidate URL via `WvsSession`, applies
  `status_filter.should_report`, and yields `Finding` objects
  (`vuln_type="Exposed-Path"`, severity based on path sensitivity — e.g.
  `.git`/`.env` = high, generic admin panel = low/info). Integration
  test with `requests-mock` covering found/not-found/soft-404 cases.
- [ ] **TASK-040** — Commit + push: `TASK-035..039: brute-force fuzzer`.

## PHASE 6 — Report Generator

- [ ] **TASK-041** — `report/report_builder.py`:
  `build_report(target: str, started_at, finished_at, endpoints: list[Endpoint], findings: list[Finding]) -> ScanResult`
  plus `summarize(findings: list[Finding]) -> dict[str, int]` (counts by
  severity) used by both renderers.
- [ ] **TASK-042** — `report/markdown_report.py`:
  `render_markdown(result: ScanResult) -> str` — target/summary table,
  findings grouped by severity (critical → info), each finding showing
  type, endpoint, parameter, payload, evidence, remediation. Unit test
  snapshotting output structure (not exact bytes) for a sample
  `ScanResult`.
- [ ] **TASK-043** — `report/templates/report.html.j2`: Jinja2 HTML
  template — clean, single-file (inline CSS, no external assets so the
  report is portable), summary badges by severity color, collapsible
  finding details.
- [ ] **TASK-044** — `report/html_report.py`: `render_html(result: ScanResult) -> str`
  rendering the Jinja2 template above. Unit test verifying key fields
  appear in output for a sample `ScanResult`.
- [ ] **TASK-045** — Commit + push: `TASK-041..044: report generator`.

## PHASE 7 — CLI Integration

- [ ] **TASK-046** — `cli.py` part A: `build_arg_parser() -> argparse.ArgumentParser`
  implementing the `scan` and `crawl-only` subcommands and all flags from
  CONTEXT.md §7 (`--target`, `--i-have-authorization`, `--modules`,
  `--threads`, `--depth`, `--wordlist`, `--output`, `--format`,
  `--config`, `--log-file`, `--version`).
- [ ] **TASK-047** — `cli.py` part B: `run_scan(args) -> int` — wires
  together config loading → authorization guard → `WvsSession` →
  `Crawler` → registered scanners (filtered by `--modules`) → optional
  `DirectoryFuzzer` → `report_builder` → chosen renderer → write to
  `--output`. Prints a live-progress summary to console via `rich`
  (endpoints found, findings found so far).
- [ ] **TASK-048** — `cli.py` part C: `main() -> None` entry point tying
  `build_arg_parser` + `run_scan`/`run_crawl_only` together with proper
  exit codes; wire up in `pyproject.toml` (already declared in TASK-004)
  and `__main__.py` for `python -m wvs`.
- [ ] **TASK-049** — End-to-end smoke test: spin up a tiny local Flask/
  http.server test fixture (or `requests-mock`-based simulation) with one
  crawlable page, one reflected-XSS param, one error-based-SQLi param,
  and one brute-forceable hidden path; run the full `wvs scan` flow
  against it in a pytest test and assert all four issue types show up in
  the resulting `ScanResult`.
- [ ] **TASK-050** — Commit + push: `TASK-046..049: CLI integration + e2e test`.

## PHASE 8 — Docs, Polish, Cross-Platform Verification

- [ ] **TASK-051** — Expand `README.md`: full usage examples for all
  flags, sample HTML report screenshot placeholder, install steps for
  Linux/macOS (`venv`) and Windows (`python -m venv` + `Scripts\activate`),
  contribution notes, and a "roadmap" section listing planned future
  scanner modules (from CONTEXT.md §11) so the project visibly signals
  it's upgradeable.
- [ ] **TASK-052** — Add `examples/sample_targets.md` listing legal
  practice targets (DVWA, OWASP Juice Shop, testphp.vulnweb.com,
  PortSwigger Web Security Academy labs) with a one-line note on how to
  spin up DVWA/Juice Shop locally via Docker for safe testing.
- [ ] **TASK-053** — Run `black` + `ruff` across the whole `src/` tree,
  fix all lint warnings, re-run full `pytest` suite, confirm 100% pass.
- [ ] **TASK-054** — Manually verify path handling is platform-neutral:
  grep the codebase for any raw `"/"` or `"\\"` string path building,
  any `os.system`/shell calls, or any POSIX-only stdlib usage, and fix
  any found.
- [ ] **TASK-055** — Add a minimal GitHub Actions workflow
  (`.github/workflows/ci.yml`) running `pytest` + `ruff` on `ubuntu-latest`,
  `windows-latest`, and `macos-latest` for every push — this is the real
  cross-platform safety net going forward.
- [ ] **TASK-056** — Final commit + push: `TASK-051..055: docs, polish, CI`.
  Update CONTEXT.md §13 "Current State Tracker" to reflect Phase 8
  complete and v0.1 feature-complete.

---

## FUTURE / BACKLOG (not yet scheduled — do not start unless told)

These are candidate next-phase additions per CONTEXT.md §11. Leave
untouched for now; they exist here so future task numbers can be added
under a "PHASE 9" heading without losing the plan:

- SSTI (Server-Side Template Injection) scanner module
- Command Injection scanner module
- Open Redirect scanner module
- Security-header auditor (CSP, HSTS, X-Frame-Options, etc.)
- CORS misconfiguration checker
- Session/cookie/auth support (login before scanning authenticated pages)
- Proxy support (route traffic through Burp Suite for manual review)
- JSON report format
- Optional lightweight web dashboard for viewing reports