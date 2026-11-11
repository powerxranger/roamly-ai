"""Wires the agents together into the LangGraph workflow with semantic supervisor routing."""

from functools import lru_cache
from langgraph.graph import END, START, StateGraph

from src.agents.advisor_agent import advisor_agent
from src.agents.final_agent import final_agent
from src.agents.flight_agent import flight_agent
from src.agents.hotel_agent import hotel_agent
from src.agents.itinerary_agent import itinerary_agent
from src.agents.router_agent import router_agent
from src.agents.weather_agent import weather_agent
from src.clients.checkpointer import get_checkpointer
from src.graph.state import TravelState


def scout_fanout(state: TravelState) -> dict:
    """Pass-through coordinator that fans out in parallel to research scouts."""
    return {"response_type": "plan"}


def route_supervisor(state: TravelState) -> str:
    """Determine dynamic execution path based on classified travel intent.

    Path 1 & 2 (Plan creation or modification): Routes to scout fan-out.
    Path 3 (Local Q&A, recommendations, food, advice): Fast-paths to advisor agent.
    """
    intent = state.get("intent") or {}
    intent_type = intent.get("intent_type", "initial_planning")

    if intent_type == "general_question":
        return "advisor_agent"

    return "scout_fanout"


def build_graph() -> StateGraph:
    """Build the uncompiled graph with dynamic conditional routing."""

    graph = StateGraph(TravelState)

    # 1. Register all nodes
    graph.add_node("router_agent", router_agent)
    graph.add_node("advisor_agent", advisor_agent)
    graph.add_node("scout_fanout", scout_fanout)
    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("final_agent", final_agent)

    # 2. START always activates the Lead Supervisor (Router Agent) first
    graph.add_edge(START, "router_agent")

    # 3. Dynamic Conditional Routing: Fast advisor vs Planning pipeline
    graph.add_conditional_edges(
        "router_agent",
        route_supervisor,
        {
            "advisor_agent": "advisor_agent",
            "scout_fanout": "scout_fanout",
        },
    )

    # 4. Path 3: Advisor completes directly to END (fast 1-hop path)
    graph.add_edge("advisor_agent", END)

    # 5. Path 1 & 2: Parallel research fan-out from scout_fanout
    graph.add_edge("scout_fanout", "flight_agent")
    graph.add_edge("scout_fanout", "hotel_agent")
    graph.add_edge("scout_fanout", "weather_agent")

    # 6. Barrier Fan-in: wait for research nodes before architecting itinerary
    graph.add_edge("flight_agent", "itinerary_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("weather_agent", "itinerary_agent")

    # 7. Sequential executive synthesis
    graph.add_edge("itinerary_agent", "final_agent")
    graph.add_edge("final_agent", END)

    return graph


@lru_cache(maxsize=1)
def get_travel_graph():
    """Compile the graph with the in-memory checkpointer."""
    return build_graph().compile(checkpointer=get_checkpointer())
