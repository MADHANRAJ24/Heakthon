from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import os

from models import Action, Observation, Reward
from env import SupportTriageEnv
from tasks import TASKS

app = FastAPI(title="Support Triage OpenEnv")
env = SupportTriageEnv()

# Store active episodes if multi-session or just keep it simple locally
# For HF Space demo, single session with a simple mapping is fine
sessions = {}

class ResetRequest(BaseModel):
    task_id: str = "easy"

@app.get("/")
async def health():
    return {"status": "ok", "environment": "SupportTriageEnv"}

@app.get("/tasks")
async def get_tasks():
    return TASKS

@app.post("/reset")
async def reset(req: ResetRequest):
    obs = env.reset(task_id=req.task_id)
    return {"observation": obs.model_dump(), "episode_id": env.state()["episode_id"]}

@app.post("/step")
async def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    }

@app.get("/state")
async def state():
    return env.state()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
