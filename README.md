# Web Vulnerability Scanner (wvs)

A modular, CLI-first mini web-app security scanner (a learning-grade mini Burp Suite + sqlmap + ffuf hybrid) built in Python.

> **Authorized use only:**
> This tool is strictly for educational purposes and authorized testing. Do not run this scanner against any target unless you have explicit permission. Practice targets like [DVWA](https://github.com/digininja/DVWA), [OWASP Juice Shop](https://github.com/juice-shop/juice-shop), or [testphp.vulnweb.com](http://testphp.vulnweb.com) are recommended for testing.

## Installation

```bash
# Clone the repository
git clone https://github.com/zodrimon/web-vuln-scanner.git
cd web-vuln-scanner

# Install in editable mode
pip install -e .
```

## Usage Example

```bash
wvs scan --target https://example.com --i-have-authorization \
          --modules sqli,xss,bruteforce \
          --threads 10 --depth 3 \
          --wordlist wordlists/common_dirs.txt \
          --output report.html --format html
```
