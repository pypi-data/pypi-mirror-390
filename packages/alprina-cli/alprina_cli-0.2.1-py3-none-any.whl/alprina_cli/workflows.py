"""
Alprina Agent Workflows - Structured orchestration patterns.

Implements AI SDK workflow patterns for coordinating security agents:
- Sequential (Chain): Step-by-step security analysis
- Routing: Intelligent agent selection
- Parallel: Run multiple agents simultaneously
- Orchestrator-Worker: Main Agent coordinates specialized agents
- Evaluator-Optimizer: Quality control and error recovery

Reference: https://ai-sdk.dev/docs/agents/workflows
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from loguru import logger
from datetime import datetime
import asyncio


class WorkflowType(Enum):
    """Types of agent workflows."""
    SEQUENTIAL = "sequential"          # Chain: A → B → C
    ROUTING = "routing"                # Route to best agent
    PARALLEL = "parallel"              # Run agents concurrently
    ORCHESTRATOR_WORKER = "orchestrator_worker"  # Main coordinates workers
    EVALUATOR_OPTIMIZER = "evaluator_optimizer"  # Quality control loop


class WorkflowResult:
    """Result from workflow execution."""

    def __init__(self, success: bool = True):
        self.success = success
        self.steps = []
        self.errors = []
        self.start_time = datetime.now()
        self.end_time = None
        self.final_output = None
        self.metadata = {}

    def add_step(self, step_name: str, output: Any, agent: str = None):
        """Add a completed workflow step."""
        self.steps.append({
            "name": step_name,
            "agent": agent,
            "output": output,
            "timestamp": datetime.now().isoformat()
        })

    def add_error(self, error: str, step: str = None):
        """Add an error that occurred during workflow."""
        self.errors.append({
            "error": error,
            "step": step,
            "timestamp": datetime.now().isoformat()
        })
        self.success = False

    def complete(self, final_output: Any):
        """Mark workflow as complete."""
        self.end_time = datetime.now()
        self.final_output = final_output

    def duration(self) -> float:
        """Get workflow duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "steps": self.steps,
            "errors": self.errors,
            "duration": self.duration(),
            "final_output": self.final_output,
            "metadata": self.metadata
        }


class AlprinaWorkflow:
    """
    Base workflow orchestrator for Alprina agents.

    Implements the Orchestrator-Worker pattern where the Main Alprina Agent
    coordinates specialized security agents through structured workflows.
    """

    def __init__(self, workflow_type: WorkflowType = WorkflowType.ORCHESTRATOR_WORKER):
        """
        Initialize workflow.

        Args:
            workflow_type: Type of workflow pattern to use
        """
        self.workflow_type = workflow_type
        self.result = WorkflowResult()
        logger.info(f"Initialized {workflow_type.value} workflow")

    async def execute_sequential(
        self,
        steps: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> WorkflowResult:
        """
        Execute sequential workflow (Chain pattern).

        Steps executed in order: A → B → C
        Each step's output becomes next step's input.

        Args:
            steps: List of steps [{agent, task, params}]
            context: Shared context across steps

        Returns:
            WorkflowResult with final output

        Example:
            steps = [
                {"agent": "secret_detection", "task": "scan", "params": {"target": "./"}},
                {"agent": "codeagent", "task": "analyze_secrets", "params": {}},
                {"agent": "report_generator", "task": "create_report", "params": {}}
            ]
        """
        logger.info(f"Starting sequential workflow with {len(steps)} steps")

        current_output = context or {}

        for i, step in enumerate(steps, 1):
            try:
                logger.info(f"Step {i}/{len(steps)}: {step.get('task')} via {step.get('agent')}")

                # Execute step with previous output as input
                step_output = await self._execute_step(
                    agent=step["agent"],
                    task=step["task"],
                    params={**step.get("params", {}), "input": current_output}
                )

                self.result.add_step(
                    step_name=step["task"],
                    output=step_output,
                    agent=step["agent"]
                )

                # Output becomes input for next step
                current_output = step_output

            except Exception as e:
                logger.error(f"Step {i} failed: {e}")
                self.result.add_error(str(e), step=step["task"])
                break

        self.result.complete(current_output)
        return self.result

    async def execute_routing(
        self,
        user_request: str,
        available_agents: List[Dict[str, Any]],
        router_fn: Callable
    ) -> WorkflowResult:
        """
        Execute routing workflow.

        Router intelligently selects best agent based on request.

        Args:
            user_request: User's natural language request
            available_agents: List of available agents
            router_fn: Function that routes request to agent

        Returns:
            WorkflowResult with selected agent's output

        Example:
            router_fn decides: "scan code" → CodeAgent
                              "check API" → Web Scanner Agent
        """
        logger.info("Starting routing workflow")

        try:
            # Route to best agent
            selected_agent = router_fn(user_request, available_agents)
            logger.info(f"Routed to: {selected_agent['name']}")

            # Execute with selected agent
            output = await self._execute_step(
                agent=selected_agent["id"],
                task=selected_agent["task"],
                params=selected_agent.get("params", {})
            )

            self.result.add_step(
                step_name="routing_decision",
                output={"selected_agent": selected_agent["name"]},
                agent="router"
            )

            self.result.add_step(
                step_name=selected_agent["task"],
                output=output,
                agent=selected_agent["id"]
            )

            self.result.complete(output)

        except Exception as e:
            logger.error(f"Routing workflow failed: {e}")
            self.result.add_error(str(e))
            self.result.complete(None)

        return self.result

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> WorkflowResult:
        """
        Execute parallel workflow.

        Multiple agents run simultaneously for efficiency.

        Args:
            tasks: List of independent tasks to run in parallel
            context: Shared context

        Returns:
            WorkflowResult with all outputs

        Example:
            Scan code + Check secrets + Audit config simultaneously
        """
        logger.info(f"Starting parallel workflow with {len(tasks)} tasks")

        try:
            # Create async tasks
            async_tasks = []
            for task in tasks:
                async_task = self._execute_step(
                    agent=task["agent"],
                    task=task["task"],
                    params={**task.get("params", {}), **(context or {})}
                )
                async_tasks.append(async_task)

            # Execute all in parallel
            outputs = await asyncio.gather(*async_tasks, return_exceptions=True)

            # Process results
            for i, (task, output) in enumerate(zip(tasks, outputs)):
                if isinstance(output, Exception):
                    logger.error(f"Task {i+1} failed: {output}")
                    self.result.add_error(str(output), step=task["task"])
                else:
                    self.result.add_step(
                        step_name=task["task"],
                        output=output,
                        agent=task["agent"]
                    )

            # Aggregate all outputs
            final_output = {
                "parallel_results": [
                    {"task": t["task"], "output": o}
                    for t, o in zip(tasks, outputs)
                    if not isinstance(o, Exception)
                ]
            }

            self.result.complete(final_output)

        except Exception as e:
            logger.error(f"Parallel workflow failed: {e}")
            self.result.add_error(str(e))
            self.result.complete(None)

        return self.result

    async def execute_orchestrator_worker(
        self,
        orchestrator_agent: str,
        workers: List[Dict[str, Any]],
        task: str,
        params: Dict[str, Any]
    ) -> WorkflowResult:
        """
        Execute Orchestrator-Worker workflow.

        Main Agent (orchestrator) coordinates specialized workers.
        This is the PRIMARY pattern for Alprina!

        Args:
            orchestrator_agent: Main agent coordinating work
            workers: List of worker agents [{agent, task, params}]
            task: Overall task to accomplish
            params: Parameters for orchestration

        Returns:
            WorkflowResult with coordinated output

        Example:
            Orchestrator: Main Alprina Agent
            Workers: [CodeAgent, Web Scanner, Secret Detection]
            Task: "Comprehensive security scan"
        """
        logger.info(f"Starting orchestrator-worker workflow: {orchestrator_agent} coordinating {len(workers)} workers")

        try:
            # Step 1: Orchestrator plans work
            plan = await self._execute_step(
                agent=orchestrator_agent,
                task="plan_work",
                params={"task": task, "workers": workers, **params}
            )

            self.result.add_step(
                step_name="orchestration_planning",
                output=plan,
                agent=orchestrator_agent
            )

            # Step 2: Execute worker tasks
            worker_results = []
            for worker in workers:
                try:
                    result = await self._execute_step(
                        agent=worker["agent"],
                        task=worker["task"],
                        params=worker.get("params", {})
                    )

                    self.result.add_step(
                        step_name=worker["task"],
                        output=result,
                        agent=worker["agent"]
                    )

                    worker_results.append({
                        "agent": worker["agent"],
                        "output": result
                    })

                except Exception as e:
                    logger.error(f"Worker {worker['agent']} failed: {e}")
                    self.result.add_error(str(e), step=worker["task"])

            # Step 3: Orchestrator aggregates results
            final_output = await self._execute_step(
                agent=orchestrator_agent,
                task="aggregate_results",
                params={
                    "worker_results": worker_results,
                    "original_task": task
                }
            )

            self.result.add_step(
                step_name="result_aggregation",
                output=final_output,
                agent=orchestrator_agent
            )

            self.result.complete(final_output)

        except Exception as e:
            logger.error(f"Orchestrator-worker workflow failed: {e}")
            self.result.add_error(str(e))
            self.result.complete(None)

        return self.result

    async def execute_evaluator_optimizer(
        self,
        agent: str,
        task: str,
        params: Dict[str, Any],
        evaluator_fn: Callable,
        max_iterations: int = 3
    ) -> WorkflowResult:
        """
        Execute Evaluator-Optimizer workflow.

        Quality control loop: Execute → Evaluate → Improve → Repeat

        Args:
            agent: Agent to execute task
            task: Task to perform
            params: Task parameters
            evaluator_fn: Function to evaluate output quality
            max_iterations: Maximum improvement iterations

        Returns:
            WorkflowResult with optimized output

        Example:
            1. CodeAgent scans code
            2. Evaluator checks for false positives
            3. If quality < threshold, re-scan with refined params
            4. Repeat until quality acceptable or max iterations
        """
        logger.info(f"Starting evaluator-optimizer workflow (max {max_iterations} iterations)")

        best_output = None
        best_score = 0.0

        for iteration in range(1, max_iterations + 1):
            try:
                logger.info(f"Iteration {iteration}/{max_iterations}")

                # Execute task
                output = await self._execute_step(
                    agent=agent,
                    task=task,
                    params=params
                )

                # Evaluate quality
                evaluation = evaluator_fn(output)
                score = evaluation.get("score", 0.0)
                feedback = evaluation.get("feedback", "")

                logger.info(f"Quality score: {score:.2f} - {feedback}")

                self.result.add_step(
                    step_name=f"iteration_{iteration}",
                    output={
                        "result": output,
                        "score": score,
                        "feedback": feedback
                    },
                    agent=agent
                )

                # Track best result
                if score > best_score:
                    best_score = score
                    best_output = output

                # Check if quality acceptable
                if evaluation.get("acceptable", False):
                    logger.info(f"Quality acceptable after {iteration} iterations")
                    break

                # Optimize parameters for next iteration
                if iteration < max_iterations:
                    params = self._optimize_params(params, evaluation)

            except Exception as e:
                logger.error(f"Iteration {iteration} failed: {e}")
                self.result.add_error(str(e), step=f"iteration_{iteration}")
                break

        self.result.metadata["iterations"] = iteration
        self.result.metadata["best_score"] = best_score
        self.result.complete(best_output)

        return self.result

    async def _execute_step(
        self,
        agent: str,
        task: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Execute a single workflow step with actual Alprina agents.

        Args:
            agent: Agent identifier
            task: Task to perform
            params: Task parameters

        Returns:
            Step output
        """
        logger.debug(f"Executing: {agent}.{task}()")

        # Import here to avoid circular dependencies
        from .security_engine import run_agent, run_local_scan, run_remote_scan
        from .report_generator import generate_security_reports
        from pathlib import Path

        try:
            # Route to appropriate Alprina agent
            if task in ["scan", "code_audit", "web_recon", "vuln_scan", "secret_detection", "config_audit"]:
                target = params.get("target")

                if not target:
                    return {"error": "No target specified", "agent": agent}

                # Determine if local or remote scan
                is_local = Path(target).exists() if target else False

                if is_local:
                    # Local file/directory scan
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        run_local_scan,
                        target,
                        task if task != "scan" else "code-audit",
                        params.get("safe_only", True)
                    )
                else:
                    # Remote URL/IP scan
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        run_remote_scan,
                        target,
                        task if task != "scan" else "web-recon",
                        params.get("safe_only", True)
                    )

                return result

            elif task == "create_reports" or task == "generate_reports":
                # Generate markdown reports
                scan_results = params.get("input") or params.get("results")
                target = params.get("target")

                if scan_results and target:
                    report_path = await asyncio.get_event_loop().run_in_executor(
                        None,
                        generate_security_reports,
                        scan_results,
                        target
                    )
                    return {"report_path": report_path, "status": "success"}

                return {"error": "Missing scan results or target", "agent": agent}

            elif task == "plan_work":
                # Orchestrator planning step
                return {
                    "plan": "analyzed_request",
                    "workers_assigned": params.get("workers", []),
                    "status": "planned"
                }

            elif task == "aggregate_results":
                # Orchestrator aggregation step
                worker_results = params.get("worker_results", [])
                return {
                    "aggregated": True,
                    "total_findings": sum(
                        len(r.get("output", {}).get("findings", []))
                        for r in worker_results
                    ),
                    "worker_results": worker_results,
                    "status": "aggregated"
                }

            else:
                # Generic agent execution
                logger.warning(f"Unknown task type: {task}, using run_agent fallback")
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    run_agent,
                    task,
                    params.get("input_data", ""),
                    params.get("metadata", {})
                )
                return result

        except Exception as e:
            logger.error(f"Step execution failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "agent": agent,
                "task": task,
                "status": "failed"
            }

    def _optimize_params(
        self,
        params: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize parameters based on evaluation feedback.

        Args:
            params: Current parameters
            evaluation: Evaluation result with feedback

        Returns:
            Optimized parameters
        """
        # Example optimization logic
        optimized = params.copy()

        feedback = evaluation.get("feedback", "").lower()

        # Adjust based on feedback
        if "too many false positives" in feedback:
            optimized["confidence_threshold"] = optimized.get("confidence_threshold", 0.5) + 0.1

        if "missed vulnerabilities" in feedback:
            optimized["sensitivity"] = optimized.get("sensitivity", 0.5) + 0.1

        return optimized


# Quality evaluator functions

def evaluate_scan_quality(output: Any) -> Dict[str, Any]:
    """
    Evaluate quality of scan results.

    Checks for:
    - False positive indicators
    - Coverage completeness
    - Confidence scores
    - Result consistency

    Args:
        output: Scan results to evaluate

    Returns:
        Evaluation dict with score and feedback
    """
    findings = output.get("findings", []) if isinstance(output, dict) else []

    if not findings:
        return {
            "score": 1.0,
            "acceptable": True,
            "feedback": "No findings - scan complete"
        }

    # Count findings by severity
    severity_counts = {}
    low_confidence_count = 0
    total_findings = len(findings)

    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Check confidence if available
        confidence = finding.get("confidence", 1.0)
        if confidence < 0.6:
            low_confidence_count += 1

    # Calculate quality score
    false_positive_ratio = low_confidence_count / total_findings if total_findings > 0 else 0
    quality_score = 1.0 - (false_positive_ratio * 0.5)  # Penalize for low confidence findings

    # Acceptable if score >= 0.7 and not too many critical with low confidence
    acceptable = quality_score >= 0.7

    feedback = []
    if false_positive_ratio > 0.3:
        feedback.append(f"High false positive ratio ({false_positive_ratio:.1%})")
    if severity_counts.get("CRITICAL", 0) > 10:
        feedback.append("Unusually high critical findings - verify accuracy")

    return {
        "score": quality_score,
        "acceptable": acceptable,
        "feedback": "; ".join(feedback) if feedback else "Quality acceptable",
        "metrics": {
            "total_findings": total_findings,
            "low_confidence": low_confidence_count,
            "false_positive_ratio": false_positive_ratio,
            "severity_distribution": severity_counts
        }
    }


def evaluate_comprehensive_scan(output: Any) -> Dict[str, Any]:
    """
    Evaluate comprehensive security scan results from multiple agents.

    Args:
        output: Workflow results from parallel/orchestrator-worker execution

    Returns:
        Evaluation dict
    """
    if isinstance(output, dict) and "parallel_results" in output:
        # Parallel execution results
        results = output["parallel_results"]
        total_findings = sum(
            len(r.get("output", {}).get("findings", []))
            for r in results
        )

        # Check coverage - did all agents run?
        expected_agents = {"codeagent", "secret_detection", "config_audit"}
        agents_run = {r.get("task") for r in results}

        coverage = len(agents_run & expected_agents) / len(expected_agents)

        return {
            "score": coverage,
            "acceptable": coverage >= 0.66,  # At least 2/3 agents ran
            "feedback": f"Coverage: {coverage:.1%} ({len(agents_run)}/{len(expected_agents)} agents)",
            "metrics": {
                "total_findings": total_findings,
                "agents_run": list(agents_run),
                "coverage": coverage
            }
        }

    # Single scan result
    return evaluate_scan_quality(output)


# Convenience functions for common workflows

async def comprehensive_security_scan(target: str) -> WorkflowResult:
    """
    Run comprehensive security scan using orchestrator-worker pattern.

    Orchestrator: Main Alprina Agent
    Workers: CodeAgent, Secret Detection, Config Audit

    Args:
        target: Path to scan

    Returns:
        WorkflowResult with all findings
    """
    workflow = AlprinaWorkflow(WorkflowType.ORCHESTRATOR_WORKER)

    return await workflow.execute_orchestrator_worker(
        orchestrator_agent="main_alprina_agent",
        workers=[
            {
                "agent": "codeagent",
                "task": "code_audit",
                "params": {"target": target}
            },
            {
                "agent": "secret_detection",
                "task": "find_secrets",
                "params": {"target": target}
            },
            {
                "agent": "config_audit",
                "task": "audit_configs",
                "params": {"target": target}
            }
        ],
        task="comprehensive_scan",
        params={"target": target}
    )


async def parallel_multi_target_scan(targets: List[str]) -> WorkflowResult:
    """
    Scan multiple targets in parallel.

    Args:
        targets: List of paths/URLs to scan

    Returns:
        WorkflowResult with all scan results
    """
    workflow = AlprinaWorkflow(WorkflowType.PARALLEL)

    tasks = [
        {
            "agent": "codeagent",
            "task": "scan",
            "params": {"target": target}
        }
        for target in targets
    ]

    return await workflow.execute_parallel(tasks)


async def sequential_scan_and_report(target: str) -> WorkflowResult:
    """
    Sequential workflow: Scan → Analyze → Generate Report

    Args:
        target: Path to scan

    Returns:
        WorkflowResult with final report
    """
    workflow = AlprinaWorkflow(WorkflowType.SEQUENTIAL)

    steps = [
        {
            "agent": "codeagent",
            "task": "scan",
            "params": {"target": target}
        },
        {
            "agent": "main_alprina_agent",
            "task": "analyze_findings",
            "params": {}
        },
        {
            "agent": "report_generator",
            "task": "create_markdown_reports",
            "params": {}
        }
    ]

    return await workflow.execute_sequential(steps)
