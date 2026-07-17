import uuid
from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession
from wvs.scanners.base_scanner import BaseScanner
from wvs.scanners.xss.payloads import REFLECTED_XSS_PAYLOADS
from wvs.core.plugin_registry import register_scanner


def generate_marker() -> str:
    """Returns a unique per-scan token to embed in payloads."""
    return uuid.uuid4().hex[:8]


def is_reflected_unescaped(response_text: str, payload: str) -> bool:
    """
    Checks whether the raw payload appears unescaped in the response body.
    We check if the exact payload string is present.
    """
    return payload in response_text


@register_scanner
class ReflectedXssScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "xss_reflected"

    @property
    def severity_default(self) -> str:
        return "medium"

    def scan(self, endpoint: Endpoint, session: WvsSession) -> list[Finding]:
        findings = []
        if not endpoint.params:
            return findings

        marker = generate_marker()

        for param, original_value in endpoint.params.items():
            for payload_template in REFLECTED_XSS_PAYLOADS:
                payload = payload_template.format(marker=marker)

                test_params = endpoint.params.copy()
                test_params[param] = f"{original_value}{payload}"

                try:
                    if endpoint.method == "POST":
                        resp = session.post(endpoint.url, data=test_params)
                    else:
                        resp = session.get(endpoint.url, params=test_params)

                    if is_reflected_unescaped(resp.text, payload):
                        # Extract a snippet around the payload for evidence
                        idx = resp.text.find(payload)
                        start = max(0, idx - 20)
                        end = min(len(resp.text), idx + len(payload) + 20)
                        snippet = resp.text[start:end].replace("\n", " ").strip()

                        findings.append(
                            Finding(
                                vuln_type="Reflected XSS",
                                severity=self.severity_default,
                                endpoint=endpoint,
                                parameter=param,
                                payload=payload,
                                evidence=f"Payload reflected unescaped: ...{snippet}...",
                                description="Reflected Cross-Site Scripting (XSS) detected. The application reflects user input directly into the HTML without encoding.",
                                remediation="HTML-entity encode all user-supplied input before rendering it in the browser.",
                            )
                        )
                        break  # Skip remaining payloads for this parameter
                except Exception:
                    pass

        return findings
