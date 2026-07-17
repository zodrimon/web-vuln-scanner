import pytest
import sys
from wvs.core.authorization import confirm_authorized

def test_confirm_authorized_flag_true():
    assert confirm_authorized("http://example.com", True) == True

def test_confirm_authorized_no_tty(monkeypatch):
    # Mock sys.stdout.isatty to False
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert confirm_authorized("http://example.com", False) == False

def test_confirm_authorized_tty_yes(monkeypatch):
    # Mock sys.stdout.isatty to True
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    # Mock input to return 'y'
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm_authorized("http://example.com", False) == True

def test_confirm_authorized_tty_no(monkeypatch):
    # Mock sys.stdout.isatty to True
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    # Mock input to return 'n'
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert confirm_authorized("http://example.com", False) == False
