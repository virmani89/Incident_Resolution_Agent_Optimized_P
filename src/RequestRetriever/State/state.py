from typing import TypedDict, Any


class IncidentState(TypedDict, total=False):
    user_issue: str
    candidates: list[dict[str, Any]]
    matched_incident: dict[str, Any]
    final_response: Any
    error: str
