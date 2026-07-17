import pytest
from wvs.bruteforce.status_filter import should_report

def test_should_report_hard_404():
    # Hard 404 should be ignored
    assert should_report(status_code=404, response_size=100, ignore_codes={404}) == False
    
def test_should_report_200_ok():
    # Regular 200 should be reported
    assert should_report(status_code=200, response_size=5000, ignore_codes={404}) == True
    
def test_should_report_ignored_codes():
    # Ignored 403 should be ignored
    assert should_report(status_code=403, response_size=200, ignore_codes={404, 403}) == False
    # Not ignored 403 should be reported
    assert should_report(status_code=403, response_size=200, ignore_codes={404}) == True

def test_should_report_soft_404():
    # Baseline size is 1000. 
    # A 200 response of size 1005 should be treated as a soft 404.
    assert should_report(status_code=200, response_size=1005, ignore_codes={404}, baseline_404_size=1000) == False
    
    # A 200 response of size 1050 should be treated as a soft 404.
    assert should_report(status_code=200, response_size=1050, ignore_codes={404}, baseline_404_size=1000) == False
    
    # A 200 response of size 1051 should NOT be treated as a soft 404 (outside 5% margin).
    assert should_report(status_code=200, response_size=1051, ignore_codes={404}, baseline_404_size=1000) == True
    
    # A 200 response of size 5000 is clearly a real page.
    assert should_report(status_code=200, response_size=5000, ignore_codes={404}, baseline_404_size=1000) == True
