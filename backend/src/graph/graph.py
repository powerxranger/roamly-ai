"""Wires the agents together into the LangGraph workflow with semantic supervisor routing."""

from functools import lru_cache
from langgraph.graph import END, START, StateGraph

from src.agents.final_agent import final_agent
from src.agents.flight_agent import flight_agent
from src.agents.hotel_agent import hotel_agent
from src.agents.itinerary_agent import itinerary_agent
from src.agents.router_agent import router_agent
from src.agents.weather_agent import weather_agent
from src.clients.checkpointer import get_checkpointer
from src.graph.state import TravelState


def build_graph() -> StateGraph:
    """Build the uncompiled graph with the semantic supervisor routing node."""

    graph = StateGraph(TravelState)

    # 1. Register all nodes
    graph.add_node("router_agent", router_agent)
    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("final_agent", final_agent)

    # 2. START always activates the Lead Supervisor (Router Agent) first
    graph.add_edge(START, "router_agent")

    # 3. Parallel research fan-out from supervisor
    graph.add_edge("router_agent", "flight_agent")
    graph.add_edge("router_agent", "hotel_agent")
    graph.add_edge("router_agent", "weather_agent")

    # 4. Barrier Fan-in: wait for research nodes before architecting itinerary
    graph.add_edge("flight_agent", "itinerary_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("weather_agent", "itinerary_agent")

    # 5. Sequential executive synthesis
    graph.add_edge("itinerary_agent", "final_agent")
    graph.add_edge("final_agent", END)

    return graph


@lru_cache(maxsize=1)
def get_travel_graph():
    """Compile the graph with the in-memory checkpointer."""
    return build_graph().compile(checkpointer=get_checkpointer())
