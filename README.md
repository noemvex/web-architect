# NOEMVEX-WEB-ARCHITECT v1.0 [VANGUARD EDITION]
![Python](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/badge/License-MIT-grey) ![Focus](https://img.shields.io/badge/Focus-Stealth%20Recon-yellow) ![Type](https://img.shields.io/badge/Edition-Vanguard%20Edition-red)

> **"Bypass the WAF, Map the Shadows."**
> Advanced stealth web reconnaissance and API auditing suite. Engineered for JS decompilation, secret hunting, and GDPR/PII exposure detection.
> ⚠️ **Disclaimer:** This tool is for educational purposes and authorized security testing only.

---
## About
**NOEMVEX-WEB-ARCHITECT** is not a traditional brute-force scanner. Standard tools are instantly blocked by modern Web Application Firewalls (Cloudflare, AWS WAF). I built the Vanguard Engine to act less like a scanner and more like a legitimate browser. It silently maps the attack surface by decompiling client-side JavaScript, uncovering hidden API routes, and hunting for hardcoded secrets without triggering basic rate limits.

## Capabilities
* **Stealth Crawling:** Custom User-Agent pool and dynamic jitter (delay) to fly under the WAF radar.
* **JS Decompilation:** Automated hunting for AWS keys, Stripe tokens, and JWTs within minified JavaScript bundles.
* **Shadow API Discovery:** Extracts undocumented endpoints directly from the DOM and logic scripts.
* **Data Privacy Audit (PII):** Actively probes discovered endpoints for unauthorized access to sensitive user data (Emails, SSNs, Credit Cards).
* **Corporate Reporting:** Dumps findings into a structured JSON report suitable for executive briefings and compliance checks.

---
## Usage

### 1. Requirements
Ensure you have Python 3.x installed on your system.
pip3 install -r requirements.txt

### 2. Execution
Run the tool using the following command structure. Highly recommend using the --delay flag if you are dealing with aggressive WAFs.

Syntax:
python3 noemvex_architect.py -u <target_url> -t <threads> -d <delay>

Example:
python3 noemvex_architect.py -u https://example.com -t 10 -d 2.5

---
## Output Preview

    ███╗   ██╗ ██████╗ ███████╗███╗   ███╗██╗   ██╗███████╗██╗  ██╗
    ████╗  ██║██╔═══██╗██╔════╝████╗ ████║██║   ██║██╔════╝╚██╗██╔╝
    ██╔██╗ ██║██║   ██║█████╗  ██╔████╔██║██║   ██║█████╗   ╚███╔╝ 
    ██║╚██╗██║██║   ██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝██╔══╝   ██╔██╗ 
    ██║ ╚████║╚██████╔╝███████╗██║ ╚═╝ ██║ ╚████╔╝ ███████╗██╗  ██╗
    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
                   [ WEB ARCHITECT v1.0 - VANGUARD EDITION ]

    [*] Target Locked: https://vulnerable-api.com
    [*] Config: 10 Threads | Max Jitter: 2.5s

    ┏━ [PHASE 1]: Stealth Crawling & DOM Analysis
    ┃  [OK] Crawl Complete. Mapped 42 pages and 8 JS bundles.
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ┏━ [PHASE 2]: Static Asset Decompilation (JS Analysis)
    ┃  [CRITICAL] Exposed AWS_Access_Key detected in app.min.js
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ┏━ [PHASE 3]: Active API Probing & PII Discovery
    ┃  Probing 12 discovered endpoints...
    ┃  [CRITICAL] Data Exposure (PII Leak) detected at /api/v1/user/profile
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    --- [ MISSION REPORT ] ---
    Overall Risk Score: 85/100
    [√] Intelligence archived: architect_report_vulnerable-api.com.json

---
## Known Issues & Tech Debt
* **False Positives on JWT:** The regex sometimes catches long, random base64 strings in minified React apps. Need to refine the entropy logic in upcoming releases.
* **Single Page Applications (SPAs):** Relies on BeautifulSoup right now. Planning to integrate a headless browser module for deep DOM rendering.

---
## ⚠️ Compliance & Ghost Mode
**Regulatory Context:** This tool is specifically engineered to assist organizations in complying with European security regulations (GDPR & NIS2) by identifying unauthorized PII exposure before it leads to massive regulatory fines.

**Ghost Mode:** All commits to this repository are GPG signed and metadata is strictly managed. The author assumes no liability for unauthorized usage.

---
### Developer
**Emre 'noemvex' Sahin**
*Red Team Specialist & Security Architect*
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/emresahin-sec) [![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/noemvex)
