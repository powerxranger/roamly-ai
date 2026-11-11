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
    user_query = (state.get("user_query") or "").lower()

    if custom_msg and len(custom_msg.strip()) > 10:
        response_text = custom_msg.strip()
    elif intent_type == "clarification_needed":
        if "europe" in user_query:
            response_text = (
                "Europe has dozens of distinct travel corridors! To build the best itinerary for you:\n\n"
                "1. **How many days do you have?** (e.g. 7 days vs 2 weeks)\n"
                "2. **Which corridor appeals most to you?**\n"
                "   - **Classic Capitals**: London, Paris, and Amsterdam (7 to 10 days)\n"
                "   - **Mediterranean Sun**: Rome, Florence, and Amalfi Coast (8 to 10 days)\n"
                "   - **Central Europe**: Vienna, Prague, and Budapest (7 days)\n\n"
                "Reply with your preferred corridor or duration, and I will build your complete plan."
            )
        elif "southeast asia" in user_query or "asia" in user_query:
            response_text = (
                "Asia has incredible diversity! To build the right trip plan for you:\n\n"
                "1. **How many days are you planning for?**\n"
                "2. **Which region or style do you prefer?**\n"
                "   - **Thailand & Vietnam**: Bangkok, Chiang Mai, and Hanoi for food and culture\n"
                "   - **Japan Golden Route**: Tokyo, Kyoto, and Osaka for bullet trains and heritage\n"
                "   - **Island Leisure**: Bali or Phuket for beaches and relaxation\n\n"
                "Tell me which route or vibe you prefer, and I will map out the complete journey."
            )
        else:
            response_text = DEFAULT_CLARIFICATION_MESSAGE
    else:
        response_text = DEFAULT_OUT_OF_SCOPE_MESSAGE

    return {
        "messages": [AIMessage(content=response_text)],
        "response_type": "conversation",
    }
