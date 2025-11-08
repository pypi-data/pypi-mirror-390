"""
Alprina Report Generator - Creates markdown security reports in .alprina/ folder.
Generates comprehensive, professional security documentation.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger


def generate_security_reports(scan_results: dict, target_path: str, agent_type: str = "generic"):
    """
    Generate comprehensive security reports in .alprina/ folder.

    Creates:
    - SECURITY-REPORT.md: Full vulnerability analysis
    - FINDINGS.md: Detailed findings with code snippets
    - REMEDIATION.md: Step-by-step fix instructions
    - EXECUTIVE-SUMMARY.md: Non-technical overview
    - Agent-specific specialized reports (if applicable)

    Args:
        scan_results: Results from security scan
        target_path: Path where scan was performed
        agent_type: Type of agent that performed scan (for specialized reports)
    """
    try:
        # Determine report directory
        if os.path.isdir(target_path):
            report_dir = Path(target_path) / ".alprina"
        else:
            # If target is a file, use parent directory
            report_dir = Path(target_path).parent / ".alprina"

        # Create .alprina directory
        report_dir.mkdir(exist_ok=True)
        logger.info(f"Creating security reports in: {report_dir}")

        # Generate standard report files
        _generate_security_report(scan_results, report_dir)
        _generate_findings_report(scan_results, report_dir)
        _generate_remediation_report(scan_results, report_dir)
        _generate_executive_summary(scan_results, report_dir)

        # Generate agent-specific specialized reports
        if agent_type in SPECIALIZED_REPORT_GENERATORS:
            logger.info(f"Generating specialized {agent_type} report")
            generator = SPECIALIZED_REPORT_GENERATORS[agent_type]
            generator(scan_results, report_dir)

        logger.info("✓ Security reports generated successfully")
        return str(report_dir)

    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        raise


def _generate_security_report(results: dict, output_dir: Path):
    """Generate SECURITY-REPORT.md - Full vulnerability analysis."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Count findings by severity
    severity_counts = {
        "CRITICAL": len([f for f in findings if f.get("severity") == "CRITICAL"]),
        "HIGH": len([f for f in findings if f.get("severity") == "HIGH"]),
        "MEDIUM": len([f for f in findings if f.get("severity") == "MEDIUM"]),
        "LOW": len([f for f in findings if f.get("severity") == "LOW"]),
        "INFO": len([f for f in findings if f.get("severity") == "INFO"]),
    }

    report = f"""# 🔒 Alprina Security Report

**Generated:** {scan_date}
**Target:** {results.get('target', 'N/A')}
**Scan Mode:** {results.get('mode', 'N/A')}
**Profile:** {results.get('profile', 'default')}
**Files Scanned:** {results.get('files_scanned', 0)}

---

## 📊 Executive Summary

Total security findings: **{len(findings)}**

### Severity Distribution

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | {severity_counts['CRITICAL']} |
| 🟠 HIGH | {severity_counts['HIGH']} |
| 🟡 MEDIUM | {severity_counts['MEDIUM']} |
| 🔵 LOW | {severity_counts['LOW']} |
| ⚪ INFO | {severity_counts['INFO']} |

---

## 🎯 Risk Assessment

"""

    # Risk level determination
    if severity_counts['CRITICAL'] > 0:
        risk_level = "🔴 **CRITICAL RISK**"
        risk_desc = "Immediate action required. Critical vulnerabilities detected that could lead to system compromise."
    elif severity_counts['HIGH'] > 0:
        risk_level = "🟠 **HIGH RISK**"
        risk_desc = "Urgent attention needed. High-severity vulnerabilities require prompt remediation."
    elif severity_counts['MEDIUM'] > 0:
        risk_level = "🟡 **MEDIUM RISK**"
        risk_desc = "Moderate security concerns detected. Address these issues in your next development cycle."
    elif severity_counts['LOW'] > 0:
        risk_level = "🔵 **LOW RISK**"
        risk_desc = "Minor security issues detected. Consider addressing these during regular maintenance."
    else:
        risk_level = "🟢 **NO ISSUES**"
        risk_desc = "No security vulnerabilities detected. Your code follows security best practices!"

    report += f"""**Overall Risk Level:** {risk_level}

{risk_desc}

---

## 🔍 Detailed Findings

"""

    # Group findings by severity
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        severity_findings = [f for f in findings if f.get("severity") == severity]

        if severity_findings:
            severity_icons = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🔵",
                "INFO": "⚪"
            }

            report += f"\n### {severity_icons[severity]} {severity} Severity ({len(severity_findings)} issues)\n\n"

            for i, finding in enumerate(severity_findings, 1):
                report += f"""#### {i}. {finding.get('type', 'Security Issue')}

**Location:** `{finding.get('location', 'N/A')}`
"""
                if finding.get('line'):
                    report += f"**Line:** {finding.get('line')}  \n"

                report += f"""**Description:** {finding.get('description', 'N/A')}

---

"""

    report += """
## 📝 Next Steps

1. Review all **CRITICAL** and **HIGH** severity findings immediately
2. Consult the **REMEDIATION.md** file for detailed fix instructions
3. Implement fixes and re-scan to verify resolution
4. Review **FINDINGS.md** for detailed technical analysis
5. Share **EXECUTIVE-SUMMARY.md** with stakeholders

---

## 🛡️ About Alprina

Alprina is an AI-powered security scanning platform that helps you find and fix vulnerabilities in your code.

**Need help?**
- Documentation: https://alprina.ai/docs
- Support: support@alprina.ai
- Dashboard: https://dashboard.alprina.ai

---

*Generated by Alprina Security Scanner*
*Report ID: {results.get('scan_id', 'local-scan')}*
"""

    # Write report
    output_file = output_dir / "SECURITY-REPORT.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _generate_findings_report(results: dict, output_dir: Path):
    """Generate FINDINGS.md - All vulnerabilities with code context."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🔍 Security Findings - Detailed Analysis

**Generated:** {scan_date}
**Total Findings:** {len(findings)}

---

"""

    if not findings:
        report += """## ✅ No Security Issues Found!

Your code passed all security checks. Great work maintaining secure coding practices!

### What We Checked:
- SQL Injection vulnerabilities
- Cross-Site Scripting (XSS)
- Hardcoded secrets and credentials
- Authentication/Authorization flaws
- Insecure configurations
- Input validation issues
- Cryptographic weaknesses
- Dependency vulnerabilities

Keep up the good security practices!
"""
    else:
        # Group by file
        findings_by_file = {}
        for finding in findings:
            location = finding.get('location', 'unknown')
            if location not in findings_by_file:
                findings_by_file[location] = []
            findings_by_file[location].append(finding)

        for file_path, file_findings in findings_by_file.items():
            report += f"## 📄 File: `{file_path}`\n\n"
            report += f"**Issues Found:** {len(file_findings)}\n\n"

            for i, finding in enumerate(file_findings, 1):
                severity_icons = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🔵",
                    "INFO": "⚪"
                }

                icon = severity_icons.get(finding.get("severity"), "⚪")

                report += f"""### {icon} Finding #{i}: {finding.get('type', 'Security Issue')}

**Severity:** {finding.get('severity', 'N/A')}
"""
                if finding.get('line'):
                    report += f"**Line Number:** {finding.get('line')}  \n"

                report += f"""
**Description:**
{finding.get('description', 'N/A')}

**Risk:**
{_get_risk_explanation(finding)}

**CWE Reference:**
{_get_cwe_reference(finding.get('type', ''))}

---

"""

    report += """
## 📚 Additional Resources

### OWASP Top 10
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### Secure Coding Guidelines
- [NIST Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

*For remediation steps, see REMEDIATION.md*
*For executive summary, see EXECUTIVE-SUMMARY.md*
"""

    output_file = output_dir / "FINDINGS.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _generate_remediation_report(results: dict, output_dir: Path):
    """Generate REMEDIATION.md - Step-by-step fix instructions."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🛠️ Remediation Guide

**Generated:** {scan_date}
**Findings to Address:** {len(findings)}

---

## 📋 How to Use This Guide

This guide provides step-by-step instructions to fix each security issue found in your code.

**Priority Order:**
1. 🔴 CRITICAL - Fix immediately (within 24 hours)
2. 🟠 HIGH - Fix urgently (within 1 week)
3. 🟡 MEDIUM - Fix soon (within 1 month)
4. 🔵 LOW - Fix when convenient
5. ⚪ INFO - Optional improvements

---

"""

    if not findings:
        report += "## ✅ No Issues to Remediate\n\nYour code is secure! No action needed.\n"
    else:
        # Group by severity for prioritization
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            severity_findings = [f for f in findings if f.get("severity") == severity]

            if severity_findings:
                severity_icons = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🔵",
                    "INFO": "⚪"
                }

                report += f"\n## {severity_icons[severity]} {severity} Priority Fixes\n\n"

                for i, finding in enumerate(severity_findings, 1):
                    report += f"""### Fix #{i}: {finding.get('type', 'Security Issue')}

**File:** `{finding.get('location', 'N/A')}`
"""
                    if finding.get('line'):
                        report += f"**Line:** {finding.get('line')}  \n"

                    report += f"""
**Issue:**
{finding.get('description', 'N/A')}

**How to Fix:**

{_get_remediation_steps(finding)}

**Verification:**
1. Apply the fix to your code
2. Run Alprina scan again: `alprina scan {results.get('target', '.')}`
3. Verify this issue is resolved

---

"""

    report += """
## 🔄 Re-scanning After Fixes

After implementing fixes, run a new scan to verify:

```bash
alprina scan {target}
```

You can also view your scan history in the dashboard:
https://dashboard.alprina.ai

---

## 💡 Best Practices

### Preventive Measures

1. **Use a Security Linter** - Integrate Alprina into your CI/CD pipeline
2. **Code Reviews** - Have security-focused code reviews
3. **Dependency Updates** - Keep dependencies up to date
4. **Security Training** - Educate your team on secure coding

### Recommended Tools

- **Pre-commit Hooks** - Run Alprina before each commit
- **CI/CD Integration** - Automated security scanning on PRs
- **IDE Plugins** - Real-time security feedback while coding

---

## 📞 Need Help?

**Alprina Support:**
- Documentation: https://alprina.ai/docs
- Email: support@alprina.ai
- Dashboard: https://dashboard.alprina.ai

**Security Resources:**
- OWASP: https://owasp.org
- CWE: https://cwe.mitre.org
- NIST: https://csrc.nist.gov

---

*After fixing issues, re-run the scan to update this report*
""".replace("{target}", results.get('target', '.'))

    output_file = output_dir / "REMEDIATION.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _generate_executive_summary(results: dict, output_dir: Path):
    """Generate EXECUTIVE-SUMMARY.md - Non-technical overview."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Count findings by severity
    severity_counts = {
        "CRITICAL": len([f for f in findings if f.get("severity") == "CRITICAL"]),
        "HIGH": len([f for f in findings if f.get("severity") == "HIGH"]),
        "MEDIUM": len([f for f in findings if f.get("severity") == "MEDIUM"]),
        "LOW": len([f for f in findings if f.get("severity") == "LOW"]),
    }

    report = f"""# 📊 Executive Summary - Security Assessment

**Report Date:** {scan_date}
**Project:** {results.get('target', 'N/A')}
**Scan Coverage:** {results.get('files_scanned', 0)} files analyzed

---

## 🎯 Overview

This report provides a high-level summary of the security assessment performed on your codebase using Alprina's AI-powered security scanner.

### What We Found

**Total Security Findings:** {len(findings)}

"""

    # Risk assessment
    if severity_counts['CRITICAL'] > 0:
        risk_badge = "🔴 CRITICAL RISK"
        recommendation = "**Immediate action required.** Critical vulnerabilities detected that could lead to data breaches or system compromise."
    elif severity_counts['HIGH'] > 0:
        risk_badge = "🟠 HIGH RISK"
        recommendation = "**Urgent attention needed.** Significant security vulnerabilities require prompt remediation to protect your assets."
    elif severity_counts['MEDIUM'] > 0:
        risk_badge = "🟡 MEDIUM RISK"
        recommendation = "**Action recommended.** Moderate security concerns should be addressed in your next development cycle."
    elif severity_counts['LOW'] > 0:
        risk_badge = "🔵 LOW RISK"
        recommendation = "**Minor improvements suggested.** Address these issues during regular maintenance for enhanced security."
    else:
        risk_badge = "🟢 SECURE"
        recommendation = "**No security issues detected.** Your codebase follows security best practices!"

    report += f"""**Security Risk Level:** {risk_badge}

{recommendation}

---

## 📈 Findings Breakdown

| Priority Level | Count | Action Timeline |
|---------------|-------|-----------------|
| 🔴 Critical | {severity_counts['CRITICAL']} | Fix within 24 hours |
| 🟠 High | {severity_counts['HIGH']} | Fix within 1 week |
| 🟡 Medium | {severity_counts['MEDIUM']} | Fix within 1 month |
| 🔵 Low | {severity_counts['LOW']} | Fix when convenient |

---

## 💼 Business Impact

"""

    if severity_counts['CRITICAL'] > 0:
        report += """### Critical Security Risks

**Potential Impact:**
- Data breach or unauthorized access
- System compromise
- Regulatory compliance violations (GDPR, HIPAA, etc.)
- Reputational damage
- Financial losses

**Recommended Action:**
Allocate immediate resources to address critical vulnerabilities. Consider engaging security experts if internal capacity is limited.

"""
    elif severity_counts['HIGH'] > 0:
        report += """### Significant Security Concerns

**Potential Impact:**
- Elevated risk of security incidents
- Possible data exposure
- Compliance audit findings
- Customer trust erosion

**Recommended Action:**
Prioritize these fixes in the current sprint. Ensure development team has necessary security training and resources.

"""
    else:
        report += """### Security Posture

Your current security posture is good. Continue maintaining security best practices and regular scanning to ensure ongoing protection.

"""

    report += """---

## 📋 Recommended Next Steps

### Immediate Actions (This Week)
1. ✅ Review this executive summary with stakeholders
2. ✅ Share REMEDIATION.md with development team
3. ✅ Prioritize fixes based on severity levels
4. ✅ Allocate resources for remediation work

### Short-term Actions (This Month)
1. 🔨 Implement fixes for all HIGH and CRITICAL findings
2. 🔄 Re-scan codebase after fixes
3. 📚 Conduct security training for development team
4. 🔍 Review security processes and policies

### Long-term Actions (This Quarter)
1. 🚀 Integrate Alprina into CI/CD pipeline
2. 📊 Establish regular security scanning schedule
3. 🎓 Ongoing security awareness training
4. 📈 Track and report security metrics

---

## 🛡️ About This Assessment

**Scanning Technology:**
Alprina uses AI-powered security agents to detect vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)
- Authentication & Authorization flaws
- Hardcoded secrets
- Insecure configurations
- And 100+ other vulnerability types

**Coverage:**
This scan analyzed {results.get('files_scanned', 0)} files in your codebase using industry-standard security frameworks (OWASP, CWE, NIST).

**Limitations:**
Automated scanning is highly effective but should be complemented with:
- Manual security code reviews
- Penetration testing for production systems
- Ongoing security monitoring

---

## 📞 Questions or Concerns?

**For Technical Details:**
Review the SECURITY-REPORT.md and FINDINGS.md files for complete technical analysis.

**For Remediation:**
See REMEDIATION.md for step-by-step fix instructions.

**For Support:**
- Dashboard: https://dashboard.alprina.ai
- Documentation: https://alprina.ai/docs
- Email: support@alprina.ai

---

## 📊 Metrics & Tracking

**Scan ID:** {results.get('scan_id', 'local-scan')}
**View in Dashboard:** [https://dashboard.alprina.ai](https://dashboard.alprina.ai)

Track your security progress over time:
- Vulnerability trends
- Fix rates
- Security score
- Compliance status

---

*This executive summary is intended for non-technical stakeholders. For technical details, refer to the complete security report.*

**Generated by Alprina Security Platform**
**Trusted by security-conscious development teams worldwide**
"""

    output_file = output_dir / "EXECUTIVE-SUMMARY.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _get_risk_explanation(finding: dict) -> str:
    """Get risk explanation based on finding type."""

    risk_explanations = {
        "SQL Injection": "Attackers could execute arbitrary database queries, leading to data theft, modification, or deletion.",
        "XSS": "Malicious scripts could be injected and executed in users' browsers, stealing credentials or performing unauthorized actions.",
        "Hardcoded Secret": "Exposed credentials could allow unauthorized access to systems, databases, or third-party services.",
        "Authentication Bypass": "Attackers could gain unauthorized access without valid credentials.",
        "Insecure Configuration": "System misconfiguration could expose sensitive data or create security vulnerabilities.",
        "Debug Mode": "Debug information could reveal system internals and sensitive data to attackers.",
        "Weak Cryptography": "Data encryption may be compromised, exposing sensitive information.",
    }

    finding_type = finding.get('type', '')
    return risk_explanations.get(finding_type, "This vulnerability could be exploited by attackers to compromise system security.")


def _get_cwe_reference(finding_type: str) -> str:
    """Get CWE reference for finding type."""

    cwe_mapping = {
        "SQL Injection": "[CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)",
        "XSS": "[CWE-79: Cross-site Scripting](https://cwe.mitre.org/data/definitions/79.html)",
        "Hardcoded Secret": "[CWE-798: Use of Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)",
        "Authentication Bypass": "[CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)",
        "Insecure Configuration": "[CWE-16: Configuration](https://cwe.mitre.org/data/definitions/16.html)",
        "Debug Mode": "[CWE-489: Active Debug Code](https://cwe.mitre.org/data/definitions/489.html)",
    }

    return cwe_mapping.get(finding_type, "[CWE Database](https://cwe.mitre.org/)")


def _get_remediation_steps(finding: dict) -> str:
    """Get specific remediation steps based on finding type."""

    remediation_guides = {
        "SQL Injection": """
**Step 1:** Use parameterized queries or prepared statements

```python
# ❌ Vulnerable Code
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# ✅ Secure Code
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Step 2:** Validate and sanitize all user input
**Step 3:** Use an ORM (like SQLAlchemy) with built-in protections
**Step 4:** Implement least privilege database access
""",

        "Hardcoded Secret": """
**Step 1:** Move secrets to environment variables

```python
# ❌ Vulnerable Code
API_KEY = "sk_live_abc123xyz"

# ✅ Secure Code
import os
API_KEY = os.getenv("API_KEY")
```

**Step 2:** Use a `.env` file (add to `.gitignore`)
**Step 3:** Use a secret management service (AWS Secrets Manager, HashiCorp Vault)
**Step 4:** Rotate the exposed credential immediately
**Step 5:** Scan git history and remove the secret
""",

        "XSS": """
**Step 1:** Escape all user-generated content before rendering

```python
# ❌ Vulnerable Code
return f"<div>{user_input}</div>"

# ✅ Secure Code
from html import escape
return f"<div>{escape(user_input)}</div>"
```

**Step 2:** Use Content Security Policy (CSP) headers
**Step 3:** Validate input on both client and server side
**Step 4:** Use a template engine with auto-escaping
""",

        "Debug Mode": """
**Step 1:** Disable debug mode in production

```python
# ❌ Vulnerable Code
DEBUG = True

# ✅ Secure Code
DEBUG = os.getenv("DEBUG", "False") == "True"
```

**Step 2:** Set appropriate environment variables
**Step 3:** Use different config files for dev/prod
**Step 4:** Remove debug endpoints from production
""",
    }

    finding_type = finding.get('type', '')

    if finding_type in remediation_guides:
        return remediation_guides[finding_type]
    else:
        return f"""
**General Remediation Steps:**

1. Review the code at `{finding.get('location', 'N/A')}`
2. Understand the security risk described above
3. Implement security best practices for this vulnerability type
4. Test the fix in a development environment
5. Deploy the fix to production
6. Re-scan with Alprina to verify resolution

**Need specific guidance?**
Contact Alprina support at support@alprina.ai with your Scan ID.
"""


# ============================================================================
# SPECIALIZED REPORT GENERATORS FOR DIFFERENT AGENT TYPES
# ============================================================================

def _generate_red_team_report(results: dict, output_dir: Path):
    """Generate RED-TEAM-REPORT.md - Penetration testing findings."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# ⚔️ Red Team Assessment Report

**Assessment Date:** {scan_date}
**Target:** {results.get('target', 'N/A')}
**Engagement Type:** {results.get('engagement_type', 'Offensive Security Testing')}

---

## 📋 Executive Summary

This report documents the findings from an offensive security assessment (red team) performed on the target system. The assessment simulates real-world attack scenarios to identify exploitable vulnerabilities.

### Assessment Scope

**Total Attack Vectors Tested:** {len(findings)}
**Successful Exploits:** {len([f for f in findings if f.get('exploitable', False)])}
**Attack Surface Coverage:** {results.get('coverage', 'Comprehensive')}

---

## 🎯 Attack Vectors Identified

"""

    # Group by attack type
    attack_types = {}
    for finding in findings:
        attack_type = finding.get('attack_type', finding.get('type', 'Unknown'))
        if attack_type not in attack_types:
            attack_types[attack_type] = []
        attack_types[attack_type].append(finding)

    for attack_type, vectors in attack_types.items():
        exploitable = len([v for v in vectors if v.get('exploitable', False)])

        report += f"""### {attack_type}

**Vectors Found:** {len(vectors)}
**Exploitable:** {exploitable}

"""
        for i, vector in enumerate(vectors, 1):
            exploit_status = "✅ EXPLOITABLE" if vector.get('exploitable') else "⚠️ POTENTIAL"

            report += f"""#### {i}. {vector.get('title', 'Attack Vector')}

**Status:** {exploit_status}
**Severity:** {vector.get('severity', 'MEDIUM')}
**Location:** `{vector.get('location', 'N/A')}`

**Attack Description:**
{vector.get('description', 'N/A')}

**Exploitation Steps:**
{vector.get('exploit_steps', 'Manual testing required')}

**Impact:**
{vector.get('impact', 'Could lead to system compromise')}

---

"""

    report += """
## 🛡️ Defense Recommendations

### Immediate Actions
1. Patch all exploitable vulnerabilities within 24 hours
2. Implement WAF rules to block identified attack patterns
3. Enable security monitoring for attempted exploits
4. Review and harden authentication mechanisms

### Strategic Improvements
1. Implement defense-in-depth architecture
2. Regular red team assessments (quarterly)
3. Security awareness training for development team
4. Incident response plan updates

---

## 📊 Attack Surface Analysis

### High-Risk Areas
"""

    # Identify high-risk areas
    high_risk = [f for f in findings if f.get('severity') in ['CRITICAL', 'HIGH']]
    if high_risk:
        for area in high_risk[:5]:
            report += f"- `{area.get('location', 'N/A')}` - {area.get('type', 'Security Issue')}\n"
    else:
        report += "- No critical attack vectors identified\n"

    report += f"""

### Recommendations by Priority

**P0 (Critical):** {len([f for f in findings if f.get('severity') == 'CRITICAL'])} items - Fix immediately
**P1 (High):** {len([f for f in findings if f.get('severity') == 'HIGH'])} items - Fix within 1 week
**P2 (Medium):** {len([f for f in findings if f.get('severity') == 'MEDIUM'])} items - Fix within 1 month

---

## 🔬 Methodology

**Assessment Approach:**
- Black-box testing from external attacker perspective
- Exploit development and validation
- Post-exploitation analysis
- Privilege escalation testing

**Tools Used:**
- Alprina Red Team Agent
- Industry-standard penetration testing tools
- Custom exploit scripts

---

*This is a confidential security assessment. Distribution should be limited to authorized personnel only.*

**Assessed by:** Alprina Red Team Agent
**Report ID:** {results.get('scan_id', 'red-team-' + datetime.now().strftime('%Y%m%d'))}
"""

    output_file = output_dir / "RED-TEAM-REPORT.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _generate_blue_team_report(results: dict, output_dir: Path):
    """Generate BLUE-TEAM-REPORT.md - Defensive posture assessment."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🛡️ Blue Team Defense Posture Report

**Assessment Date:** {scan_date}
**Target:** {results.get('target', 'N/A')}
**Assessment Type:** Defensive Security Evaluation

---

## 📋 Executive Summary

This report evaluates the current security posture and defensive capabilities of the target system. It identifies gaps in security controls, monitoring, and incident response readiness.

### Security Posture Score

**Overall Score:** {results.get('security_score', 'N/A')}/100
**Control Coverage:** {len(findings)} security controls evaluated
**Gaps Identified:** {len([f for f in findings if f.get('status') == 'missing' or f.get('severity') in ['HIGH', 'CRITICAL']])}

---

## 🔍 Security Controls Assessment

"""

    # Group by control category
    categories = {}
    for finding in findings:
        category = finding.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(finding)

    for category, controls in categories.items():
        implemented = len([c for c in controls if c.get('status') == 'implemented'])
        missing = len([c for c in controls if c.get('status') == 'missing'])
        partial = len([c for c in controls if c.get('status') == 'partial'])

        report += f"""### {category}

**Total Controls:** {len(controls)}
**✅ Implemented:** {implemented}
**⚠️ Partial:** {partial}
**❌ Missing:** {missing}

"""

        for i, control in enumerate(controls, 1):
            status_icons = {
                'implemented': '✅',
                'partial': '⚠️',
                'missing': '❌',
                'weak': '🟡'
            }
            icon = status_icons.get(control.get('status', 'unknown'), '❓')

            report += f"""#### {icon} {i}. {control.get('title', 'Security Control')}

**Status:** {control.get('status', 'Unknown').upper()}
**Impact:** {control.get('severity', 'MEDIUM')}

**Assessment:**
{control.get('description', 'N/A')}

**Recommendation:**
{control.get('recommendation', 'Implement this security control')}

---

"""

    report += """
## 🎯 Priority Improvements

### Critical Gaps (Fix Immediately)
"""

    critical = [f for f in findings if f.get('severity') == 'CRITICAL']
    if critical:
        for gap in critical:
            report += f"- {gap.get('title', 'Critical Gap')}: {gap.get('recommendation', 'Implement immediately')}\n"
    else:
        report += "- No critical gaps identified ✅\n"

    report += """

### High Priority (Fix This Month)
"""

    high = [f for f in findings if f.get('severity') == 'HIGH']
    if high:
        for gap in high[:5]:
            report += f"- {gap.get('title', 'High Priority Gap')}\n"
    else:
        report += "- No high-priority gaps identified ✅\n"

    report += f"""

---

## 📊 Defensive Metrics

### Detection Capabilities
- **Logging Coverage:** {results.get('logging_coverage', 'N/A')}
- **SIEM Integration:** {results.get('siem_status', 'Not evaluated')}
- **Alert Rules:** {results.get('alert_rules', 'N/A')} configured

### Response Readiness
- **Incident Response Plan:** {results.get('ir_plan_status', 'Not evaluated')}
- **Backup Strategy:** {results.get('backup_status', 'Not evaluated')}
- **Recovery Time Objective:** {results.get('rto', 'Not defined')}

### Security Monitoring
- **Real-time Monitoring:** {results.get('monitoring_status', 'Not evaluated')}
- **Threat Intelligence:** {results.get('threat_intel', 'Not evaluated')}
- **Vulnerability Scanning:** {results.get('vuln_scan_frequency', 'Not evaluated')}

---

## 🔐 Recommended Security Controls

### Immediate Implementation
1. Enable comprehensive logging and monitoring
2. Implement SIEM or security analytics platform
3. Deploy endpoint detection and response (EDR)
4. Configure automated backup systems
5. Establish incident response procedures

### Medium-term Goals
1. Implement zero-trust architecture
2. Deploy web application firewall (WAF)
3. Establish security operations center (SOC)
4. Implement security awareness training program
5. Regular security assessments and audits

---

## 📈 Improvement Roadmap

### Month 1
- Address all critical security gaps
- Implement basic logging and monitoring
- Establish incident response team

### Quarter 1
- Deploy security tools (SIEM, EDR, WAF)
- Complete high-priority improvements
- Conduct tabletop exercises

### Year 1
- Achieve target security posture
- Establish continuous monitoring
- Regular security assessments
- Ongoing team training

---

*This assessment is intended for internal security team use. Treat as confidential.*

**Assessed by:** Alprina Blue Team Agent
**Report ID:** {results.get('scan_id', 'blue-team-' + datetime.now().strftime('%Y%m%d'))}
"""

    output_file = output_dir / "BLUE-TEAM-REPORT.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


def _generate_dfir_report(results: dict, output_dir: Path):
    """Generate DFIR-REPORT.md - Digital forensics and incident response findings."""

    findings = results.get("findings", [])
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🔬 Digital Forensics & Incident Response Report

**Analysis Date:** {scan_date}
**Target:** {results.get('target', 'N/A')}
**Analysis Type:** {results.get('analysis_type', 'Forensic Analysis')}
**Analyst:** Alprina DFIR Agent

---

## 📋 Executive Summary

This report documents the forensic analysis performed on the target system. The analysis aimed to identify indicators of compromise (IOCs), timeline of events, and preserve evidence for potential investigation.

### Key Findings

**Total Artifacts Analyzed:** {results.get('artifacts_analyzed', len(findings))}
**IOCs Identified:** {len([f for f in findings if f.get('ioc', False)])}
**Evidence Items:** {len([f for f in findings if f.get('evidence', False)])}

---

## 🕵️ Indicators of Compromise (IOCs)

"""

    iocs = [f for f in findings if f.get('ioc', False)]
    if iocs:
        for i, ioc in enumerate(iocs, 1):
            report += f"""### IOC #{i}: {ioc.get('title', 'Indicator of Compromise')}

**Type:** {ioc.get('ioc_type', 'Unknown')}
**Severity:** {ioc.get('severity', 'MEDIUM')}
**Location:** `{ioc.get('location', 'N/A')}`
**Timestamp:** {ioc.get('timestamp', 'Unknown')}

**Description:**
{ioc.get('description', 'N/A')}

**Hash Values:**
```
MD5: {ioc.get('md5', 'N/A')}
SHA256: {ioc.get('sha256', 'N/A')}
```

**Evidence Chain:**
{ioc.get('evidence_chain', 'See evidence log')}

---

"""
    else:
        report += "No indicators of compromise identified in this analysis.\n\n"

    report += """
## ⏱️ Timeline Reconstruction

"""

    # Create timeline from findings
    timeline_items = sorted([f for f in findings if f.get('timestamp')],
                          key=lambda x: x.get('timestamp', ''))

    if timeline_items:
        report += "| Timestamp | Event | Description | Severity |\n"
        report += "|-----------|-------|-------------|----------|\n"

        for item in timeline_items[:20]:  # Limit to first 20
            report += f"| {item.get('timestamp', 'Unknown')} | {item.get('title', 'Event')} | {item.get('description', 'N/A')[:50]}... | {item.get('severity', 'INFO')} |\n"
    else:
        report += "Timeline reconstruction not available (no timestamps in findings)\n"

    report += f"""

---

## 📁 Evidence Collection

### Artifacts Preserved
"""

    evidence_items = [f for f in findings if f.get('evidence', False)]
    if evidence_items:
        for item in evidence_items:
            report += f"- `{item.get('location', 'N/A')}` - {item.get('title', 'Evidence item')}\n"
    else:
        report += "- No specific evidence items flagged in this scan\n"

    report += f"""

### Chain of Custody
**Analysis Start:** {scan_date}
**Analysis End:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analyst:** Alprina DFIR Agent
**Analysis Tools:** Alprina Security Platform v1.0
**Evidence Hash:** {results.get('evidence_hash', 'N/A')}

---

## 🔍 Analysis Findings

### System State
- **System Integrity:** {results.get('system_integrity', 'Not evaluated')}
- **Recent Modifications:** {len([f for f in findings if 'modified' in f.get('type', '').lower()])} items
- **Suspicious Activity:** {len([f for f in findings if f.get('suspicious', False)])} indicators

### Network Activity
- **Network Connections:** {results.get('network_connections', 'Not analyzed')}
- **Outbound Traffic:** {results.get('outbound_traffic', 'Not analyzed')}
- **DNS Queries:** {results.get('dns_queries', 'Not analyzed')}

### File System
- **Modified Files:** {len([f for f in findings if f.get('modified', False)])}
- **New Files:** {len([f for f in findings if f.get('new_file', False)])}
- **Deleted Files:** {len([f for f in findings if f.get('deleted', False)])}

---

## 🎯 Incident Analysis

### Attack Vector Assessment
"""

    attack_vectors = [f for f in findings if 'attack' in f.get('type', '').lower()]
    if attack_vectors:
        for vector in attack_vectors:
            report += f"- **{vector.get('title')}:** {vector.get('description', 'N/A')}\n"
    else:
        report += "- No clear attack vectors identified\n"

    report += """

### Lateral Movement Indicators
"""

    lateral = [f for f in findings if 'lateral' in f.get('description', '').lower()]
    if lateral:
        for item in lateral:
            report += f"- {item.get('title', 'Lateral movement detected')}\n"
    else:
        report += "- No lateral movement indicators detected\n"

    report += """

### Data Exfiltration Risk
"""

    exfiltration = [f for f in findings if 'exfiltration' in f.get('description', '').lower() or 'data transfer' in f.get('description', '').lower()]
    if exfiltration:
        report += "⚠️ **Potential data exfiltration detected**\n\n"
        for item in exfiltration:
            report += f"- {item.get('title')}: {item.get('description', 'N/A')}\n"
    else:
        report += "✅ No data exfiltration indicators identified\n"

    report += """

---

## 📋 Recommendations

### Immediate Actions
1. Isolate affected systems if compromise confirmed
2. Preserve all evidence for potential legal proceedings
3. Reset credentials for potentially compromised accounts
4. Conduct full system integrity check
5. Review all timeline events with security team

### Investigation Next Steps
1. Expand analysis to related systems
2. Review logs for additional IOCs
3. Conduct memory forensics if warranted
4. Interview system administrators and users
5. Engage law enforcement if criminal activity detected

### Long-term Improvements
1. Implement enhanced logging and monitoring
2. Deploy EDR solution for better visibility
3. Establish incident response procedures
4. Regular forensic readiness assessments
5. Security awareness training for staff

---

## 📝 Analysis Notes

**Methodology:**
- Static file system analysis
- Log file review
- IOC matching against threat intelligence
- Timeline reconstruction from artifacts
- Evidence preservation procedures followed

**Limitations:**
- Analysis based on available artifacts at time of scan
- Memory forensics not performed
- Network capture not available
- Live system analysis not conducted

---

*This is a confidential forensic report. Handle according to evidence preservation procedures.*

**Report ID:** {results.get('scan_id', 'dfir-' + datetime.now().strftime('%Y%m%d'))}
**Analyst:** Alprina DFIR Agent
**Classification:** CONFIDENTIAL - LEGAL PRIVILEGE MAY APPLY
"""

    output_file = output_dir / "DFIR-REPORT.md"
    output_file.write_text(report)
    logger.info(f"✓ Created: {output_file}")


# Registry of specialized report generators
SPECIALIZED_REPORT_GENERATORS = {
    "red_teamer": _generate_red_team_report,
    "red-team": _generate_red_team_report,
    "offensive-security": _generate_red_team_report,

    "blue_teamer": _generate_blue_team_report,
    "blue-team": _generate_blue_team_report,
    "defensive-security": _generate_blue_team_report,

    "dfir": _generate_dfir_report,
    "forensics": _generate_dfir_report,
    "incident-response": _generate_dfir_report,
}
