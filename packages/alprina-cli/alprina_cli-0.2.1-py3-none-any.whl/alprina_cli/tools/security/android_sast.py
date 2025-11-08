"""
Android SAST Tool (Static Application Security Testing)

Context Engineering:
- Android app security analysis
- Manifest analysis, code review, permission auditing
- Returns structured mobile security findings
- Memory-aware: Tracks app vulnerability patterns

Secure mobile apps from the start.
"""

from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class AndroidSASTParams(BaseModel):
    """
    Parameters for Android SAST operations.

    Context: Focused schema for Android security testing.
    """
    target: str = Field(
        description="Target Android app (APK, source code directory, or AndroidManifest.xml)"
    )
    analysis_type: Literal["manifest", "permissions", "code_review", "crypto", "network", "full"] = Field(
        default="full",
        description="Analysis type: manifest, permissions, code_review, crypto, network, full"
    )
    severity_threshold: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        default="MEDIUM",
        description="Minimum severity to report"
    )
    max_findings: int = Field(
        default=50,
        description="Maximum findings to return"
    )


class AndroidSASTTool(AlprinaToolBase[AndroidSASTParams]):
    """
    Android SAST tool for mobile app security analysis.

    Context Engineering Benefits:
    - Structured mobile security findings
    - Manifest and permission analysis
    - Code-level vulnerability detection
    - Memory integration for pattern tracking

    Analysis Types:
    - manifest: AndroidManifest.xml analysis
    - permissions: Permission auditing
    - code_review: Source code security review
    - crypto: Cryptographic implementation review
    - network: Network security analysis
    - full: Comprehensive security analysis

    Usage:
    ```python
    tool = AndroidSASTTool(memory_service=memory)
    result = await tool.execute(AndroidSASTParams(
        target="./app/src",
        analysis_type="full",
        severity_threshold="HIGH"
    ))
    ```
    """

    name: str = "AndroidSAST"
    description: str = """Android Static Application Security Testing.

Capabilities:
- AndroidManifest.xml security analysis
- Permission auditing and risk assessment
- Source code vulnerability detection
- Cryptographic implementation review
- Network security analysis
- Comprehensive mobile security assessment

Returns: Structured Android security findings"""
    params: type[AndroidSASTParams] = AndroidSASTParams

    # Dangerous Android permissions
    DANGEROUS_PERMISSIONS = [
        "READ_CONTACTS", "WRITE_CONTACTS",
        "READ_SMS", "SEND_SMS", "RECEIVE_SMS",
        "READ_CALL_LOG", "WRITE_CALL_LOG",
        "CAMERA", "RECORD_AUDIO",
        "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
        "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE"
    ]

    # Suspicious API calls
    SUSPICIOUS_APIS = {
        "reflection": ["Class.forName", "getDeclaredMethod", "invoke"],
        "native_code": ["System.loadLibrary", "Runtime.exec"],
        "crypto_weak": ["DES", "MD5", "SHA1"],
        "network": ["HttpURLConnection", "OkHttp", "Retrofit"],
        "data_storage": ["SharedPreferences", "SQLiteDatabase", "openFileOutput"]
    }

    async def execute(self, params: AndroidSASTParams) -> ToolOk | ToolError:
        """
        Execute Android SAST analysis.

        Context: Returns structured mobile security findings.
        """
        logger.info(f"AndroidSAST: {params.target} (type={params.analysis_type})")

        try:
            # Check memory for similar apps
            if self.memory_service and self.memory_service.is_enabled():
                similar_apps = self.memory_service.search(
                    f"Android security analysis similar to {params.target}",
                    limit=3
                )
                if similar_apps:
                    logger.info(f"Found {len(similar_apps)} similar app analyses")

            # Execute analysis
            if params.analysis_type == "manifest":
                findings = await self._manifest_analysis(params)
            elif params.analysis_type == "permissions":
                findings = await self._permission_analysis(params)
            elif params.analysis_type == "code_review":
                findings = await self._code_review_analysis(params)
            elif params.analysis_type == "crypto":
                findings = await self._crypto_analysis(params)
            elif params.analysis_type == "network":
                findings = await self._network_analysis(params)
            else:  # full
                findings = await self._full_analysis(params)

            # Filter by severity
            findings = self._filter_by_severity(findings, params.severity_threshold)

            # Limit findings
            if len(findings) > params.max_findings:
                findings = findings[:params.max_findings]
                truncated = True
            else:
                truncated = False

            # Calculate stats
            severity_counts = {}
            for finding in findings:
                sev = finding.get("severity", "INFO")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            result_content = {
                "target": params.target,
                "analysis_type": params.analysis_type,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "by_severity": severity_counts,
                    "truncated": truncated
                }
            }

            # Store in memory
            if self.memory_service and self.memory_service.is_enabled():
                self.memory_service.add_scan_results(
                    tool_name="AndroidSAST",
                    target=params.target,
                    results=result_content
                )

            return ToolOk(content=result_content)

        except Exception as e:
            logger.error(f"Android SAST failed: {e}")
            return ToolError(
                message=f"Android SAST failed: {str(e)}",
                brief="Analysis failed"
            )

    async def _manifest_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Analyze AndroidManifest.xml.

        Context: Security analysis of manifest file.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        # Find AndroidManifest.xml
        manifest_path = None
        if target_path.is_file() and target_path.name == "AndroidManifest.xml":
            manifest_path = target_path
        elif target_path.is_dir():
            # Search for manifest
            manifests = list(target_path.rglob("AndroidManifest.xml"))
            if manifests:
                manifest_path = manifests[0]

        if not manifest_path:
            findings.append({
                "category": "manifest",
                "severity": "INFO",
                "title": "No AndroidManifest.xml found",
                "description": "Could not locate AndroidManifest.xml file"
            })
            return findings

        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Check for debuggable flag
            if root.find(".//application[@android:debuggable='true']", {'android': 'http://schemas.android.com/apk/res/android'}):
                findings.append({
                    "category": "manifest",
                    "severity": "HIGH",
                    "title": "Debuggable Flag Enabled",
                    "description": "Application is debuggable in production",
                    "recommendation": "Remove android:debuggable=\"true\" from manifest",
                    "file": str(manifest_path)
                })

            # Check for backup enabled
            if root.find(".//application[@android:allowBackup='true']", {'android': 'http://schemas.android.com/apk/res/android'}):
                findings.append({
                    "category": "manifest",
                    "severity": "MEDIUM",
                    "title": "Backup Enabled",
                    "description": "Application allows backup (potential data exposure)",
                    "recommendation": "Consider android:allowBackup=\"false\"",
                    "file": str(manifest_path)
                })

            # Check for exported components
            exported_components = root.findall(".//*[@android:exported='true']", {'android': 'http://schemas.android.com/apk/res/android'})
            if exported_components:
                findings.append({
                    "category": "manifest",
                    "severity": "MEDIUM",
                    "title": "Exported Components",
                    "description": f"Found {len(exported_components)} exported components",
                    "recommendation": "Review exported components for necessity",
                    "file": str(manifest_path)
                })

        except Exception as e:
            findings.append({
                "category": "manifest",
                "severity": "LOW",
                "title": "Manifest Parse Error",
                "description": f"Could not parse manifest: {str(e)}",
                "file": str(manifest_path)
            })

        return findings

    async def _permission_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Analyze app permissions.

        Context: Permission auditing and risk assessment.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        # Find AndroidManifest.xml
        manifest_path = None
        if target_path.is_file() and target_path.name == "AndroidManifest.xml":
            manifest_path = target_path
        elif target_path.is_dir():
            manifests = list(target_path.rglob("AndroidManifest.xml"))
            if manifests:
                manifest_path = manifests[0]

        if not manifest_path:
            return findings

        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Get all permissions
            permissions = root.findall(".//uses-permission", {'android': 'http://schemas.android.com/apk/res/android'})

            dangerous_perms = []
            for perm in permissions:
                perm_name = perm.get('{http://schemas.android.com/apk/res/android}name', '')

                # Check if dangerous
                for dangerous in self.DANGEROUS_PERMISSIONS:
                    if dangerous in perm_name:
                        dangerous_perms.append(perm_name)

            if dangerous_perms:
                findings.append({
                    "category": "permissions",
                    "severity": "HIGH",
                    "title": "Dangerous Permissions Requested",
                    "description": f"App requests {len(dangerous_perms)} dangerous permissions",
                    "permissions": dangerous_perms,
                    "recommendation": "Verify all permissions are necessary",
                    "file": str(manifest_path)
                })

            # Check for over-permission
            if len(permissions) > 10:
                findings.append({
                    "category": "permissions",
                    "severity": "MEDIUM",
                    "title": "Excessive Permissions",
                    "description": f"App requests {len(permissions)} permissions",
                    "recommendation": "Review and minimize permission requests",
                    "file": str(manifest_path)
                })

        except Exception as e:
            logger.debug(f"Permission analysis error: {e}")

        return findings

    async def _code_review_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Review source code for vulnerabilities.

        Context: Code-level security analysis.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if not target_path.exists():
            return findings

        # Find Java/Kotlin files
        code_files = []
        if target_path.is_dir():
            code_files.extend(list(target_path.rglob("*.java"))[:20])
            code_files.extend(list(target_path.rglob("*.kt"))[:20])

        for code_file in code_files:
            try:
                content = code_file.read_text(errors="ignore")

                # Check for suspicious APIs
                for api_category, api_list in self.SUSPICIOUS_APIS.items():
                    for api in api_list:
                        if api in content:
                            severity = "HIGH" if api_category in ["reflection", "native_code"] else "MEDIUM"
                            findings.append({
                                "category": "code_review",
                                "severity": severity,
                                "title": f"Suspicious API: {api}",
                                "description": f"Found {api_category} API: {api}",
                                "file": str(code_file),
                                "api_category": api_category
                            })

                # Check for hardcoded secrets
                if re.search(r"(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{10,}['\"]", content, re.IGNORECASE):
                    findings.append({
                        "category": "code_review",
                        "severity": "CRITICAL",
                        "title": "Hardcoded Secret",
                        "description": "Found hardcoded API key or secret",
                        "file": str(code_file),
                        "recommendation": "Use Android Keystore or encrypted storage"
                    })

                # Check for SQL injection
                if re.search(r"(execSQL|rawQuery).*\+.*", content):
                    findings.append({
                        "category": "code_review",
                        "severity": "HIGH",
                        "title": "Potential SQL Injection",
                        "description": "SQL query with string concatenation",
                        "file": str(code_file),
                        "recommendation": "Use parameterized queries"
                    })

            except Exception as e:
                logger.debug(f"Could not review {code_file}: {e}")

        return findings

    async def _crypto_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Analyze cryptographic implementations.

        Context: Crypto security review.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.is_dir():
            code_files = list(target_path.rglob("*.java"))[:20]
            code_files.extend(list(target_path.rglob("*.kt"))[:20])

            for code_file in code_files:
                try:
                    content = code_file.read_text(errors="ignore")

                    # Check for weak crypto
                    for weak_algo in ["DES", "MD5", "SHA1"]:
                        if weak_algo in content:
                            findings.append({
                                "category": "crypto",
                                "severity": "HIGH",
                                "title": f"Weak Cryptography: {weak_algo}",
                                "description": f"Using weak algorithm: {weak_algo}",
                                "file": str(code_file),
                                "recommendation": "Use AES-256, SHA-256 or better"
                            })

                    # Check for hardcoded keys
                    if re.search(r"(SecretKeySpec|IvParameterSpec).*new.*byte\[\]", content):
                        findings.append({
                            "category": "crypto",
                            "severity": "CRITICAL",
                            "title": "Hardcoded Encryption Key",
                            "description": "Encryption key appears to be hardcoded",
                            "file": str(code_file),
                            "recommendation": "Use Android Keystore"
                        })

                except Exception:
                    pass

        return findings

    async def _network_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Analyze network security.

        Context: Network communication security.
        """
        findings = []

        target_path = Path(params.target).expanduser()

        if target_path.is_dir():
            # Check network security config
            network_configs = list(target_path.rglob("network_security_config.xml"))
            if not network_configs:
                findings.append({
                    "category": "network",
                    "severity": "MEDIUM",
                    "title": "No Network Security Config",
                    "description": "Missing network_security_config.xml",
                    "recommendation": "Implement network security configuration"
                })

            # Check for cleartext traffic
            code_files = list(target_path.rglob("*.java"))[:20]
            code_files.extend(list(target_path.rglob("*.kt"))[:20])

            for code_file in code_files:
                try:
                    content = code_file.read_text(errors="ignore")

                    if "http://" in content.lower() and "https://" not in content.lower():
                        findings.append({
                            "category": "network",
                            "severity": "HIGH",
                            "title": "Cleartext HTTP Traffic",
                            "description": "App uses HTTP instead of HTTPS",
                            "file": str(code_file),
                            "recommendation": "Use HTTPS for all network traffic"
                        })

                    # Check for certificate pinning
                    if "CertificatePinner" in content or "TrustManager" in content:
                        findings.append({
                            "category": "network",
                            "severity": "INFO",
                            "title": "Certificate Pinning Detected",
                            "description": "App implements certificate pinning (good practice)",
                            "file": str(code_file)
                        })

                except Exception:
                    pass

        return findings

    async def _full_analysis(self, params: AndroidSASTParams) -> List[Dict[str, Any]]:
        """
        Comprehensive Android security analysis.

        Context: Full SAST scan.
        """
        findings = []

        # Execute all analysis types
        findings.extend(await self._manifest_analysis(params))
        findings.extend(await self._permission_analysis(params))
        findings.extend(await self._code_review_analysis(params))
        findings.extend(await self._crypto_analysis(params))
        findings.extend(await self._network_analysis(params))

        return findings

    def _filter_by_severity(self, findings: List[Dict[str, Any]], threshold: str) -> List[Dict[str, Any]]:
        """Filter findings by severity threshold"""
        severity_order = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        threshold_level = severity_order.get(threshold, 2)

        return [
            f for f in findings
            if severity_order.get(f.get("severity", "INFO"), 0) >= threshold_level
        ]
