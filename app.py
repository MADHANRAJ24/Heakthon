from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import os

from models import Action, Observation, Reward
from env import SupportTriageEnv
from tasks import TASKS

app = FastAPI(title="Support Triage OpenEnv")

# Add CORS middleware to allow the grader to access the Space
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SupportTriageEnv()

# Store active episodes if multi-session or just keep it simple locally
sessions = {}

class ResetRequest(BaseModel):
    task_id: str = "easy"

@app.get("/")
async def health():
    return {
        "status": "running",
        "environment": "SupportTriageEnv",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/tasks", "/state"]
    }

@app.get("/tasks")
async def get_tasks():
    return TASKS

@app.post("/reset")
async def reset(req: ResetRequest):
    try:
        obs = env.reset(task_id=req.task_id)
        current_state = env.state()
        # Return both flat and nested structures for maximum compatibility
        return {
            "observation": obs.model_dump(),
            "episode_id": current_state.get("episode_id"),
            **obs.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info,
            **obs.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    return env.state()

if __name__ == "__main__":
    # HF Spaces standard port is 7860, local default is 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
