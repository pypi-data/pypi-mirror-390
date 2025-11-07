"""Workflow-specific metrics and analysis for OpenTelemetry tracing."""

from typing import Any, Dict, List


def analyze_workflow_structure(workflow) -> Dict[str, Any]:
    """
    Analyze workflow structure to extract metrics.

    Args:
        workflow: List of top-level steps

    Returns:
        Dictionary of workflow metrics
    """
    metrics = {}

    total_steps = count_total_steps(workflow)
    metrics["sup.workflow.total_steps"] = total_steps

    metrics["sup.workflow.top_level_steps"] = len(workflow)

    step_ids = extract_step_ids(workflow)
    metrics["sup.workflow.step_ids"] = step_ids

    max_depth = calculate_max_depth(workflow)
    metrics["sup.workflow.max_depth"] = max_depth

    return metrics


def count_total_steps(steps) -> int:
    """Count total number of steps including nested ones."""
    count = len(steps)
    for step in steps:
        if step.steps:
            count += count_total_steps(step.steps)
    return count


def extract_step_ids(steps) -> List[str]:
    """Extract all step IDs from workflow."""
    step_ids = []
    for step in steps:
        step_ids.append(step.step_id)
        if step.steps:
            step_ids.extend(extract_step_ids(step.steps))
    return step_ids


def calculate_max_depth(steps, current_depth: int = 1) -> int:
    """Calculate maximum depth of the workflow tree."""
    max_depth = current_depth
    for step in steps:
        if step.steps:
            depth = calculate_max_depth(step.steps, current_depth + 1)
            max_depth = max(max_depth, depth)
    return max_depth
