import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from models import ChatRequest, ChatResponse
from agent import run_agent, stream_agent
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Intelligent flight search agent powered by Claude API, LangChain and RAG",
    version=settings.app_version
)

# CORS — allows frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running ✈️"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Standard chat endpoint — returns full response.
    Use for simple integrations that don't need streaming.
    """
    try:
        result = run_agent(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(
            reply=result["reply"],
            session_id=result["session_id"],
            tools_used=result["tools_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming endpoint — streams response token by token.
    Use for chat interfaces where response appears in real time.
    """
    async def event_generator():
        try:
            async for token in stream_agent(
                message=request.message,
                session_id=request.session_id
            ):
                yield {
                    "event": "message",
                    "data": token
                }
            yield {
                "event": "done",
                "data": "[DONE]"
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

