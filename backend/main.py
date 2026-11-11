import json
import os
import traceback
import uvicorn

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from src.config.settings import (
    CORS_ORIGINS,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    has_llm_key,
)
from src.graph.runner import arun_travel_agent, astream_travel_agent


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
    stream: bool = False


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
    is_ready = has_llm_key()
    configured_providers = []
    if GEMINI_API_KEY:
        configured_providers.append("Gemini")
    if GROQ_API_KEY:
        configured_providers.append("Groq")

    return JSONResponse(
        content={
            "ready": is_ready,
            "configured_providers": configured_providers,
            "missing": [] if is_ready else ["GEMINI_API_KEY or GROQ_API_KEY"],
            "credentials": {
                "GEMINI_API_KEY": {
                    "label": "Google Gemini API key (Primary)",
                    "hint": "Primary model: gemini-3.8-flash with 1500 free requests/day.",
                    "placeholder": "AIzaSy...",
                    "configured": bool(GEMINI_API_KEY),
                    "source": "env" if GEMINI_API_KEY else None,
                },
                "GROQ_API_KEY": {
                    "label": "Groq API key (Fallback)",
                    "hint": "Fallback: open-source model fallback.",
                    "placeholder": "gsk_...",
                    "configured": bool(GROQ_API_KEY),
                    "source": "env" if GROQ_API_KEY else None,
                },
            },
        }
    )


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    is_ready = has_llm_key()
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running",
        "ready": is_ready,
        "missing": [] if is_ready else ["GEMINI_API_KEY or GROQ_API_KEY"],
    }


# =========================
# Planning
# =========================

@app.post("/api/travel/stream")
async def travel_planner_stream(request_data: TravelRequest):
    """Server-Sent Events (SSE) streaming endpoint for real-time multi-agent execution."""
    user_message = request_data.message.strip()

    if not user_message:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Message cannot be empty."
            }
        )

    async def sse_event_generator():
        try:
            async for event_payload in astream_travel_agent(
                user_input=user_message,
                thread_id=request_data.thread_id
            ):
                yield f"data: {json.dumps(event_payload)}\n\n"
        except ValueError as e:
            missing_keys = []
            if not GEMINI_API_KEY and not GROQ_API_KEY:
                missing_keys = ["GEMINI_API_KEY or GROQ_API_KEY"]
            err_dict = {
                "event": "error",
                "status_code": 428,
                "error": str(e),
                "missing": missing_keys,
            }
            yield f"data: {json.dumps(err_dict)}\n\n"
        except Exception as e:
            err_msg = str(e)
            status_code = 500
            user_friendly = err_msg
            if "rate_limit_exceeded" in err_msg or "429" in err_msg or "413" in err_msg:
                status_code = 429
                user_friendly = (
                    "AI rate limit temporarily reached. "
                    "Please wait 10-15 seconds and try again."
                )
            print("ERROR in stream:", e)
            traceback.print_exc()
            err_dict = {
                "event": "error",
                "status_code": status_code,
                "error": user_friendly,
                "raw_error": err_msg,
            }
            yield f"data: {json.dumps(err_dict)}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    if request_data.stream:
        return await travel_planner_stream(request_data)

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
                "response_type": result.get("response_type", "plan"),
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
        missing_keys = []
        if not GEMINI_API_KEY and not GROQ_API_KEY:
            missing_keys = ["GEMINI_API_KEY or GROQ_API_KEY"]
        return JSONResponse(
            status_code=428,
            content={
                "success": False,
                "error": str(e),
                "missing": missing_keys,
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
