from langgraph.graph import StateGraph, START, END
from ..State.state import IncidentState
from ..Nodes.search_node import IncidentAgentNodes


class IncidentGraph:
    def __init__(self, llm=None, excel_file=None, searcher=None):
        self.nodes = IncidentAgentNodes(llm=llm, excel_file=excel_file, searcher=searcher)
        self.builder = StateGraph(IncidentState)

    def build(self):
        self.builder.add_node("retrieve_similar_incidents", self.nodes.retrieve_similar_incidents)
        self.builder.add_node("select_and_fetch_incident", self.nodes.select_and_fetch_incident)
        self.builder.add_node("generate_response", self.nodes.generate_response)
        self.builder.add_edge(START, "retrieve_similar_incidents")
        self.builder.add_edge("retrieve_similar_incidents", "select_and_fetch_incident")
        self.builder.add_edge("select_and_fetch_incident", "generate_response")
        self.builder.add_edge("generate_response", END)
        return self.builder.compile()
