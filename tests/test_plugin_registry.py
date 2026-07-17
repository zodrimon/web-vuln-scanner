import pytest
from wvs.core.plugin_registry import register_scanner, get_registered_scanners, _SCANNERS

@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before and after tests."""
    _SCANNERS.clear()
    yield
    _SCANNERS.clear()

def test_register_and_get_scanners():
    @register_scanner
    class DummyScanner1:
        pass
        
    @register_scanner
    class DummyScanner2:
        pass
        
    scanners = get_registered_scanners()
    
    assert len(scanners) == 2
    assert DummyScanner1 in scanners
    assert DummyScanner2 in scanners
