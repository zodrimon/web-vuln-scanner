from abc import ABC, abstractmethod
from wvs.core.models import Endpoint, Finding
from wvs.core.http_session import WvsSession

class BaseScanner(ABC):
    """Abstract base class for all scanner plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the scanner module (e.g. 'sqli', 'xss')."""
        pass
        
    @property
    @abstractmethod
    def severity_default(self) -> str:
        """The default severity if a finding is generated (e.g. 'high', 'medium')."""
        pass
        
    @abstractmethod
    def scan(self, endpoint: Endpoint, session: WvsSession) -> list[Finding]:
        """
        Scan an endpoint and return a list of Findings.
        This is called once per endpoint discovered by the crawler.
        """
        pass
