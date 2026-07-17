from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.payloads import ERROR_BASED_PAYLOADS
from wvs.scanners.base_scanner import BaseScanner
from wvs.core.plugin_registry import register_scanner

DB_ERROR_SIGNATURES = {
    "MySQL": [
        "sql syntax",
        "mysql_fetch",
    ],
    "PostgreSQL": [
        "postgresql query failed",
        "pg_query",
    ],
    "MSSQL": [
        "microsoft ole db provider for sql server",
        "unclosed quotation mark after the character string",
    ],
    "SQLite": [
        "sqlite3::sqlexception",
        "sqlite_error",
    ],
    "Oracle": [
        "ora-",
        "oracle error",
    ]
}

def detect_error_signature(response_text: str) -> str | None:
    """Returns the matched DB engine name or None."""
    lower_text = response_text.lower()
    for engine, signatures in DB_ERROR_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in lower_text:
                return engine
    return None

@register_scanner
class ErrorBasedSqliScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "sqli_error_based"
        
    @property
    def severity_default(self) -> str:
        return "high"

    def scan(self, endpoint: Endpoint, session: WvsSession) -> list[Finding]:
        """Check for error-based SQL injection on the endpoint's parameters."""
        findings = []
        
        if not endpoint.params:
            return findings
            
        for param, original_value in endpoint.params.items():
            for payload in ERROR_BASED_PAYLOADS:
                test_params = endpoint.params.copy()
                test_params[param] = f"{original_value}{payload}"
                
                try:
                    if endpoint.method == "POST":
                        resp = session.post(endpoint.url, data=test_params)
                    else:
                        resp = session.get(endpoint.url, params=test_params)
                        
                    matched_engine = detect_error_signature(resp.text)
                    if matched_engine:
                        findings.append(Finding(
                            vuln_type="SQL Injection (Error Based)",
                            severity=self.severity_default,
                            endpoint=endpoint,
                            parameter=param,
                            payload=payload,
                            evidence=f"Matched DB engine error: {matched_engine}",
                            description=f"Database error indicating possible {matched_engine} SQL Injection.",
                            remediation="Use parameterized queries."
                        ))
                        break
                except Exception:
                    pass
                    
        return findings
