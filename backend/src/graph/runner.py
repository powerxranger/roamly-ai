"""Entry point the API layer calls to run one travel planning request."""

import uuid
from langchain_core.messages import HumanMessage

from src.config.settings import has_llm_key
from src.graph.graph import get_travel_graph
from src.graph.state import initial_state


def _verify_llm_configured():
    if not has_llm_key():
        raise ValueError(
            "No LLM API keys found. Please set GEMINI_API_KEY or GROQ_API_KEY in your .env file."
        )


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

    # Check if this thread already has existing state in the checkpointer
    existing_state = None
    try:
        existing_snapshot = await graph.aget_state(config)
        if existing_snapshot and existing_snapshot.values and existing_snapshot.values.get("user_query"):
            existing_state = existing_snapshot.values
    except Exception:
        existing_state = None

    if existing_state:
        # Semantic follow-up: preserve existing structured data and append to history
        followup_history = list(existing_state.get("followup_history", []))
        followup_history.append(user_input)

        input_data = {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "destination": existing_state.get("destination", ""),
            "origin": existing_state.get("origin", ""),
            "flight_results": existing_state.get("flight_results", ""),
            "hotel_results": existing_state.get("hotel_results", ""),
            "weather_results": existing_state.get("weather_results", ""),
            "itinerary": existing_state.get("itinerary", ""),
            "flight_model": existing_state.get("flight_model"),
            "hotel_model": existing_state.get("hotel_model"),
            "itinerary_model": existing_state.get("itinerary_model"),
            "weather_model": existing_state.get("weather_model"),
            "plan": existing_state.get("plan"),
            "followup_history": followup_history,
            "llm_calls": 0,
            "response_type": "plan",
        }
    else:
        # Initial travel request
        input_data = initial_state(user_input)

    result = await graph.ainvoke(
        input_data,
        config=config,
    )

    final_answer = result["messages"][-1].content

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
        "llm_calls": result.get("llm_calls", 0),
    }


def run_travel_agent(user_input: str, thread_id: str | None = None) -> dict:
    _verify_llm_configured()

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    graph = get_travel_graph()

    # Check if this thread already has existing state in the checkpointer
    existing_state = None
    try:
        existing_snapshot = graph.get_state(config)
        if existing_snapshot and existing_snapshot.values and existing_snapshot.values.get("user_query"):
            existing_state = existing_snapshot.values
    except Exception:
        existing_state = None

    if existing_state:
        # Semantic follow-up: preserve existing structured data and append to history
        followup_history = list(existing_state.get("followup_history", []))
        followup_history.append(user_input)

        input_data = {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "destination": existing_state.get("destination", ""),
            "origin": existing_state.get("origin", ""),
            "flight_results": existing_state.get("flight_results", ""),
            "hotel_results": existing_state.get("hotel_results", ""),
            "weather_results": existing_state.get("weather_results", ""),
            "itinerary": existing_state.get("itinerary", ""),
            "flight_model": existing_state.get("flight_model"),
            "hotel_model": existing_state.get("hotel_model"),
            "itinerary_model": existing_state.get("itinerary_model"),
            "weather_model": existing_state.get("weather_model"),
            "plan": existing_state.get("plan"),
            "followup_history": followup_history,
            "llm_calls": 0,
            "response_type": "plan",
        }
    else:
        # Initial travel request
        input_data = initial_state(user_input)

    result = graph.invoke(
        input_data,
        config=config,
    )

    final_answer = result["messages"][-1].content

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
        "llm_calls": result.get("llm_calls", 0),
    }


if __name__ == "__main__":
    # Run with:  python -m src.graph.runner
    user_query = (
        "I want to plan a trip to Paris in July. "
        "Can you help me find flights, hotels, and an itinerary?"
    )

    output = run_travel_agent(user_query, thread_id="test_thread_001")
    print(output["answer"])
