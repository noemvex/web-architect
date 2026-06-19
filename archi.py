#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NOEMVEX-WEB-ARCHITECT v4.1 [ABSOLUTE VANGUARD EDITION]
Author: Emre 'noemvex' Sahin
Description: Highly Stable Web & API Reconnaissance Suite.
             Features Exponential Backoff, Zero-FP JWT Validation, and Smart WAF Resilience.
"""

import os
import requests
import re
import sys
import json
import time
import random
import argparse
import base64
import binascii
import urllib3
import ssl
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------------------
# UI CLASS
# ---------------------------------------------------------------------------
class UI:
    PURPLE = '\033[95m'
    CYAN   = '\033[96m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BOLD   = '\033[1m'
    GREY   = '\033[90m'
    END    = '\033[0m'

    @staticmethod
    def banner():
        ascii_art = [
            r"███╗   ██╗ ██████╗ ███████╗███╗   ███╗██╗   ██╗███████╗██╗  ██╗",
            r"████╗  ██║██╔═══██╗██╔════╝████╗ ████║██║   ██║██╔════╝╚██╗██╔╝",
            r"██╔██╗ ██║██║   ██║█████╗  ██╔████╔██║██║   ██║█████╗   ╚███╔╝ ",
            r"██║╚██╗██║██║   ██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝██╔══╝   ██╔██╗ ",
            r"██║ ╚████║╚██████╔╝███████╗██║ ╚═╝ ██║ ╚████╔╝ ███████╗██╗  ██╗",
            r"╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝"
        ]
        print(f"{UI.GREEN}{UI.BOLD}")
        for line in ascii_art:
            print(line)
        print(f"               {UI.PURPLE}[ WEB ARCHITECT v4.1 - ABSOLUTE VANGUARD ]{UI.END}\n")


# ---------------------------------------------------------------------------
# CUSTOM SSL ADAPTER  —  maximum target compatibility + exponential backoff
# ---------------------------------------------------------------------------
class CustomSSLAdapter(HTTPAdapter):
    """
    Mounts a relaxed SSL context (SECLEVEL=1, no cert verification) and
    couples it with urllib3 Retry using exponential back-off so that
    transient WAF 429/5xx responses are handled without crashing the scan.
    """

    def __init__(self, **kwargs):
        # Exponential backoff: waits 0s, 2s, 4s between retries
        retry_policy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
            raise_on_status=False,
        )
        super().__init__(max_retries=retry_policy, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


# ---------------------------------------------------------------------------
# CORE ENGINE
# ---------------------------------------------------------------------------
class WebArchitect:
    def __init__(self, target_url: str, threads: int, delay: float):
        self.target  = target_url if target_url.startswith("http") else f"https://{target_url}"
        self.domain  = urlparse(self.target).netloc
        self.threads = threads
        self.delay   = delay

        self._ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent":                random.choice(self._ua_pool),
            "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":           "en-US,en;q=0.5",
            "Connection":                "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

        _adapter = CustomSSLAdapter()
        self.session.mount("http://",  _adapter)
        self.session.mount("https://", _adapter)

        self.crawled_urls  : set  = set()
        self.js_assets     : set  = set()
        self.api_endpoints : set  = set()
        self.findings      : list = []
        self.risk_score    : int  = 0

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _log_finding(self, severity: str, category: str, message: str) -> None:
        self.findings.append({"severity": severity, "category": category, "message": message})
        weight = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 5}
        self.risk_score += weight.get(severity, 0)

    def _apply_jitter(self) -> None:
        if self.delay > 0:
            time.sleep(random.uniform(0.5, self.delay))

    def _stealth_request(
        self, url: str, timeout: int = 15
    ) -> requests.Response | None:
        """
        Single GET with explicit exception handling.
        The adapter already handles retries + backoff internally;
        this layer only catches hard failures (DNS, TLS, timeout)
        and logs a [WARN] without raising or calling sys.exit().
        """
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            return response
        except requests.exceptions.SSLError as exc:
            print(f"{UI.YELLOW}┃  [WARN] SSL handshake failed for {url}: {exc}{UI.END}")
        except requests.exceptions.ConnectionError as exc:
            print(f"{UI.YELLOW}┃  [WARN] Connection error for {url}: {exc}{UI.END}")
        except requests.exceptions.Timeout:
            print(f"{UI.YELLOW}┃  [WARN] Request timed out: {url}{UI.END}")
        except requests.exceptions.RequestException as exc:
            print(f"{UI.YELLOW}┃  [WARN] Unexpected request failure for {url}: {type(exc).__name__} — {str(exc)[:80]}{UI.END}")
        return None

    # ------------------------------------------------------------------
    # ZERO FALSE-POSITIVE JWT VALIDATOR
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_jwt(token: str) -> bool:
        """
        Validates a JWT candidate by:
          1. Confirming the structural three-part dot-separated format.
          2. Confirming the header starts with 'eyJ' (base64 of '{').
          3. Decoding the header with correct padding and verifying the
             presence of the mandatory 'alg' claim.
        Returns False on any malformed base64 (e.g. SVG data-URIs).
        """
        parts = token.split(".")
        if len(parts) != 3:
            return False
        header_segment = parts[0]
        if not header_segment.startswith("eyJ"):
            return False
        # Re-pad to a multiple of 4 to avoid binascii.Error
        padding  = "=" * (-len(header_segment) % 4)
        try:
            decoded = base64.b64decode(header_segment + padding).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return False
        try:
            header_obj = json.loads(decoded)
        except json.JSONDecodeError:
            return False
        # Must contain 'alg' — the single mandatory JOSE header parameter
        return "alg" in header_obj

    # ------------------------------------------------------------------
    # PHASE 1 — STEALTH CRAWL
    # ------------------------------------------------------------------
    def phase_crawl_target(self) -> None:
        print(f"{UI.CYAN}┏━ [PHASE 1]: Stealth Crawling & DOM Analysis{UI.END}")
        self._apply_jitter()
        res = self._stealth_request(self.target)

        if not res:
            print(f"{UI.RED}┃  [ERR] FATAL: Cannot reach target. Aborting crawl phase.{UI.END}")
            print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")
            return

        soup = BeautifulSoup(res.text, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                full_url = urljoin(self.target, href)
                if self.domain in full_url:
                    self.crawled_urls.add(full_url)

        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                self.js_assets.add(urljoin(self.target, src))

        print(
            f"{UI.GREEN}┃  [OK] Crawl complete. "
            f"Mapped {len(self.crawled_urls)} pages and {len(self.js_assets)} JS bundles.{UI.END}"
        )
        print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

    # ------------------------------------------------------------------
    # PHASE 2 — JS STATIC ANALYSIS
    # ------------------------------------------------------------------
    def _analyze_javascript(self, js_url: str) -> None:
        self._apply_jitter()
        res = self._stealth_request(js_url, timeout=10)
        if not res:
            return

        content = res.text
        js_name = js_url.split("/")[-1]

        secret_patterns: dict[str, str] = {
            "AWS_Access_Key":  r"(?i)AKIA[0-9A-Z]{16}",
            "Stripe_Live_Key": r"(?i)(sk_live_[0-9a-zA-Z]{24})",
            "Generic_Secret":  r"(?i)(?:api_key|secret|token)\s*[:=]\s*[\"']([a-zA-Z0-9\-_]{24,})[\"']",
            "JWT_Token":       r"eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+",
        }

        for label, pattern in secret_patterns.items():
            for match in set(re.findall(pattern, content)):
                candidate = match if isinstance(match, str) else match[0]
                if label == "JWT_Token" and not self._validate_jwt(candidate):
                    continue  # Discard SVG artefacts and malformed base64 blobs
                msg = f"Exposed {label} detected in {js_name}"
                print(f"{UI.RED}┃  [CRITICAL] {msg}{UI.END}")
                self._log_finding("CRITICAL", "Secret Exposure", msg)

        route_pattern = re.compile(
            r'["\'](/api/[^\s"\']+|/rest/[^\s"\']+|/v[0-9]/[^\s"\']+|/graphql[^\s"\']*)["\']'
        )
        for route in set(route_pattern.findall(content)):
            self.api_endpoints.add(route)

    # ------------------------------------------------------------------
    # PHASE 3 — ACTIVE API PROBING
    # ------------------------------------------------------------------
    def _probe_endpoint(self, endpoint: str) -> None:
        full_url = f"{self.target.rstrip('/')}{endpoint}"
        self._apply_jitter()
        res = self._stealth_request(full_url, timeout=10)

        if res and res.status_code == 200:
            content_type = res.headers.get("Content-Type", "").lower()
            if "application/json" in content_type:
                pii_signatures = ['"email":', '"phone":', '"ssn":', '"credit_card":', '"password":']
                if any(sig in res.text.lower() for sig in pii_signatures):
                    msg = f"PII Leak detected at {endpoint}"
                    print(f"{UI.RED}┃  [CRITICAL] {msg}{UI.END}")
                    self._log_finding("CRITICAL", "GDPR/PII Violation", msg)
                else:
                    msg = f"Unauthenticated JSON API access at {endpoint}"
                    print(f"{UI.YELLOW}┃  [WARN] {msg}{UI.END}")
                    self._log_finding("MEDIUM", "BOLA Risk", msg)

    # ------------------------------------------------------------------
    # ORCHESTRATION
    # ------------------------------------------------------------------
    def execute_analysis(self) -> None:
        if not self.js_assets:
            return

        print(f"{UI.CYAN}┏━ [PHASE 2]: Static Asset Decompilation (JS Analysis){UI.END}")
        with ThreadPoolExecutor(max_workers=self.threads) as pool:
            pool.map(self._analyze_javascript, self.js_assets)
        print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

        if self.api_endpoints:
            print(f"{UI.CYAN}┏━ [PHASE 3]: Active API Probing & PII Discovery{UI.END}")
            print(f"{UI.GREY}┃  Probing {len(self.api_endpoints)} discovered endpoints...{UI.END}")
            with ThreadPoolExecutor(max_workers=self.threads) as pool:
                pool.map(self._probe_endpoint, self.api_endpoints)
            print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

    # ------------------------------------------------------------------
    # REPORT
    # ------------------------------------------------------------------
    def generate_report(self) -> None:
        self.risk_score = min(self.risk_score, 100)
        report_data = {
            "target":    self.target,
            "timestamp": datetime.now().isoformat(),
            "risk_score": self.risk_score,
            "metrics": {
                "pages_crawled":       len(self.crawled_urls),
                "js_analyzed":         len(self.js_assets),
                "api_endpoints_found": len(self.api_endpoints),
            },
            "findings": self.findings,
        }
        filename = f"architect_report_{self.domain}.json"
        try:
            with open(filename, "w") as fh:
                json.dump(report_data, fh, indent=4)
            score_color = UI.RED if self.risk_score > 50 else UI.GREEN
            print(f"{UI.BOLD}--- [ MISSION REPORT ] ---{UI.END}")
            print(f"Overall Risk Score: {score_color}{self.risk_score}/100{UI.END}")
            print(f"{UI.GREEN}[√] Intelligence archived: {filename}{UI.END}")
        except IOError as exc:
            print(f"{UI.RED}[!] Could not write report to disk: {exc}{UI.END}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if os.geteuid() != 0:
        sys.exit(1)

    UI.banner()

    parser = argparse.ArgumentParser(
        description="NOEMVEX Web Architect — Offensive Web Reconnaissance Suite"
    )
    parser.add_argument("-u", "--url",     required=True,            help="Target URL")
    parser.add_argument("-t", "--threads", type=int,   default=5,    help="Worker threads (default: 5)")
    parser.add_argument("-d", "--delay",   type=float, default=0.0,  help="Max jitter delay in seconds (default: 0.0)")
    args = parser.parse_args()

    print(f"{UI.BOLD}[*] Target Locked: {args.url}{UI.END}")
    print(f"{UI.GREY}[*] Config: {args.threads} Threads | Max Jitter: {args.delay}s{UI.END}\n")

    engine = WebArchitect(args.url, args.threads, args.delay)
    engine.phase_crawl_target()

    if engine.crawled_urls or engine.js_assets:
        engine.execute_analysis()

    engine.generate_report()
