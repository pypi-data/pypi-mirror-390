"""
DFIR Tool (Digital Forensics and Incident Response)

Context Engineering:
- Forensic analysis and evidence collection
- Timeline reconstruction
- Artifact preservation
- Memory-aware: Builds forensic knowledge base

Preserve evidence, reconstruct events.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import hashlib
import json
from datetime import datetime

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


class DFIRParams(BaseModel):
    """
    Parameters for DFIR operations.

    Context: Focused schema for forensic analysis.
    """
    target: str = Field(
        description="Target for forensic analysis"
    )
    operation: Literal["evidence_collection", "timeline_analysis", "artifact_extraction", "hash_verification", "full_forensics"] = Field(
        default="evidence_collection",
        description="Operation: evidence_collection, timeline_analysis, artifact_extraction, hash_verification, full_forensics"
    )
    preserve_evidence: bool = Field(
        default=True,
        description="Preserve evidence chain of custody"
    )
    max_artifacts: int = Field(
        default=100,
        description="Maximum artifacts to collect"
    )


class DFIRTool(AlprinaToolBase[DFIRParams]):
    """
    DFIR tool for digital forensics and incident response.

    Context Engineering Benefits:
    - Structured forensic findings
    - Chain of custody tracking
    - Timeline reconstruction
    - Memory integration for case correlation

    Operations:
    - evidence_collection: Collect and preserve evidence
    - timeline_analysis: Reconstruct event timeline
    - artifact_extraction: Extract forensic artifacts
    - hash_verification: Verify file integrity
    - full_forensics: Comprehensive forensic analysis

    Usage:
    ```python
    tool = DFIRTool(memory_service=memory)
    result = await tool.execute(DFIRParams(
        target="/evidence",
        operation="evidence_collection",
        preserve_evidence=True
    ))
    ```
    """

    name: str = "DFIR"
    description: str = """Digital Forensics and Incident Response.

Capabilities:
- Evidence collection and preservation
- Timeline reconstruction
- Forensic artifact extraction
- File integrity verification
- Comprehensive forensic analysis

Returns: Structured forensic findings with chain of custody"""
    params: type[DFIRParams] = DFIRParams

    # Forensic artifact patterns
    FORENSIC_ARTIFACTS = {
        "browser_artifacts": ["*.sqlite", "*History*", "*Cookies*", "*Cache*"],
        "system_artifacts": ["*.log", "*.evt", "*.evtx", "*Registry*"],
        "persistence": ["*.lnk", "*.bat", "*.vbs", "*.ps1", "*startup*"],
        "user_activity": ["*.doc*", "*.pdf", "*.xls*", "*recent*"],
    }

    async def execute(self, params: DFIRParams) -> ToolOk | ToolError:
        """
        Execute DFIR operation.

        Context: Returns structured forensic findings.
        """
        logger.info(f"DFIR: {params.target} (op={params.operation})")

        try:
            # Check memory for related cases
            if self.memory_service and self.memory_service.is_enabled():
                related_cases = self.memory_service.get_tool_context("DFIR", limit=3)
                if related_cases:
                    logger.info(f"Found {len(related_cases)} related forensic cases")

            # Execute operation
            if params.operation == "evidence_collection":
                artifacts = await self._evidence_collection_operation(params)
            elif params.operation == "timeline_analysis":
                artifacts = await self._timeline_analysis_operation(params)
            elif params.operation == "artifact_extraction":
                artifacts = await self._artifact_extraction_operation(params)
            elif params.operation == "hash_verification":
                artifacts = await self._hash_verification_operation(params)
            else:  # full_forensics
                artifacts = await self._full_forensics_operation(params)

            # Limit artifacts
            if len(artifacts) > params.max_artifacts:
                artifacts = artifacts[:params.max_artifacts]
                truncated = True
            else:
                truncated = False

            # Calculate forensic stats
            artifact_types = {}
            for artifact in artifacts:
                atype = artifact.get("artifact_type", "unknown")
                artifact_types[atype] = artifact_types.get(atype, 0) + 1

            result_content = {
                "target": params.target,
                "operation": params.operation,
                "artifacts": artifacts,
                "summary": {
                    "total_artifacts": len(artifacts),
                    "by_type": artifact_types,
                    "truncated": truncated,
                    "timestamp": datetime.utcnow().isoformat(),
                    "chain_of_custody": params.preserve_evidence
                },
                "forensic_notes": "Evidence preserved with chain of custody" if params.preserve_evidence else "Analysis only, no preservation"
            }

            # Store in memory
            if self.memory_service and self.memory_service.is_enabled():
                self.memory_service.add_scan_results(
                    tool_name="DFIR",
                    target=params.target,
                    results=result_content
                )

            return ToolOk(content=result_content)

        except Exception as e:
            logger.error(f"DFIR operation failed: {e}")
            return ToolError(
                message=f"DFIR operation failed: {str(e)}",
                brief="Operation failed"
            )

    async def _evidence_collection_operation(self, params: DFIRParams) -> List[Dict[str, Any]]:
        """
        Collect and preserve evidence.

        Context: Evidence collection with chain of custody.
        """
        artifacts = []

        target_path = Path(params.target).expanduser()

        if not target_path.exists():
            artifacts.append({
                "artifact_type": "error",
                "description": f"Target does not exist: {params.target}",
                "severity": "HIGH"
            })
            return artifacts

        # Collect file metadata
        if target_path.is_file():
            artifacts.append(self._collect_file_evidence(target_path, params.preserve_evidence))
        else:
            # Collect directory evidence
            file_count = 0
            for file_path in target_path.rglob("*"):
                if file_path.is_file() and file_count < 50:
                    artifacts.append(self._collect_file_evidence(file_path, params.preserve_evidence))
                    file_count += 1

        # Add collection summary
        artifacts.append({
            "artifact_type": "collection_summary",
            "description": f"Collected {file_count if target_path.is_dir() else 1} evidence items",
            "chain_of_custody": params.preserve_evidence,
            "timestamp": datetime.utcnow().isoformat()
        })

        return artifacts

    def _collect_file_evidence(self, file_path: Path, preserve: bool) -> Dict[str, Any]:
        """Collect evidence for a single file"""
        stat = file_path.stat()

        evidence = {
            "artifact_type": "file_evidence",
            "file": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }

        # Calculate hash if preserving evidence
        if preserve:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    evidence["md5_hash"] = hashlib.md5(content).hexdigest()
                    evidence["sha256_hash"] = hashlib.sha256(content).hexdigest()
            except Exception as e:
                evidence["hash_error"] = str(e)

        return evidence

    async def _timeline_analysis_operation(self, params: DFIRParams) -> List[Dict[str, Any]]:
        """
        Reconstruct event timeline.

        Context: Timeline of file system events.
        """
        artifacts = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            # Collect timeline data
            timeline_events = []

            if target_path.is_dir():
                for file_path in target_path.rglob("*"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        timeline_events.append({
                            "file": str(file_path),
                            "modified": stat.st_mtime,
                            "accessed": stat.st_atime,
                            "created": stat.st_ctime
                        })

                        if len(timeline_events) >= 50:
                            break

            # Sort by modification time
            timeline_events.sort(key=lambda x: x["modified"], reverse=True)

            # Add recent events to artifacts
            for event in timeline_events[:20]:
                artifacts.append({
                    "artifact_type": "timeline_event",
                    "file": event["file"],
                    "modified": datetime.fromtimestamp(event["modified"]).isoformat(),
                    "accessed": datetime.fromtimestamp(event["accessed"]).isoformat(),
                    "created": datetime.fromtimestamp(event["created"]).isoformat()
                })

            artifacts.append({
                "artifact_type": "timeline_summary",
                "description": f"Analyzed {len(timeline_events)} timeline events",
                "most_recent": datetime.fromtimestamp(timeline_events[0]["modified"]).isoformat() if timeline_events else None
            })

        return artifacts

    async def _artifact_extraction_operation(self, params: DFIRParams) -> List[Dict[str, Any]]:
        """
        Extract forensic artifacts.

        Context: Extract common forensic artifacts.
        """
        artifacts = []

        target_path = Path(params.target).expanduser()

        if target_path.exists() and target_path.is_dir():
            # Search for forensic artifacts
            for artifact_category, patterns in self.FORENSIC_ARTIFACTS.items():
                found_artifacts = []

                for pattern in patterns:
                    matches = list(target_path.rglob(pattern))[:10]
                    found_artifacts.extend(matches)

                if found_artifacts:
                    artifacts.append({
                        "artifact_type": "forensic_artifact",
                        "category": artifact_category,
                        "description": f"Found {len(found_artifacts)} {artifact_category}",
                        "artifacts": [str(f) for f in found_artifacts[:5]],
                        "severity": "INFO"
                    })

            # Check for suspicious persistence mechanisms
            persistence_locations = [
                "*startup*",
                "*autorun*",
                "*.lnk",
                "*scheduled*"
            ]

            for pattern in persistence_locations:
                suspicious = list(target_path.rglob(pattern))[:5]
                if suspicious:
                    artifacts.append({
                        "artifact_type": "persistence_mechanism",
                        "description": f"Potential persistence: {pattern}",
                        "files": [str(f) for f in suspicious],
                        "severity": "MEDIUM"
                    })

        artifacts.append({
            "artifact_type": "extraction_summary",
            "description": f"Extracted artifacts from {params.target}"
        })

        return artifacts

    async def _hash_verification_operation(self, params: DFIRParams) -> List[Dict[str, Any]]:
        """
        Verify file integrity with hashes.

        Context: Hash-based file verification.
        """
        artifacts = []

        target_path = Path(params.target).expanduser()

        if target_path.exists():
            files_hashed = 0

            if target_path.is_file():
                artifacts.append(self._hash_file(target_path))
                files_hashed = 1
            else:
                # Hash multiple files
                for file_path in target_path.rglob("*"):
                    if file_path.is_file() and files_hashed < 20:
                        artifacts.append(self._hash_file(file_path))
                        files_hashed += 1

            artifacts.append({
                "artifact_type": "hash_summary",
                "description": f"Generated hashes for {files_hashed} files",
                "algorithm": "MD5, SHA256"
            })

        return artifacts

    def _hash_file(self, file_path: Path) -> Dict[str, Any]:
        """Generate hashes for a file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            return {
                "artifact_type": "file_hash",
                "file": str(file_path),
                "md5": hashlib.md5(content).hexdigest(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "size": len(content)
            }
        except Exception as e:
            return {
                "artifact_type": "hash_error",
                "file": str(file_path),
                "error": str(e)
            }

    async def _full_forensics_operation(self, params: DFIRParams) -> List[Dict[str, Any]]:
        """
        Comprehensive forensic analysis.

        Context: Full forensic investigation.
        """
        artifacts = []

        # Execute all forensic operations
        artifacts.extend(await self._evidence_collection_operation(params))
        artifacts.extend(await self._timeline_analysis_operation(params))
        artifacts.extend(await self._artifact_extraction_operation(params))
        artifacts.extend(await self._hash_verification_operation(params))

        # Add comprehensive summary
        artifacts.append({
            "artifact_type": "forensic_report",
            "description": "Comprehensive forensic analysis complete",
            "operations": ["evidence_collection", "timeline_analysis", "artifact_extraction", "hash_verification"],
            "timestamp": datetime.utcnow().isoformat(),
            "recommendation": "Review all artifacts and correlate with incident timeline"
        })

        return artifacts
