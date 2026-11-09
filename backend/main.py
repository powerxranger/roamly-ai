import os
import traceback
import uvicorn

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config.settings import CORS_ORIGINS, GROQ_API_KEY
from src.graph.runner import arun_travel_agent, run_travel_agent

# This is to allow nested event loops for async calls in FastAPI
import nest_asyncio
nest_asyncio.apply()


app = FastAPI(
    title="Roamly AI",
    description="Multi-Agent AI Travel Planner powered by LangGraph",
    version="1.0.0"
)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/")
async def root():
    return {
        "name": "Roamly AI API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# =========================
# Configuration / Health
# =========================

@app.get("/api/config")
async def read_config():
    """Report credential status based on .env configuration."""
    is_ready = bool(GROQ_API_KEY)
    return JSONResponse(
        content={
            "ready": is_ready,
            "missing": [] if is_ready else ["GROQ_API_KEY"],
            "credentials": {
                "GROQ_API_KEY": {
                    "label": "Groq API key",
                    "hint": "Powers every agent. Configured in .env file.",
                    "placeholder": "gsk_...",
                    "configured": is_ready,
                    "source": "env" if is_ready else None,
                }
            },
        }
    )


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    is_ready = bool(GROQ_API_KEY)
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running",
        "ready": is_ready,
        "missing": [] if is_ready else ["GROQ_API_KEY"],
    }


# =========================
# Planning
# =========================

@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        result = await arun_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
                "plan": result.get("plan"),
                "destination": result.get("destination", ""),
                "flight_results": result["flight_results"],
                "hotel_results": result["hotel_results"],
                "weather_results": result.get("weather_results", ""),
                "itinerary": result["itinerary"],
                "llm_calls": result["llm_calls"],
            }
        )

    except ValueError as e:
        return JSONResponse(
            status_code=428,
            content={
                "success": False,
                "error": str(e),
                "missing": ["GROQ_API_KEY"],
            }
        )

    except Exception as e:
        err_msg = str(e)
        status_code = 500
        user_friendly_error = err_msg

        if "rate_limit_exceeded" in err_msg or "429" in err_msg or "413" in err_msg:
            status_code = 429
            user_friendly_error = (
                "AI rate limit temporarily reached. "
                "Please wait 10-15 seconds and try again."
            )

        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": user_friendly_error,
                "raw_error": err_msg,
            }
        )


@app.head("/", include_in_schema=False)
async def home_head():
    """Hosting platforms probe with HEAD to detect an open port."""
    return Response(status_code=200)


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() in ("true", "1", "yes"),
    )
