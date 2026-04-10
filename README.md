# NOEMVEX-WEB-ARCHITECT v1.0
## [ STEALTH WEB RECON & API AUDITOR ]

Author: Emre 'noemvex' Sahin
Version: 1.0 (Vanguard Edition)
License: MIT
Category: Red Team / Offensive Security / Reconnaissance

### WHY I BUILT THIS (THE PROBLEM)
During recent engagements, standard tools (like SQLMap or generic fuzzers) were instantly getting blocked by modern WAFs (Cloudflare, AWS WAF). I needed a tool that acts less like a brute-forcer and more like a browser. Web Architect was built to silently map the attack surface by decompiling client-side JavaScript, uncovering hidden API routes, and hunting for hardcoded secrets without triggering basic rate limits.

### KEY FEATURES
- Stealth Crawling: Custom User-Agent pool and dynamic jitter (delay) to fly under the WAF radar.
- JS Decompilation: Automated hunting for AWS keys, Stripe tokens, and JWTs within minified JavaScript bundles.
- Shadow API Discovery: Extracts undocumented endpoints directly from the DOM and logic scripts.
- Data Privacy Audit (PII): Actively probes discovered endpoints for unauthorized access to sensitive user data (Emails, SSNs, Credit Cards) - crucial for GDPR compliance checks.
- Corporate Reporting: Dumps findings into a structured JSON report suitable for executive briefings.

### KNOWN ISSUES & TECH DEBT (v1.0)
No tool is perfect. Here is what I am planning to fix in upcoming releases:
- False Positives on JWT: The regex sometimes catches long, random base64 strings in minified React apps. Need to refine the entropy logic.
- Heavily Obfuscated JS: If the target uses extreme JS obfuscation, the regex engine might miss some hidden endpoints.
- Single Page Applications (SPAs): Relies on BS4 right now. Planning to integrate a headless browser module in v1.2 for deep DOM rendering.

### INSTALLATION
Ensure you have Python 3.9+ installed on your system.

1. Clone the repository:
   git clone https://github.com/noemvex/web-architect.git
   cd web-architect

2. Install dependencies:
   pip3 install -r requirements.txt

### USAGE
Run the tool using the following command structure. Highly recommend using the --delay flag if you are dealing with aggressive WAFs.

Syntax:
python3 noemvex_architect.py -u <target_url> -t <threads> -d <delay>

Example Execution:
python3 noemvex_architect.py -u https://target-app.com -t 10 -d 2.5

Arguments:
-u, --url       (Required) Target URL to analyze.
-t, --threads   (Optional) Concurrent worker threads. Default: 5.
-d, --delay     (Optional) Random delay (jitter) between requests to evade detection. Default: 0.0.

### OUTPUT PREVIEW
The tool provides a structured, color-coded terminal output followed by a comprehensive JSON audit report.

[*] Target Locked: https://vulnerable-api.com
[*] Config: 10 Threads | Max Jitter: 2.5s

┏━ [PHASE 1]: Stealth Crawling & DOM Analysis
┃  [OK] Crawl Complete. Mapped 42 pages and 8 JS bundles.
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━ [PHASE 2]: Static Asset Decompilation (JS Analysis)
┃  [CRITICAL] Exposed AWS_Access_Key detected in app.min.js
┃  [CRITICAL] Exposed JWT_Token detected in auth-service.js
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━ [PHASE 3]: Active API Probing & PII Discovery
┃  Probing 12 discovered endpoints...
┃  [CRITICAL] Data Exposure (PII Leak) detected at /api/v1/user/profile
┃  [WARN] Unauthenticated API Access at /api/v2/internal/config
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

--- [ MISSION REPORT ] ---
Overall Risk Score: 85/100
[√] Intelligence archived: architect_report_vulnerable-api.com.json

### COMPLIANCE & REGULATORY CONTEXT
This tool is specifically engineered to assist organizations in complying with European security regulations:
- GDPR: Identifies unauthorized PII exposure before it leads to regulatory fines.
- NIS2 Directive: Supports automated security monitoring and asset discovery for critical infrastructure.

### DISCLAIMER & GHOST MODE
This tool is for educational purposes and authorized penetration testing only. All commits to this repository are signed and metadata is strictly managed. The author, Emre 'noemvex' Sahin, assumes no liability for unauthorized usage.
