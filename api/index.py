from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
from .agent import AgentCore
from .database import SupabaseHistory
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AgentCore - AI Agent API v2 + Playwright")
agent = AgentCore()
db = SupabaseHistory()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class AutonomyRequest(BaseModel):
    objective: str

# IMPORTANT: All these start with /api in Vercel. 
# In FastAPI, because Vercel handles the rewrite inside `vercel.json` 
# mapping /api/(.*) to api/index.py, FastAPI actually WILL receive /api/... in its root path scope.
# The standard solution when combining FastAPI + Next is to mount FastAPI at /api.

api_app = FastAPI()

@api_app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = agent.run(request.session_id, request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.post("/autonomy", response_model=ChatResponse)
async def autonomy_run(request: AutonomyRequest, background_tasks: BackgroundTasks):
    try:
        response = agent.run_autonomy(request.objective)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get("/health")
async def health():
    return {
        "status": "online",
        "agent": "AgentCore",
        "autonomy_enabled": True,
        "models": {
            "primary": "gemini-2.5-flash",
            "fallback": "llama-3.3-70b-versatile"
        }
    }

@api_app.post("/manager", response_model=ChatResponse)
async def manager_run(request: AutonomyRequest):
    try:
        from .multi_agent import MultiAgentManager
        multi_manager = MultiAgentManager()
        response = multi_manager.run_manager(request.objective, session_id="user_manager_trigger")
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get("/team")
async def get_team_status():
    try:
        from .multi_agent import MultiAgentManager
        multi_manager = MultiAgentManager()
        return {"status": "ok", "team_roles": multi_manager.get_team_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get("/cron/morning")
async def cron_morning(background_tasks: BackgroundTasks):
    from .multi_agent import MultiAgentManager
    multi_manager = MultiAgentManager()
    objective = "Busca 3 noticias de IA hoy, resume y guarda."
    background_tasks.add_task(multi_manager.run_manager, objective, "cron_morning")
    return {"status": "Cron Morning Disparado"}

@api_app.get("/cron/evening")
async def cron_evening(background_tasks: BackgroundTasks):
    from .multi_agent import MultiAgentManager
    multi_manager = MultiAgentManager()
    objective = "Resumen del día ejecutado"
    background_tasks.add_task(multi_manager.run_manager, objective, "cron_evening")
    return {"status": "Cron Evening Disparado"}

# Mount the inner app to the root app so it matches /api paths perfectly
app.mount("/api", api_app)

# Fallback direct routing in case rewrite passes root paths
@app.post("/chat", response_model=ChatResponse)
async def chat_direct(request: ChatRequest):
    return await chat(request)

@app.post("/autonomy", response_model=ChatResponse)
async def autonomy_direct(request: AutonomyRequest, background_tasks: BackgroundTasks):
    return await autonomy_run(request, background_tasks)

@app.get("/health")
async def health_direct():
    return await health()

@app.post("/manager")
async def manager_direct(request: AutonomyRequest):
    return await manager_run(request)

@app.get("/team")
async def team_direct():
    return await get_team_status()

