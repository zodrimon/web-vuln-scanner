import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from rich.console import Console
from wvs.constants import VERSION, BANNER, DEFAULT_THREADS, DEFAULT_TIMEOUT
from wvs.config import load_config
from wvs.core.logger import get_logger, set_log_file
from wvs.core.authorization import confirm_authorized
from wvs.core.http_session import WvsSession
from wvs.crawler.crawler import Crawler
from wvs.core.plugin_registry import get_registered_scanners
from wvs.bruteforce.fuzzer import DirectoryFuzzer, load_wordlist
from wvs.report.report_builder import build_report
from wvs.report.markdown_report import render_markdown
from wvs.report.html_report import render_html

# Import scanners so they register themselves
import wvs.scanners.sqli.error_based
import wvs.scanners.sqli.time_based
import wvs.scanners.xss.reflected

logger = get_logger("wvs")
console = Console()

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wvs",
        description="Web Vulnerability Scanner (WVS) - Automated scanning and crawler."
    )
    parser.add_argument("--version", action="version", version=f"WVS v{VERSION}")
    parser.add_argument("--config", type=Path, help="Path to custom config YAML")
    parser.add_argument("--log-file", type=Path, help="Path to write debug logs")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run a full vulnerability scan")
    scan_parser.add_argument("target", help="Target URL (e.g. http://example.com/)")
    scan_parser.add_argument("--i-have-authorization", action="store_true", help="Confirm you have legal permission to scan the target")
    scan_parser.add_argument("--modules", nargs="+", help="Specific scanner modules to run (default: all)")
    scan_parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="Number of concurrent threads")
    scan_parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth")
    scan_parser.add_argument("--wordlist", type=Path, help="Wordlist for directory brute-forcing")
    scan_parser.add_argument("--output", type=Path, default=Path("wvs_report.html"), help="Path to save the report")
    scan_parser.add_argument("--format", choices=["markdown", "html"], default="html", help="Report format")
    
    # Crawl-only command
    crawl_parser = subparsers.add_parser("crawl-only", help="Crawl the target and discover endpoints without scanning")
    crawl_parser.add_argument("target", help="Target URL (e.g. http://example.com/)")
    crawl_parser.add_argument("--i-have-authorization", action="store_true", help="Confirm you have legal permission to crawl the target")
    crawl_parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth")
    crawl_parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="Number of concurrent threads")
    crawl_parser.add_argument("--output", type=Path, help="Path to save the discovered endpoints list")
    
    return parser

def run_scan(args) -> int:
    config = load_config(args.config)
    
    if not confirm_authorized(args.target, args.i_have_authorization):
        console.print("[red]Authorization not confirmed. Exiting.[/red]")
        return 1
        
    console.print(f"[cyan]Starting scan against {args.target}...[/cyan]")
    started_at = datetime.now()
    
    # Init session
    rate_limit = config.get("rate_limit_per_second")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)
    session = WvsSession("WVS", rate_limit_per_second=rate_limit or 10, timeout_seconds=timeout)
    
    # Crawl
    console.print("[yellow]Phase 1: Crawling...[/yellow]")
    crawler = Crawler(session, max_depth=args.depth)
    endpoints = crawler.crawl(args.target)
    console.print(f"[green]Found {len(endpoints)} endpoints.[/green]")
    
    # Scan
    findings = []
    registered_scanners = get_registered_scanners()
    scanners_to_run = []
    
    for scanner_cls in registered_scanners:
        scanner = scanner_cls()
        if not args.modules or scanner.name in args.modules:
            scanners_to_run.append(scanner)
            
    if not scanners_to_run:
        console.print("[red]No scanners selected or available. Exiting.[/red]")
        return 1
        
    console.print(f"[yellow]Phase 2: Scanning endpoints with {len(scanners_to_run)} module(s)...[/yellow]")
    for endpoint in endpoints:
        for scanner in scanners_to_run:
            logger.debug(f"Running {scanner.name} on {endpoint.url}")
            new_findings = scanner.scan(endpoint, session)
            findings.extend(new_findings)
            
    # Brute-force
    if args.wordlist and args.wordlist.exists():
        console.print("[yellow]Phase 3: Directory Brute-Forcing...[/yellow]")
        words = load_wordlist(args.wordlist)
        fuzzer = DirectoryFuzzer(session, threads=args.threads)
        extensions = config.get("bruteforce_extensions", ["php", "html"])
        bf_findings = fuzzer.fuzz(args.target, words, extensions)
        findings.extend(bf_findings)
        
    finished_at = datetime.now()
    console.print(f"\n[green]Scan completed in {(finished_at - started_at).total_seconds():.1f}s.[/green]")
    console.print(f"Total vulnerabilities found: [bold red]{len(findings)}[/bold red]")
    
    # Report
    console.print(f"[cyan]Generating {args.format} report to {args.output}...[/cyan]")
    result = build_report(args.target, started_at, finished_at, endpoints, findings)
    
    if args.format == "html":
        report_content = render_html(result)
    else:
        report_content = render_markdown(result)
        
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    return 0

def run_crawl_only(args) -> int:
    config = load_config(args.config)
    
    if not confirm_authorized(args.target, args.i_have_authorization):
        console.print("[red]Authorization not confirmed. Exiting.[/red]")
        return 1
        
    console.print(f"[cyan]Starting crawl against {args.target}...[/cyan]")
    
    rate_limit = config.get("rate_limit_per_second")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)
    session = WvsSession("WVS", rate_limit_per_second=rate_limit or 10, timeout_seconds=timeout)
    
    crawler = Crawler(session, max_depth=args.depth)
    endpoints = crawler.crawl(args.target)
    
    console.print(f"[green]Found {len(endpoints)} endpoints.[/green]")
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for ep in endpoints:
                f.write(f"[{ep.method}] {ep.url}\n")
        console.print(f"Saved to {args.output}")
    else:
        for ep in endpoints:
            print(f"[{ep.method}] {ep.url}")
            
    return 0

def main() -> int:
    print(BANNER)
    parser = build_arg_parser()
    args = parser.parse_args()
    
    if args.log_file:
        set_log_file(str(args.log_file))
        
    try:
        if args.command == "scan":
            return run_scan(args)
        elif args.command == "crawl-only":
            return run_crawl_only(args)
    except KeyboardInterrupt:
        console.print("\n[red]Process interrupted by user.[/red]")
        return 130
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {e}[/red]")
        logger.exception("Fatal error")
        return 1
        
    return 0
