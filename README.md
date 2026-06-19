# NOEMVEX-WEB-ARCHITECT v4.1 - ABSOLUTE VANGUARD EDITION
![Python](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/badge/License-MIT-grey) ![Focus](https://img.shields.io/badge/Focus-Stealth%20Recon-yellow) ![Type](https://img.shields.io/badge/Edition-Absolute%20Vanguard-cyan)

> **"Bypass the WAF, Map the Shadows."**
> Highly Stable Web & API Reconnaissance Suite. Engineered for JS decompilation, Zero-False-Positive secret hunting, and GDPR/PII exposure detection with Smart WAF Resilience.
> ⚠️ **Disclaimer:** This tool is for educational purposes and authorized security testing only.

---
## About
**NOEMVEX-WEB-ARCHITECT** is not a traditional brute-force scanner. Standard tools are instantly blocked by modern Web Application Firewalls (Cloudflare, AWS WAF). I built the Vanguard Engine to act less like a scanner and more like a legitimate browser. It silently maps the attack surface by decompiling client-side JavaScript, uncovering hidden API routes, and hunting for hardcoded secrets. 

Version 4.1 introduces the **CustomSSLAdapter (SECLEVEL=1)** coupled with an Exponential Backoff retry policy, guaranteeing stability against transient WAF blocks (429/5xx), and a **Zero-FP JWT Validator** to eliminate base64 noise in minified bundles.

## Capabilities
* **Smart WAF Resilience:** Custom SSL context with Exponential Backoff (Retry on 429/500/502/503/504) to survive aggressive rate limiting.
* **Zero-FP JWT Validation:** Cryptographic verification of JWT headers (`alg` claim and base64 padding) to eliminate false positives in minified React/Angular JS bundles.
* **Stealth Crawling:** Custom User-Agent pool and dynamic jitter (delay) to fly under the WAF radar.
* **Shadow API Discovery:** Extracts undocumented endpoints (`/api/v1/*`, `/graphql`, etc.) directly from the DOM and logic scripts.
* **Data Privacy Audit (PII):** Actively probes discovered endpoints for unauthorized access to sensitive user data (Emails, SSNs, Credit Cards, Passwords).
* **Executive Reporting:** Dumps findings into a structured JSON report with an aggregate Risk Score (0-100) for compliance tracking.

---
## Installation & Usage

    git clone https://github.com/noemvex/web-architect.git
    cd web-architect
    pip3 install -r requirements.txt

**Note:** Root privileges (`sudo`) are required for raw socket operations and potential OS-level network calls.

    Syntax:
    sudo python3 noemvex_architect.py -u <target_url> -t <threads> -d <delay>

    Example (Aggressive WAF Evasion):
    sudo python3 noemvex_architect.py -u https://vulnerable-api.com -t 10 -d 2.5

---
## Output Preview

    ███╗   ██╗ ██████╗ ███████╗███╗   ███╗██╗   ██╗███████╗██╗  ██╗
    ████╗  ██║██╔═══██╗██╔════╝████╗ ████║██║   ██║██╔════╝╚██╗██╔╝
    ██╔██╗ ██║██║   ██║█████╗  ██╔████╔██║██║   ██║█████╗   ╚███╔╝ 
    ██║╚██╗██║██║   ██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝██╔══╝   ██╔██╗ 
    ██║ ╚████║╚██████╔╝███████╗██║ ╚═╝ ██║ ╚████╔╝ ███████╗██╗  ██╗
    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
                   [ WEB ARCHITECT v4.1 - ABSOLUTE VANGUARD ]

    [*] Target Locked: https://vulnerable-api.com
    [*] Config: 10 Threads | Max Jitter: 2.5s

    ┏━ [PHASE 1]: Stealth Crawling & DOM Analysis
    ┃  [OK] Crawl complete. Mapped 42 pages and 8 JS bundles.
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ┏━ [PHASE 2]: Static Asset Decompilation (JS Analysis)
    ┃  [CRITICAL] Exposed Generic_Secret detected in app.min.js
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ┏━ [PHASE 3]: Active API Probing & PII Discovery
    ┃  Probing 12 discovered endpoints...
    ┃  [CRITICAL] PII Leak detected at /api/v1/user/profile
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    --- [ MISSION REPORT ] ---
    Overall Risk Score: 50/100
    [√] Intelligence archived: architect_report_vulnerable-api.com.json

---
## ⚠️ Compliance & Ghost Mode
**Regulatory Context:** This tool is specifically engineered to assist organizations in complying with European security regulations (GDPR & NIS2) by identifying unauthorized PII exposure before it leads to massive regulatory fines.

**Ghost Mode:** All commits to this repository are GPG signed and metadata is strictly managed. The author assumes no liability for unauthorized usage.

---
### Developer
**Emre 'noemvex' Sahin**
*Red Team Specialist & Security Architect*
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/emresahin-sec) [![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/noemvex)