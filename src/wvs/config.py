import yaml
from pathlib import Path
import argparse
from typing import Any

class ConfigError(Exception):
    pass

def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Deep merge dict2 into dict1."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config(path: Path | None = None, cli_args: argparse.Namespace | None = None) -> dict[str, Any]:
    """Load config from default, user override, and CLI args."""
    
    # Base structure that must exist
    config = {
        "threads": 10,
        "timeout_seconds": 8,
        "rate_limit_per_second": 5,
        "user_agent": "WVS/0.1 (+https://github.com/zodrimon/web-vuln-scanner)",
        "crawl": {
            "max_depth": 3,
            "same_origin_only": True,
            "respect_robots_txt": True
        },
        "modules": ["sqli", "xss", "bruteforce"],
        "sqli": {
            "time_delay_seconds": 5
        },
        "bruteforce": {
            "wordlist": "wordlists/common_dirs.txt",
            "extensions": ["", ".php", ".bak", ".txt"]
        },
        "report": {
            "format": "html",
            "output_path": "wvs_report.html"
        }
    }
    
    default_config_path = Path("config/default_config.yaml")
    if default_config_path.exists():
        with open(default_config_path, "r") as f:
            default_yaml = yaml.safe_load(f) or {}
            config = deep_merge(config, default_yaml)
            
    if path and path.exists():
        with open(path, "r") as f:
            user_yaml = yaml.safe_load(f) or {}
            config = deep_merge(config, user_yaml)
            
    # CLI Overrides
    if cli_args:
        if hasattr(cli_args, "threads") and cli_args.threads is not None:
            config["threads"] = cli_args.threads
        if hasattr(cli_args, "modules") and cli_args.modules:
            config["modules"] = [m.strip() for m in cli_args.modules.split(",")]
        if hasattr(cli_args, "depth") and cli_args.depth is not None:
            config["crawl"]["max_depth"] = cli_args.depth
        if hasattr(cli_args, "wordlist") and cli_args.wordlist:
            config["bruteforce"]["wordlist"] = cli_args.wordlist
        if hasattr(cli_args, "output") and cli_args.output:
            config["report"]["output_path"] = cli_args.output
        if hasattr(cli_args, "format") and cli_args.format:
            config["report"]["format"] = cli_args.format
            
    # Validation
    required_keys = ["threads", "timeout_seconds", "rate_limit_per_second", "user_agent", "crawl", "modules", "sqli", "bruteforce", "report"]
    for key in required_keys:
        if key not in config:
            raise ConfigError(f"Missing required config key: {key}")
            
    return config
