#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NOEMVEX-WEB-ARCHITECT v1.0
Author: Emre 'noemvex' Sahin
Description: Stealth Web & API Reconnaissance Suite. 
             Combines DOM crawling, JS decompilation, Secret Hunting, and PII/BOLA detection.
             Engineered for WAF evasion.
"""

import requests
import re
import sys
import json
import time
import random
import argparse
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# --- STANDARD UI CLASS (Unified Noemvex Design System) ---
class UI:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    GREY = '\033[90m'
    END = '\033[0m'

    @staticmethod
    def banner():
        # Raw string (r"") 
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
        print(f"               {UI.PURPLE}[ WEB ARCHITECT v1.0 - VANGUARD EDITION ]{UI.END}\n")

class WebArchitect:
    def __init__(self, target_url, threads, delay):
        self.target = target_url if target_url.startswith('http') else f'https://{target_url}'
        self.domain = urlparse(self.target).netloc
        self.threads = threads
        self.delay = delay
        
        # User-Agent Pool to avoid basic WAF signature matching
        self.ua_pool = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.ua_pool),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        self.crawled_urls = set()
        self.js_assets = set()
        self.api_endpoints = set()
        self.findings = []
        self.risk_score = 0

    def log_finding(self, severity, category, message):
        """Standardized corporate logging mechanism for JSON reporting."""
        self.findings.append({
            "severity": severity,
            "category": category,
            "message": message
        })
        # Score calculation
        if severity == "CRITICAL": self.risk_score += 25
        elif severity == "HIGH": self.risk_score += 15
        elif severity == "MEDIUM": self.risk_score += 5

    def apply_jitter(self):
        """Adds a random delay to bypass rate-limiting WAF rules."""
        if self.delay > 0:
            jitter = random.uniform(0.5, self.delay)
            time.sleep(jitter)

    def phase_crawl_target(self):
        """Phase 1: Deep Spidering & Asset Extraction."""
        print(f"{UI.CYAN}┏━ [PHASE 1]: Stealth Crawling & DOM Analysis{UI.END}")
        try:
            self.apply_jitter()
            # Note: 15s timeout is crucial here. Heavy targets drop connections often.
            res = self.session.get(self.target, timeout=15)
            
            # Using BS4 instead of raw Regex because dynamically loaded SPAs break regex easily.
            soup = BeautifulSoup(res.text, 'html.parser')

            # Extract internal links
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(self.target, href)
                    if self.domain in full_url:
                        self.crawled_urls.add(full_url)

            # Extract JavaScript bundles (This is the goldmine)
            for script in soup.find_all('script'):
                src = script.get('src')
                if src:
                    js_url = urljoin(self.target, src)
                    self.js_assets.add(js_url)

            print(f"{UI.GREEN}┃  [OK] Crawl Complete. Mapped {len(self.crawled_urls)} pages and {len(self.js_assets)} JS bundles.{UI.END}")

        except requests.exceptions.Timeout:
            print(f"{UI.RED}┃  [ERR] Connection timed out. Target might be blocking us or is overloaded.{UI.END}")
            sys.exit(1)
        except Exception as e:
            print(f"{UI.RED}┃  [ERR] Unexpected error during crawl: {str(e)}{UI.END}")
            sys.exit(1)
            
        print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

    def analyze_javascript(self, js_url):
        """Phase 2 Worker: Hunts for Hardcoded Secrets and Hidden API Routes."""
        try:
            self.apply_jitter()
            res = self.session.get(js_url, timeout=10)
            content = res.text
            js_name = js_url.split('/')[-1]

            # Heuristic Secret Patterns
            # TODO: Refine JWT pattern in v1.2. False positive rate is currently annoying on minified React apps.
            patterns = {
                "AWS_Access_Key": r'(?i)AKIA[0-9A-Z]{16}',
                "Stripe_Key": r'(?i)(sk_live_[0-9a-zA-Z]{24})',
                "Generic_Secret": r'(?i)(?:api_key|secret|token|password)\s*[:=]\s*["\']([a-zA-Z0-9\-_]{16,})["\']',
                "JWT_Token": r'ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            }

            for key, pattern in patterns.items():
                matches = re.findall(pattern, content)
                for match in matches:
                    if key == "JWT_Token" and len(match) < 30: 
                        continue # Skip short garbage matches
                    
                    msg = f"Exposed {key} detected in {js_name}"
                    print(f"{UI.RED}┃  [CRITICAL] {msg}{UI.END}")
                    self.log_finding("CRITICAL", "Secret Exposure", msg)

            # Extract Hidden API Routes
            route_pattern = re.compile(r'["\'](/api/.*?|/v[0-9]/.*?|/graphql.*?)["\']')
            routes = route_pattern.findall(content)
            for route in routes:
                self.api_endpoints.add(route)

        except requests.exceptions.RequestException:
            pass # Silently skip unreachable JS files to reduce terminal noise

    def probe_endpoint(self, endpoint):
        """Phase 3 Worker: Passive BOLA and PII Exposure Analysis."""
        full_url = f"{self.target.rstrip('/')}{endpoint}"
        try:
            self.apply_jitter()
            res = self.session.get(full_url, timeout=10)
            
            if res.status_code == 200:
                # Analyze response body for PII
                # FIXME: Add regex for credit cards instead of static strings.
                pii_signatures = ['"email":', '"phone":', '"ssn":', '"credit_card":', '"password":']
                
                if any(sig in res.text.lower() for sig in pii_signatures):
                    msg = f"Data Exposure (PII Leak) detected at {endpoint}"
                    print(f"{UI.RED}┃  [CRITICAL] {msg}{UI.END}")
                    self.log_finding("CRITICAL", "GDPR/PII Violation", msg)
                else:
                    msg = f"Unauthenticated API Access at {endpoint}"
                    print(f"{UI.YELLOW}┃  [WARN] {msg}{UI.END}")
                    self.log_finding("MEDIUM", "BOLA Risk", msg)
                    
        except requests.exceptions.RequestException:
            pass

    def execute_analysis(self):
        print(f"{UI.CYAN}┏━ [PHASE 2]: Static Asset Decompilation (JS Analysis){UI.END}")
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.analyze_javascript, self.js_assets)
        print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

        print(f"{UI.CYAN}┏━ [PHASE 3]: Active API Probing & PII Discovery{UI.END}")
        if not self.api_endpoints:
            print(f"{UI.GREY}┃  No explicit API routes found in JS sources. Developer did a good job hiding them.{UI.END}")
        else:
            print(f"{UI.GREY}┃  Probing {len(self.api_endpoints)} discovered endpoints...{UI.END}")
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                executor.map(self.probe_endpoint, self.api_endpoints)
        print(f"{UI.CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{UI.END}\n")

    def generate_report(self):
        """Compiles findings into a Corporate Pentest standard JSON report."""
        self.risk_score = min(self.risk_score, 100)
        report_data = {
            "target": self.target,
            "timestamp": datetime.now().isoformat(),
            "regulatory_context": "Checks performed align with GDPR Data Privacy and NIS2 Security Standards.",
            "risk_score": self.risk_score,
            "metrics": {
                "pages_crawled": len(self.crawled_urls),
                "js_analyzed": len(self.js_assets),
                "api_endpoints_found": len(self.api_endpoints)
            },
            "findings": self.findings
        }
        
        filename = f"architect_report_{self.domain}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=4)

            print(f"{UI.BOLD}--- [ MISSION REPORT ] ---{UI.END}")
            score_color = UI.RED if self.risk_score > 50 else UI.GREEN
            print(f"Overall Risk Score: {score_color}{self.risk_score}/100{UI.END}")
            print(f"{UI.GREEN}[√] Intelligence archived: {filename}{UI.END}")
        except IOError as e:
            print(f"{UI.RED}[!] Could not write report to disk: {str(e)}{UI.END}")

if __name__ == "__main__":
    UI.banner()
    
    parser = argparse.ArgumentParser(description="NOEMVEX WEB ARCHITECT - Advanced Stealth Recon Suite")
    parser.add_argument('-u', '--url', required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument('-t', '--threads', type=int, default=5, help="Number of concurrent threads (Default: 5)")
    parser.add_argument('-d', '--delay', type=float, default=0.0, help="Max random delay between requests in seconds to bypass WAF (Default: 0.0)")
    
    args = parser.parse_args()
    
    print(f"{UI.BOLD}[*] Target Locked: {args.url}{UI.END}")
    print(f"{UI.GREY}[*] Config: {args.threads} Threads | Max Jitter: {args.delay}s{UI.END}\n")
    
    engine = WebArchitect(args.url, args.threads, args.delay)
    engine.phase_crawl_target()
    engine.execute_analysis()
    engine.generate_report()