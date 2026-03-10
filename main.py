from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from agent import AgentCore
from database import SupabaseHistory
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AgentCore - AI Agent API")
agent = AgentCore()
db = SupabaseHistory()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = agent.run(request.session_id, request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {
        "status": "online",
        "agent": "AgentCore",
        "models": {
            "primary": "gemini-2.5-flash-preview-04-17",
            "fallback": "llama-3.3-70b-versatile"
        }
    }

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    try:
        history = db.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
