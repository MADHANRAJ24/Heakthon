from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
import json
import logging

from models import Action, Observation, Reward
from env import SupportTriageEnv
from tasks import TASKS

# Configure logging to see what's happening in the Space
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openenv")

app = FastAPI(title="Support Triage OpenEnv")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to log requests for diagnostics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

env = SupportTriageEnv()

class ResetRequest(BaseModel):
    task_id: str = "easy"

@app.get("/")
async def health():
    return {
        "status": "running",
        "environment": "SupportTriageEnv",
        "endpoints": ["/reset", "/step", "/tasks", "/state"]
    }

@app.get("/tasks")
async def get_tasks():
    return TASKS

# Handle both GET and POST for /reset to be ultra-compatible
@app.api_route("/reset", methods=["GET", "POST"])
async def reset(request: Request):
    try:
        # Determine task_id from JSON body, query params, or default
        task_id = request.query_params.get("task_id", "easy")
        
        if request.method == "POST":
            # Safely attempt to parse JSON if provided
            try:
                body = await request.json()
                if isinstance(body, dict):
                    task_id = body.get("task_id", body.get("task", task_id))
            except Exception:
                pass # Default to easy or query param
        
        obs = env.reset(task_id=task_id)
        current_state = env.state()
        
        # Strictly standard OpenEnv reset response, no extra top-level fields
        resp = {
            "observation": obs.model_dump(),
            "info": {
                "message": "Environment reset successfully",
                "episode_id": current_state.get("episode_id"),
                "task_id": task_id
            }
        }
        logger.info(f"Reset successful for task: {task_id}")
        return resp
    except Exception as e:
        logger.error(f"Reset failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
        # Move reasoning to info to keep reward as a pure float (standard OpenEnv)
        info["reasoning"] = reward.reasoning
        
        # Move episode_id to info to keep the top-level standard
        info["episode_id"] = env.state().get("episode_id")
        
        return {
            "observation": obs.model_dump(),
            "reward": float(reward.value),
            "done": bool(done),
            "info": info
        }
    except Exception as e:
        logger.error(f"Step failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    return env.state()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
