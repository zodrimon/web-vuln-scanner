# Web Vulnerability Scanner (WVS)

WVS is an automated web vulnerability scanner designed to crawl websites, discover endpoints, and detect common security vulnerabilities. It currently supports detecting Error-Based SQL Injection, Time-Based SQL Injection, Reflected Cross-Site Scripting (XSS), and exposed directories/files.

## Features

- **Automated Crawling**: Discovers endpoints by parsing links and forms, respecting `robots.txt` and configurable crawl depth.
- **SQL Injection Detection**: 
  - Error-based SQLi (supports MySQL, PostgreSQL, MSSQL, SQLite, Oracle).
  - Time-based SQLi with baseline calibration to reduce false positives.
- **Reflected XSS Detection**: Injects unique markers and detects unescaped reflection in the DOM.
- **Directory Brute-Forcing**: Discovers hidden files and directories (e.g., `.env`, `.git`, `admin/`) with soft-404 detection.
- **Reporting**: Generates beautiful HTML or Markdown reports detailing the vulnerabilities found.
- **Modular Architecture**: Easily extensible to add new vulnerability scanners.

## Disclaimer

**Legal & Liability Disclaimer**: This tool is provided for educational and authorized testing purposes only. You must obtain explicit, written permission from the owner of the target system before running any scans. The authors are not responsible for any misuse, damage, or legal consequences caused by the use of this software. By using this tool, you agree to take full responsibility for your actions.

## Installation

This project requires Python 3.10+.

1. Clone the repository:
   ```bash
   git clone https://github.com/zodrimon/web-vuln-scanner.git
   cd web-vuln-scanner
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

You can run WVS using the `wvs` CLI command or via `python -m wvs`.

### Full Vulnerability Scan

Run a full crawl and scan against a target:

```bash
python -m wvs scan "http://example.com" --i-have-authorization
```

*Note: The `--i-have-authorization` flag is mandatory to confirm you have permission to scan the target.*

**Options:**
- `--wordlist <path>`: Provide a wordlist to enable directory brute-forcing.
- `--depth <int>`: Maximum crawl depth (default: 3).
- `--threads <int>`: Number of concurrent threads (default: 10).
- `--modules <module_name...>`: Specific scanners to run (default: all). Available: `sqli_error_based`, `sqli_time_based`, `xss_reflected`.
- `--output <path>`: Path to save the report (default: `wvs_report.html`).
- `--format <html|markdown>`: Format of the report (default: `html`).

### Crawl Only

To only crawl the target and list discovered endpoints without running any vulnerability scanners:

```bash
python -m wvs crawl-only "http://example.com" --i-have-authorization
```

*Screenshot of the HTML report.*

## Architecture

WVS is built with a modular, pipeline-based architecture:

1. **Crawler (`wvs.crawler`)**: Visits the target URL, extracts links and forms, normalizes URLs, and queues them for scanning.
2. **Scanners (`wvs.scanners`)**: 
   - A plugin registry loads all `BaseScanner` implementations.
   - Each endpoint discovered by the crawler is passed to the selected scanners.
   - Scanners inject payloads and evaluate the HTTP responses.
3. **Brute-Forcer (`wvs.bruteforce`)**: Uses a multithreaded fuzzer to discover hidden files based on a wordlist.
4. **Reporter (`wvs.report`)**: Consolidates all `Finding` objects into a `ScanResult` and renders them into HTML or Markdown.

## Development and Testing

Run the pytest suite to verify all modules:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please ensure that you add unit tests for any new modules and run `black` and `ruff` against the codebase before submitting a PR.

## Roadmap

Future modules planned for WVS:
- **SSTI** (Server-Side Template Injection)
- **Command Injection**
- **Open Redirect**
- **Security Headers Auditor** (CSP, HSTS, etc.)
- **CORS Misconfiguration Checker**
- **Session/Cookie/Auth Support** (for authenticated scanning)
- **Proxy Support** (route traffic through Burp Suite)
