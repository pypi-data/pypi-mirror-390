"""
Base classes for Alprina CLI tools.

Context Engineering Principles:
- Tools are callable utilities (not full LLM agents)
- Self-contained with clear input/output schemas
- Minimal token footprint in context
- MCP-compatible design
- Progressive disclosure pattern

Based on: Kimi-CLI CallableTool2 pattern
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Optional
from pydantic import BaseModel
from loguru import logger


# Tool return types (lightweight wrappers)
class ToolResult:
    """Base result from tool execution"""

    def __init__(self, content: Any, metadata: dict = None):
        self.content = content
        self.metadata = metadata or {}

    def __str__(self):
        return str(self.content)


class ToolOk(ToolResult):
    """Successful tool execution"""

    def __init__(self, content: Any = None, output: str = "", metadata: dict = None):
        super().__init__(content or output, metadata)
        self.output = output if output else str(content)


class ToolError(ToolResult):
    """Failed tool execution"""

    def __init__(self, message: str, brief: str = None, output: str = "", metadata: dict = None):
        super().__init__({"error": message, "brief": brief or message}, metadata)
        self.message = message
        self.brief = brief or message
        self.output = output


# Type variable for tool parameters
TParams = TypeVar('TParams', bound=BaseModel)


class AlprinaToolBase(ABC, Generic[TParams]):
    """
    Base class for all Alprina CLI tools.

    Context Engineering Benefits:
    - Lightweight: No embedded LLM, just callable functions
    - Clear contracts: Pydantic schemas for inputs/outputs
    - Composable: Can be used by multiple agents/commands
    - Testable: Pure functions with minimal dependencies
    - MCP-ready: Compatible with Model Context Protocol

    Usage:
    ```python
    class ScanParams(BaseModel):
        target: str = Field(description="Target to scan")

    class ScanTool(AlprinaToolBase[ScanParams]):
        name: str = "Scan"
        description: str = "Perform security scan"
        params: type[ScanParams] = ScanParams

        async def execute(self, params: ScanParams):
            result = await perform_scan(params.target)
            return ToolOk(content=result)
    ```
    """

    # Tool metadata (subclasses must define)
    name: str = "Tool"
    description: str = "Base tool"
    params: type[TParams] = BaseModel  # type: ignore

    # Optional: Guardrails for security validation
    input_guardrails: list = []
    output_guardrails: list = []
    enable_guardrails: bool = True

    # Optional: Memory service for context persistence
    memory_service: Optional[Any] = None

    # Optional: Database client for persistence
    database_client: Optional[Any] = None
    enable_database: bool = True

    # Optional: API key for authentication
    api_key: Optional[str] = None

    def __init__(
        self,
        memory_service: Optional[Any] = None,
        enable_guardrails: bool = True,
        database_client: Optional[Any] = None,
        enable_database: bool = True,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize tool with optional configuration.

        Args:
            memory_service: Optional MemoryService instance for context persistence
            enable_guardrails: Enable/disable guardrails (default: True)
            database_client: Optional NeonDatabaseClient for scan persistence
            enable_database: Enable/disable database persistence (default: True)
            api_key: Optional API key for authentication
            **kwargs: Additional configuration
        """
        self.memory_service = memory_service
        self.enable_guardrails = enable_guardrails
        self.database_client = database_client
        self.enable_database = enable_database
        self.api_key = api_key

        # Initialize default guardrails if not set
        if not self.input_guardrails and enable_guardrails:
            from alprina_cli.guardrails import DEFAULT_INPUT_GUARDRAILS
            self.input_guardrails = DEFAULT_INPUT_GUARDRAILS

        if not self.output_guardrails and enable_guardrails:
            from alprina_cli.guardrails import DEFAULT_OUTPUT_GUARDRAILS
            self.output_guardrails = DEFAULT_OUTPUT_GUARDRAILS

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    async def execute(self, params: TParams) -> ToolResult:
        """
        Execute the tool with given parameters.

        Context: This is where the actual work happens.
        Should return high-signal results (not verbose logs).

        Args:
            params: Validated parameters (Pydantic model)

        Returns:
            ToolOk: Success with result
            ToolError: Failure with error message
        """
        raise NotImplementedError

    async def __call__(self, params: TParams) -> ToolResult:
        """
        Call interface for the tool.

        Context: Applies guardrails, authentication, and database persistence.
        """
        import time
        start_time = time.time()
        user_id = None
        scan_id = None

        # Step 1: Authenticate user (if API key provided)
        if self.enable_database and self.database_client and self.api_key:
            try:
                auth_result = await self.database_client.authenticate_api_key(self.api_key)
                if not auth_result:
                    return ToolError(
                        message="Invalid or expired API key",
                        brief="Authentication failed",
                        metadata={"code": "AUTH_FAILED"}
                    )
                user_id = auth_result.get('user_id')
                logger.debug(f"Authenticated user: {user_id}")
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                # Continue without authentication (local usage)
                pass

        # Step 2: Check scan limits (if authenticated)
        if user_id and self.enable_database and self.database_client:
            try:
                can_scan, scans_used, scans_limit = await self.database_client.check_scan_limit(user_id)
                if not can_scan:
                    return ToolError(
                        message=f"Monthly scan limit exceeded ({scans_used}/{scans_limit})",
                        brief="Scan limit reached",
                        metadata={"scans_used": scans_used, "scans_limit": scans_limit}
                    )
                logger.debug(f"Scan limit check: {scans_used}/{scans_limit}")
            except Exception as e:
                logger.error(f"Scan limit check error: {e}")
                # Continue anyway (don't block on limit check errors)
                pass

        # Step 3: Create scan record (status: pending)
        if user_id and self.enable_database and self.database_client:
            try:
                # Extract target from params
                params_dict = params.model_dump() if hasattr(params, 'model_dump') else params.dict()
                target = params_dict.get('target', 'unknown')

                scan_id = await self.database_client.create_scan(
                    user_id=user_id,
                    tool_name=self.name,
                    target=target,
                    params=params_dict
                )
                logger.info(f"Created scan record: {scan_id}")
            except Exception as e:
                logger.error(f"Failed to create scan record: {e}")
                # Continue anyway (don't block on DB errors)
                pass

        # Step 4: Update scan status (running)
        if scan_id and self.enable_database and self.database_client:
            try:
                await self.database_client.update_scan_status(scan_id, "running")
            except Exception as e:
                logger.error(f"Failed to update scan status: {e}")

        # Step 5: Apply input guardrails
        if self.enable_guardrails and self.input_guardrails:
            try:
                from alprina_cli.guardrails import validate_input

                # Convert params to dict for validation
                params_dict = params.model_dump() if hasattr(params, 'model_dump') else params.dict()

                # Validate each parameter
                for param_name, value in params_dict.items():
                    validation_result = validate_input(value, param_name, guardrails=self.input_guardrails)

                    if not validation_result.passed:
                        logger.warning(
                            f"Input guardrail triggered in {self.name}.{param_name}: {validation_result.reason}"
                        )
                        if validation_result.tripwire_triggered:
                            # Critical violation - block execution and mark scan as failed
                            if scan_id and self.enable_database and self.database_client:
                                try:
                                    await self.database_client.save_scan_results(
                                        scan_id=scan_id,
                                        findings={"error": validation_result.reason},
                                        findings_count=0,
                                        status="failed"
                                    )
                                except Exception as e:
                                    logger.error(f"Failed to save scan failure: {e}")

                            return ToolError(
                                message=f"Security violation: {validation_result.reason}",
                                brief=f"Input guardrail blocked execution",
                                metadata={"severity": validation_result.severity, "param": param_name}
                            )
            except Exception as e:
                logger.error(f"Error applying input guardrails in {self.name}: {e}")
                # Don't block on guardrail errors, just log
                pass

        # Step 6: Execute tool
        result = await self.execute(params)
        duration_ms = int((time.time() - start_time) * 1000)

        # Step 7: Apply output guardrails (sanitize sensitive data)
        if self.enable_guardrails and self.output_guardrails and isinstance(result, ToolOk):
            try:
                from alprina_cli.guardrails import sanitize_output, sanitize_dict

                # Sanitize output content
                if isinstance(result.content, str):
                    sanitization_result = sanitize_output(result.content, guardrails=self.output_guardrails)
                    if sanitization_result.redactions_made > 0:
                        logger.info(
                            f"Output sanitized in {self.name}: {sanitization_result.redactions_made} redactions "
                            f"({', '.join(sanitization_result.redaction_types)})"
                        )
                        result.content = sanitization_result.sanitized_value
                        result.output = sanitization_result.sanitized_value

                elif isinstance(result.content, dict):
                    sanitized_content, redactions = sanitize_dict(result.content, guardrails=self.output_guardrails)
                    if redactions > 0:
                        logger.info(f"Output sanitized in {self.name}: {redactions} redactions")
                        result.content = sanitized_content

            except Exception as e:
                logger.error(f"Error applying output guardrails in {self.name}: {e}")
                # Don't block on sanitization errors, return original result
                pass

        # Step 8: Save scan results to database
        if scan_id and user_id and self.enable_database and self.database_client:
            try:
                # Extract findings and count
                findings = result.content if isinstance(result.content, dict) else {"output": str(result.content)}
                findings_count = 0

                if isinstance(result, ToolOk):
                    # Try to count findings from result
                    if isinstance(result.content, dict):
                        findings_count = len(result.content.get('findings', []))
                        if findings_count == 0 and 'vulnerabilities' in result.content:
                            findings_count = len(result.content.get('vulnerabilities', []))

                    # Save successful scan
                    await self.database_client.save_scan_results(
                        scan_id=scan_id,
                        findings=findings,
                        findings_count=findings_count,
                        status="completed"
                    )
                    logger.info(f"Saved scan results: {scan_id} ({findings_count} findings)")
                else:
                    # Save failed scan
                    await self.database_client.save_scan_results(
                        scan_id=scan_id,
                        findings={"error": getattr(result, 'message', str(result.content))},
                        findings_count=0,
                        status="failed"
                    )
                    logger.warning(f"Saved failed scan: {scan_id}")

            except Exception as e:
                logger.error(f"Failed to save scan results: {e}")

        # Step 9: Track usage for billing
        if scan_id and user_id and self.enable_database and self.database_client:
            try:
                # Determine credit cost (could be configurable per tool)
                credits_used = 1  # Default

                await self.database_client.track_scan_usage(
                    user_id=user_id,
                    scan_id=scan_id,
                    tool_name=self.name,
                    credits_used=credits_used,
                    duration_ms=duration_ms,
                    vulnerabilities_found=findings_count if isinstance(result, ToolOk) else 0
                )
                logger.debug(f"Tracked usage: {credits_used} credits, {duration_ms}ms")

                # Increment scan count
                await self.database_client.increment_scan_count(user_id)

            except Exception as e:
                logger.error(f"Failed to track usage: {e}")

        # Add scan_id to result metadata if available
        if scan_id and isinstance(result, ToolResult):
            if not result.metadata:
                result.metadata = {}
            result.metadata['scan_id'] = scan_id
            result.metadata['duration_ms'] = duration_ms

        return result

    def to_dict(self) -> dict:
        """
        Convert tool to dictionary representation.

        Context: Used for serialization and MCP integration.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.params.model_json_schema() if self.params else {}
        }

    def to_mcp_schema(self) -> dict:
        """
        Convert tool to MCP-compatible schema.

        Context: Enables integration with Model Context Protocol.
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.params.model_json_schema() if self.params else {}
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}'>"


class SyncToolBase(Generic[TParams]):
    """
    Synchronous version of AlprinaToolBase.

    Context: Use for tools that don't need async (rare).
    Most tools should use AlprinaToolBase (async).
    """

    name: str = "SyncTool"
    description: str = "Synchronous base tool"
    params: type[TParams] = BaseModel  # type: ignore

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def execute(self, params: TParams) -> ToolResult:
        """Execute synchronously"""
        raise NotImplementedError

    def __call__(self, params: TParams) -> ToolResult:
        return self.execute(params)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.params.model_json_schema() if self.params else {}
        }


# Convenience exports
__all__ = [
    "AlprinaToolBase",
    "SyncToolBase",
    "ToolResult",
    "ToolOk",
    "ToolError",
    "TParams"
]
