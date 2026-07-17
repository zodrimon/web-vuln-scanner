import time
from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession
from wvs.scanners.sqli.payloads import TIME_BASED_PAYLOADS
from wvs.scanners.base_scanner import BaseScanner
from wvs.core.plugin_registry import register_scanner


def measure_baseline_latency(session: WvsSession, endpoint: Endpoint) -> float | None:
    """Sends a clean request twice and returns the average latency."""
    latencies = []
    for _ in range(2):
        try:
            start_time = time.time()
            if endpoint.method == "POST":
                session.post(endpoint.url, data=endpoint.params)
            else:
                session.get(endpoint.url, params=endpoint.params)
            latencies.append(time.time() - start_time)
        except Exception:
            return None

    return sum(latencies) / len(latencies)


@register_scanner
class TimeBasedSqliScanner(BaseScanner):
    def __init__(self, delay: int = 5):
        self.delay = delay

    @property
    def name(self) -> str:
        return "sqli_time_based"

    @property
    def severity_default(self) -> str:
        return "critical"

    def scan(self, endpoint: Endpoint, session: WvsSession) -> list[Finding]:
        findings = []
        if not endpoint.params:
            return findings

        baseline = measure_baseline_latency(session, endpoint)
        if baseline is None:
            return findings

        # If baseline is extremely high already, time-based SQLi might be too noisy.
        # But for this scanner, we'll just require baseline + delay * 0.8
        threshold = baseline + (self.delay * 0.8)

        for param, original_value in endpoint.params.items():
            for engine, payload_template in TIME_BASED_PAYLOADS.items():
                payload = payload_template.format(delay=self.delay)
                test_params = endpoint.params.copy()
                test_params[param] = f"{original_value}{payload}"

                def _measure_payload() -> float | None:
                    try:
                        start_time = time.time()
                        if endpoint.method == "POST":
                            session.post(endpoint.url, data=test_params)
                        else:
                            session.get(endpoint.url, params=test_params)
                        return time.time() - start_time
                    except Exception:
                        return None

                first_latency = _measure_payload()
                if first_latency is not None and first_latency >= threshold:
                    # Require confirmation to avoid network jitter false positives
                    second_latency = _measure_payload()
                    if second_latency is not None and second_latency >= threshold:
                        findings.append(
                            Finding(
                                vuln_type="SQL Injection (Time Based)",
                                severity=self.severity_default,
                                endpoint=endpoint,
                                parameter=param,
                                payload=payload,
                                evidence=f"Observed consistent delay > {threshold:.2f}s (Engine: {engine})",
                                description=f"Time-based SQL injection confirmed for {engine}. The application consistently delayed responses by {self.delay} seconds when injected.",
                                remediation="Use parameterized queries.",
                            )
                        )
                        break  # Found vuln on this param, stop testing other engines/payloads

        return findings
