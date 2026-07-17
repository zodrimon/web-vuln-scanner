import argparse
from pathlib import Path
import pytest
from wvs.config import load_config, ConfigError

def test_load_config_with_overrides(tmp_path):
    # Setup user yaml override
    user_config_path = tmp_path / "user_config.yaml"
    user_config_content = """
threads: 20
crawl:
  max_depth: 5
report:
  format: markdown
"""
    user_config_path.write_text(user_config_content)
    
    # Setup CLI args
    cli_args = argparse.Namespace(
        threads=50,
        modules="sqli,xss",
        depth=None,
        wordlist=None,
        output="custom_report.md",
        format=None
    )
    
    config = load_config(path=user_config_path, cli_args=cli_args)
    
    # Assertions
    assert config["threads"] == 50  # CLI should win
    assert config["crawl"]["max_depth"] == 5 # User YAML should win over default
    assert config["report"]["format"] == "markdown" # User YAML should win
    assert config["report"]["output_path"] == "custom_report.md" # CLI win
    assert config["modules"] == ["sqli", "xss"] # CLI win
    assert config["timeout_seconds"] == 8 # Default fallback
