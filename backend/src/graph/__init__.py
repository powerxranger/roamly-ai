from src.graph.state import TravelState, initial_state


def __getattr__(name: str):
    if name in ("build_graph", "get_travel_graph"):
        from src.graph.graph import build_graph, get_travel_graph

        return locals()[name]
    if name in ("run_travel_agent", "arun_travel_agent"):
        from src.graph.runner import arun_travel_agent, run_travel_agent

        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "TravelState",
    "arun_travel_agent",
    "build_graph",
    "get_travel_graph",
    "initial_state",
    "run_travel_agent",
]

