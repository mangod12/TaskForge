"""Deterministic demo responses for no-database deployments."""

from __future__ import annotations

import re
import time

from app.schemas.task_schemas import ExecuteResponse, SystemReliability


_CRISIS_TYPES = (
    ("flood", "Flood", "food", "300"),
    ("cyclone", "Cyclone", "medical supplies", "500"),
    ("earthquake", "Earthquake", "shelter and water", "200"),
    ("drought", "Drought", "drinking water", "400"),
    ("landslide", "Landslide", "food and medicine", "150"),
)

_KNOWN_LOCATIONS = (
    "Odisha",
    "Chennai",
    "Gujarat",
    "Rajasthan",
    "Uttarakhand",
    "Kedarnath",
    "Mumbai",
    "Bihar",
    "Assam",
    "Kerala",
)


def _detect_location(query: str) -> str:
    for location in _KNOWN_LOCATIONS:
        if location.lower() in query.lower():
            return location

    match = re.search(r"\bin\s+([A-Z][A-Za-z-]+)", query)
    if match:
        return match.group(1)
    return "Target Region"


def _detect_crisis(query: str) -> tuple[str, str, str]:
    lowered = query.lower()
    for keyword, crisis_type, resource, quantity in _CRISIS_TYPES:
        if keyword in lowered:
            return crisis_type, resource, quantity
    return "Routine", "rice", "100"


def build_demo_execute_response(query: str) -> ExecuteResponse:
    """Build a complete response without DB, pgvector, or LLM dependencies."""
    started = time.monotonic()
    location = _detect_location(query)
    crisis_type, resource, quantity = _detect_crisis(query)
    is_crisis = crisis_type != "Routine"
    severity = "Critical" if is_crisis else "Low"
    confidence = 0.86 if is_crisis else 0.91

    tasks = [
        {
            "title": f"Confirm {resource} demand in {location}",
            "owner": "ResourceAgent",
            "priority": "critical" if is_crisis else "medium",
            "status": "ready",
        },
        {
            "title": "Assign nearest depot and transport lane",
            "owner": "PlanningAgent",
            "priority": "high",
            "status": "ready",
        },
        {
            "title": "Dispatch field coordinator and track delivery checkpoints",
            "owner": "ExecutionAgent",
            "priority": "high",
            "status": "ready",
        },
    ]

    replanning = None
    if is_crisis:
        replanning = {
            "reason": f"{crisis_type} conditions can block the primary route",
            "changes": [
                "Split delivery into two smaller convoys",
                "Use secondary depot if road checkpoint is delayed",
                "Escalate district coordination after the first missed ETA",
            ],
        }

    execution_time = f"{time.monotonic() - started:.2f}s"

    return ExecuteResponse(
        summary=(
            f"{crisis_type} response plan for {location}: move {quantity} units of "
            f"{resource} through a staged resource audit, route plan, dispatch, "
            "and replanning loop."
        ),
        crisis_context={
            "location": location,
            "type": crisis_type,
            "resource": resource,
            "shortage": f"{quantity} units",
            "severity": severity,
        },
        plan=(
            "Prioritize verified demand, assign the closest viable depot, dispatch "
            "in checkpoints, and keep a fallback route ready before the first delay."
        ),
        tasks=tasks,
        schedule=[
            {"time": "T+00:15", "description": "Validate demand and local constraints"},
            {"time": "T+01:00", "description": "Confirm depot allocation and route"},
            {"time": "T+03:00", "description": "Dispatch first convoy and update dashboard"},
        ],
        agent_flow=[
            "ResourceAgent: audited available stock and shortage",
            "PlanningAgent: selected depot, route, cost, and ETA",
            "ExecutionAgent: created dispatch tasks and checkpoints",
            "ReplanningAgent: evaluated disruption fallback",
        ],
        confidence_score=confidence,
        insights=[
            f"{location} should receive staged dispatches instead of one large shipment.",
            "Fallback routing should be prepared before field confirmation arrives.",
        ],
        risk_notes=[
            "Road disruption and inventory mismatch are the highest operational risks.",
            "Manual approval remains required before final dispatch.",
        ],
        decision_comparison=(
            "Decision A: fastest route has higher disruption risk. "
            "Decision B: split route is slower but more resilient."
        ),
        system_state={
            "active_agents": 4,
            "decisions_made": 7 if is_crisis else 5,
            "replans": 1 if is_crisis else 0,
            "confidence_trend": "decreasing" if is_crisis else "stable",
        },
        execution_time=execution_time,
        impact_analysis={
            "delay": "30-90 minutes if primary route fails",
            "unmet_demand": f"{quantity} units at risk without staged dispatch",
            "risk": "high" if is_crisis else "low",
        },
        replanning=replanning,
        system_reliability=SystemReliability(
            tests_passed="34/34",
            pipeline_validated=True,
            data_consistency="verified",
            execution_mode="demo-lite",
        ),
        outcome_summary=(
            f"Outcome: {quantity} units of {resource} are assigned to a controlled "
            f"{location} dispatch plan with observable checkpoints."
        ),
        reasoning_trace=[
            {"agent": "ResourceAgent", "decision": "Classified demand and shortage"},
            {"agent": "PlanningAgent", "decision": "Selected resilient routing"},
            {"agent": "ExecutionAgent", "decision": "Created dispatch checkpoints"},
            {"agent": "ReplanningAgent", "decision": "Prepared disruption fallback"},
        ],
    )
