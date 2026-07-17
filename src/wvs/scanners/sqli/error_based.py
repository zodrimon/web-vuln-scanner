from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.payloads import ERROR_BASED_PAYLOADS

DB_ERRORS = [
    "sql syntax",
    "mysql_fetch",
    "ora-",
    "postgresql query failed",
    "sqlite3::sqlexception",
    "microsoft ole db provider for sql server",
    "unclosed quotation mark after the character string"
]

def check_error_based(endpoint: Endpoint, session: WvsSession) -> list[Finding]:
    """Check for error-based SQL injection on the endpoint's parameters."""
    findings = []
    
    if not endpoint.params:
        return findings
        
    for param, original_value in endpoint.params.items():
        for payload in ERROR_BASED_PAYLOADS:
            test_params = endpoint.params.copy()
            # Append payload to original value
            test_params[param] = f"{original_value}{payload}"
            
            try:
                if endpoint.method == "POST":
                    resp = session.post(endpoint.url, data=test_params)
                else:
                    resp = session.get(endpoint.url, params=test_params)
                    
                resp_text_lower = resp.text.lower()
                
                matched_error = None
                for db_error in DB_ERRORS:
                    if db_error in resp_text_lower:
                        matched_error = db_error
                        break
                        
                if matched_error:
                    findings.append(Finding(
                        vuln_type="SQL Injection (Error Based)",
                        severity="high",
                        endpoint=endpoint,
                        parameter=param,
                        payload=payload,
                        evidence=f"Matched error pattern: {matched_error}",
                        description="Database error indicating possible SQL Injection.",
                        remediation="Use parameterized queries."
                    ))
                    # If we found an injection on this param with one payload,
                    # we can skip the rest of the payloads for this specific param
                    # to save time and reduce noise.
                    break
                    
            except Exception:
                # If network fails, skip this payload
                pass
                
    return findings
