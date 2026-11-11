"""Entry point the API layer calls to run one travel planning request."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from langchain_core.messages import HumanMessage

from src.config.settings import has_llm_key
from src.graph.graph import get_travel_graph
from src.graph.state import initial_state


def _verify_llm_configured():
    if not has_llm_key():
        raise ValueError(
            "No LLM API keys found. Please set GEMINI_API_KEY or GROQ_API_KEY in your .env file."
        )


def _prepare_graph_input(user_input: str, existing_state: dict | None) -> dict:
    """Construct the graph input dictionary, preserving existing trip state on follow-ups."""
    if existing_state:
        followup_history = list(existing_state.get("followup_history", []))
        followup_history.append(user_input)

        return {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "destination": existing_state.get("destination", ""),
            "origin": existing_state.get("origin", ""),
            "travel_dates": existing_state.get("travel_dates"),
            "flight_results": existing_state.get("flight_results", ""),
            "hotel_results": existing_state.get("hotel_results", ""),
            "weather_results": existing_state.get("weather_results", ""),
            "itinerary": existing_state.get("itinerary", ""),
            "flight_model": existing_state.get("flight_model"),
            "hotel_model": existing_state.get("hotel_model"),
            "itinerary_model": existing_state.get("itinerary_model"),
            "weather_model": existing_state.get("weather_model"),
            "trip_summary": existing_state.get("trip_summary", ""),
            "estimated_budget": existing_state.get("estimated_budget", ""),
            "recommendations": existing_state.get("recommendations", []),
            "followup_suggestions": existing_state.get("followup_suggestions", []),
            "plan": existing_state.get("plan"),
            "followup_history": followup_history,
            "llm_calls": 0,
            "response_type": "plan",
        }

    return initial_state(user_input)


def _format_run_result(thread_id: str, result: dict, run_llm_calls: int | None = None) -> dict:
    """Format the graph execution state into the API response dictionary."""
    final_answer = result["messages"][-1].content
    calls = run_llm_calls if run_llm_calls is not None else result.get("llm_calls", 0)

    suggestions = (
        result.get("followup_suggestions")
        or (result.get("plan") or {}).get("followup_suggestions", [])
    )

    return {
        "thread_id": thread_id,
        "response_type": result.get("response_type", "plan"),
        "answer": final_answer,
        "plan": result.get("plan"),
        "destination": result.get("destination", ""),
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "itinerary": result.get("itinerary", ""),
        "followup_suggestions": suggestions,
        "llm_calls": calls,
    }


async def arun_travel_agent(user_input: str, thread_id: str | None = None) -> dict:
    """Async entry point running graph nodes in parallel."""
    _verify_llm_configured()

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    graph = get_travel_graph()

    existing_state = None
    initial_llm_calls = 0
    try:
        existing_snapshot = await graph.aget_state(config)
        if existing_snapshot and existing_snapshot.values and existing_snapshot.values.get("user_query"):
            existing_state = existing_snapshot.values
            initial_llm_calls = existing_state.get("llm_calls", 0)
    except Exception:
        existing_state = None
        initial_llm_calls = 0

    input_data = _prepare_graph_input(user_input, existing_state)

    result = await graph.ainvoke(
        input_data,
        config=config,
    )

    run_llm_calls = max(result.get("llm_calls", 0) - initial_llm_calls, 0)
    return _format_run_result(thread_id, result, run_llm_calls=run_llm_calls)


async def astream_travel_agent(
    user_input: str,
    thread_id: str | None = None,
) -> AsyncGenerator[dict, None]:
    """Async generator yielding real-time execution events as nodes complete in LangGraph."""
    _verify_llm_configured()

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    graph = get_travel_graph()

    existing_state = None
    initial_llm_calls = 0
    try:
        existing_snapshot = await graph.aget_state(config)
        if existing_snapshot and existing_snapshot.values and existing_snapshot.values.get("user_query"):
            existing_state = existing_snapshot.values
            initial_llm_calls = existing_state.get("llm_calls", 0)
    except Exception:
        existing_state = None
        initial_llm_calls = 0

    input_data = _prepare_graph_input(user_input, existing_state)

    yield {
        "event": "start",
        "thread_id": thread_id,
    }

    async for chunk in graph.astream(input_data, config=config, stream_mode="updates"):
        for node_name, node_update in chunk.items():
            if node_name == "router_agent":
                intent = node_update.get("intent") or {}
                yield {
                    "event": "node_complete",
                    "node": "router_agent",
                    "intent_type": intent.get("intent_type", "initial_planning"),
                    "destination": node_update.get("destination", ""),
                    "origin": node_update.get("origin", ""),
                }
            elif node_name == "scout_fanout":
                yield {
                    "event": "node_complete",
                    "node": "scout_fanout",
                }
            elif node_name in ("flight_agent", "hotel_agent", "weather_agent"):
                yield {
                    "event": "node_complete",
                    "node": node_name,
                }
            elif node_name in ("itinerary_agent", "guardrail_agent", "advisor_agent"):
                yield {
                    "event": "node_complete",
                    "node": node_name,
                }

    final_snapshot = await graph.aget_state(config)
    final_values = final_snapshot.values if final_snapshot else {}
    run_llm_calls = max(final_values.get("llm_calls", 0) - initial_llm_calls, 0)
    formatted_result = _format_run_result(thread_id, final_values, run_llm_calls=run_llm_calls)

    yield {
        "event": "complete",
        "result": formatted_result,
    }


def run_travel_agent(user_input: str, thread_id: str | None = None) -> dict:
    """Synchronous convenience wrapper around arun_travel_agent."""
    return asyncio.run(arun_travel_agent(user_input, thread_id))
