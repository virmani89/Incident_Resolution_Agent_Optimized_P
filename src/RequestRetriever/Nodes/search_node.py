from ..State.state import IncidentState
from ..Tools.search_tool import IncidentSearch


class IncidentAgentNodes:
    """Fast deterministic retrieval; no remote LLM call is needed to rank 9 Excel rows."""
    def __init__(self, llm=None, excel_file=None, searcher=None):
        self.searcher = searcher or IncidentSearch(excel_file)

    def retrieve_similar_incidents(self, state: IncidentState):
        candidates = self.searcher.search(state.get("user_issue", ""), top_k=5)
        return {"candidates": candidates}

    def select_and_fetch_incident(self, state: IncidentState):
        candidates = state.get("candidates", [])
        if not candidates:
            return {"matched_incident": {}}
        # Use the top-ranked record directly. This avoids a slow Groq round-trip
        # and prevents the LLM from discarding a valid retrieval result.
        best = candidates[0]
        if best.get("retrieval_score", 0.0) < 0.10:
            return {"matched_incident": {}}
        return {"matched_incident": best}

    def generate_response(self, state: IncidentState):
        item = state.get("matched_incident") or {}
        if not item:
            return {"final_response": (
                "No sufficiently similar incident was found in the Excel knowledge base. "
                "Please include the affected application, function, or observed behaviour."
            )}
        return {"final_response": {
            "Reference issue": item["issue"],
            "Problem Statement": item["problem_statement"],
            "Impact": item["impact"],
            "RCA": item["rca"],
            "Resolution": item["resolution"],
            "Defect ID": item["defect_id"],
            "Retrieval score": item["retrieval_score"],
            "Note": "Retrieved from the closest historical Excel record. Confirm applicability before implementing the resolution.",
        }}
