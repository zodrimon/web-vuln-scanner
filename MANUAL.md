# WVS User Manual

## Table of Contents
1. [Overview](#overview)
2. [Installation Guide](#installation-guide)
    - [Linux](#linux)
    - [Windows](#windows)
    - [macOS](#macos)
3. [CLI Reference (`--help`)](#cli-reference)
4. [How the Scanners Work](#how-the-scanners-work)
    - [Crawler Engine](#crawler-engine)
    - [SQL Injection (Error-Based & Time-Based)](#sql-injection)
    - [Reflected XSS](#reflected-xss)
    - [Directory Brute-Forcing](#directory-brute-forcing)

---

## Overview
Web Vulnerability Scanner (WVS) is an automated, modular command-line tool built to identify basic vulnerabilities on target websites. It crawls a target URL to discover endpoints, executes specialized vulnerability scanning payloads against those endpoints, fuzzes for hidden directories, and generates a formatted HTML or Markdown report.

**Note:** This tool is designed strictly for authorized, educational testing.

---

## Installation Guide

The tool relies heavily on Python 3.10+ and standard dependency management via virtual environments. 

### Linux
1. **Ensure Python and pip are installed:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```
2. **Clone the repository:**
   ```bash
   git clone https://github.com/zodrimon/web-vuln-scanner.git
   cd web-vuln-scanner
   ```
3. **Set up the virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install WVS dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

### Windows
1. **Ensure Python 3 is installed** (check the "Add Python to PATH" box during installation).
2. **Open PowerShell or Command Prompt and clone the repo:**
   ```powershell
   git clone https://github.com/zodrimon/web-vuln-scanner.git
   cd web-vuln-scanner
   ```
3. **Set up the virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
4. **Install WVS dependencies:**
   ```powershell
   pip install -r requirements.txt
   pip install -e .
   ```

### macOS
1. **Ensure Python 3 is installed** (via Homebrew):
   ```bash
   brew install python git
   ```
2. **Clone the repository:**
   ```bash
   git clone https://github.com/zodrimon/web-vuln-scanner.git
   cd web-vuln-scanner
   ```
3. **Set up the virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install WVS dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

---

## CLI Reference

To run WVS, activate your virtual environment and use the `wvs` command.

### Subcommands
WVS provides two main subcommands:
- `scan`: Runs a full web vulnerability scan (crawl + vulnerability scan + brute-force).
- `crawl-only`: Runs only the crawling phase to map out a target's endpoints without exploiting or fuzzing anything.

### Global & Subcommand Flags

#### Help (`-h, --help`)
To see all available commands and arguments:
```bash
wvs -h
wvs scan -h
```

#### Full Scan Mode (`wvs scan`)
```bash
wvs scan "http://testphp.vulnweb.com" --i-have-authorization
```
- **`TARGET`** (Positional): The base URL to scan. (e.g., `http://example.com`)
- **`--i-have-authorization`** *(Required)*: Bypasses the interactive prompt, explicitly confirming that you possess the legal authority to test the given target. 
- **`--modules MODULE [MODULE ...]`**: Specify a space-separated list of scanners to run. If omitted, WVS runs **all** available modules. Available options:
  - `sqli_error_based`
  - `sqli_time_based`
  - `xss_reflected`
- **`--threads THREADS`**: Number of concurrent connections/threads to utilize. Default is `10`. Lower this to prevent DDOSing delicate targets.
- **`--depth DEPTH`**: Maximum link-following depth for the Crawler. Default is `3`.
- **`--wordlist WORDLIST`**: Path to a dictionary `.txt` file for directory brute-forcing. If omitted, no fuzzing occurs. You can use the built-in small wordlist at `wordlists/common_dirs.txt`.
- **`--output OUTPUT`**: The file path to save the generated report. Default is `wvs_report.html`.
- **`--format {html,markdown}`**: The format of the output report. Default is `html`.

#### Crawl Only Mode (`wvs crawl-only`)
```bash
wvs crawl-only "http://testphp.vulnweb.com" --i-have-authorization
```
- Includes the same parameters for the target, authorization, threads, and crawl depth. It will dump a JSON-like representation of discovered links and parameters directly to the console or output file.

---

## How the Scanners Work

WVS's engine operates in distinct phases, leveraging isolated, specialized modules.

### 1. Crawler Engine
The crawler systematically traverses the target utilizing a Breadth-First Search (BFS) algorithm. 
- **Link & Form Parsing:** It inspects `<a>` tags for hrefs and parses `<form>` tags for `action`, `method`, and `<input>` parameters.
- **Scope Restrictive:** It maintains a `same_origin_only` rule, meaning it will absolutely not crawl external subdomains or entirely different websites found on the target.
- **Robots.txt:** Automatically reads the `/robots.txt` configuration to prevent traversing paths heavily discouraged by the webmaster.

### 2. SQL Injection
WVS tests the safety of parameters by detecting if malicious SQL syntax breaks or pauses the backend queries.
- **Error-Based:** Iterates over a list of malformed payload endings (`'`, `""`, etc.) injecting them into endpoints. It then inspects the resulting page text for SQL database error signatures (e.g., `mysql_fetch_array()`, `ORA-`, `pg_query`).
- **Time-Based:** When databases hide SQL errors (Blind SQLi), WVS attempts to enforce a delayed response (`SLEEP(5)`, `pg_sleep(5)`). WVS calculates an initial response "baseline" latency. If injecting the sleep payload delays the HTTP response significantly beyond the baseline limit, it marks the endpoint as vulnerable.

### 3. Reflected XSS
Reflected Cross-Site Scripting occurs when an application takes user input and embeds it into the HTML DOM without sanitization.
- WVS generates a completely unique tag for every test payload (e.g., `<wvs73b9a1>alert(1)</wvs73b9a1>`).
- It submits this to all endpoint parameters. 
- The module then searches the resulting HTTP response text for the exact presence of that unique tag marker. If found intact, the parameter is vulnerable to Reflected XSS.

### 4. Directory Brute-Forcing (Fuzzer)
The directory fuzzer helps uncover hidden files that are not explicitly linked on the website (e.g., `/admin/`, `.git/`, `.env`).
- Taking an optional wordlist, it attempts `GET` requests against `<target>/<word>`.
- **Soft-404 Filtering:** Standard web scanners struggle with websites that return a `200 OK` for pages that don't exist (Soft 404s). WVS dynamically requests a guaranteed-fake endpoint (like `/wvs-bogus-random-1234`) to gauge what a "fake page" response code and file size look like. It rejects any hits that closely match the Soft-404 signature.
