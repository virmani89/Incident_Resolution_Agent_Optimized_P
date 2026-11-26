from pathlib import Path
import streamlit as st
from ..Graph.graph import IncidentGraph
from ..Tools.search_tool import IncidentSearch
from .display_result import display_result

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXCEL_FILE = PROJECT_ROOT / "data" / "IncidentResolution.xlsx"


@st.cache_resource(show_spinner="Loading incident knowledge base...")
def get_searcher(excel_path: str, modified_time: float):
    # modified_time invalidates the cache automatically when the workbook changes.
    return IncidentSearch(excel_path)


@st.cache_resource(show_spinner=False)
def get_compiled_graph(excel_path: str, modified_time: float):
    searcher = get_searcher(excel_path, modified_time)
    return IncidentGraph(excel_file=excel_path, searcher=searcher).build()


def load_ui():
    st.title("Agentic AI Incident Resolution Assistant")
    st.write("Find similar historical incidents and retrieve their recorded RCA, impact, resolution and defect reference.")
    if not EXCEL_FILE.exists():
        st.error(f"Knowledge base not found: {EXCEL_FILE}")
        return
    modified_time = EXCEL_FILE.stat().st_mtime
    st.caption(f"Knowledge base: {EXCEL_FILE.name}")
    user_issue = st.text_area(
        "Describe your issue",
        placeholder="Example: A policy transaction is not appearing in PolicyView even though it was issued.",
        height=120,
    )
    if st.button("Find Resolution", type="primary"):
        if not user_issue.strip():
            st.warning("Please describe the incident first.")
            return
        try:
            graph = get_compiled_graph(str(EXCEL_FILE), modified_time)
            with st.spinner("Searching historical incidents..."):
                result = graph.invoke({"user_issue": user_issue.strip()})
            st.subheader("Resolution")
            if result.get("error"):
                st.warning(result["error"])
            display_result(result.get("final_response", "No result was generated."))
        except Exception as exc:
            st.error(f"Unable to process the request: {exc}")
