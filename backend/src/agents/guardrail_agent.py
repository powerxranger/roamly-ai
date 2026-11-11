"""Guardrail Agent: handles out-of-scope and ambiguous requests with direct boundary guidance."""

from langchain_core.messages import AIMessage

from src.graph.state import TravelState


DEFAULT_OUT_OF_SCOPE_MESSAGE = (
    "I am Roamly, an AI travel planner. I specialize in building day-by-day itineraries, "
    "scouting transit and accommodations, checking local weather, and recommending places to eat and explore.\n\n"
    "I cannot assist with queries outside of travel planning, such as general coding, homework, math, or trivia.\n\n"
    "Here are a few travel requests you can try:\n"
    "- **\"Plan a 5-day trip to Tokyo & Kyoto\"**\n"
    "- **\"Weekend getaway from Delhi to Jaipur by train\"**\n"
    "- **\"What are the best street food spots in Bangkok?\"**"
)

DEFAULT_CLARIFICATION_MESSAGE = (
    "I would love to help you plan your trip! To get started, where are you thinking of going?\n\n"
    "You can provide:\n"
    "- A destination city or country (e.g. *\"5 days in Amsterdam\"*)\n"
    "- A route between two locations (e.g. *\"Travel from New York to Montreal\"*)\n"
    "- A style or travel preference (e.g. *\"A 4-day mountain getaway in Himachal Pradesh\"*)"
)


def guardrail_agent(state: TravelState) -> dict:
    """Returns a focused conversational boundary response without triggering heavy scouts."""
    intent = state.get("intent") or {}
    intent_type = intent.get("intent_type", "out_of_scope")
    custom_msg = intent.get("guardrail_message")

    if custom_msg and len(custom_msg.strip()) > 10:
        response_text = custom_msg.strip()
    elif intent_type == "clarification_needed":
        response_text = DEFAULT_CLARIFICATION_MESSAGE
    else:
        response_text = DEFAULT_OUT_OF_SCOPE_MESSAGE

    return {
        "messages": [AIMessage(content=response_text)],
        "response_type": "conversation",
    }
