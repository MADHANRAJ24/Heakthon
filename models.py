from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class Action(BaseModel):
    """
    Action sent by the agent to the environment.
    """
    command: str = Field(..., description="Action name: 'categorize', 'draft_response', 'resolve'")
    data: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the command")

class Observation(BaseModel):
    """
    Observation returned to the agent after each step.
    """
    email_content: Optional[str] = Field(None, description="Body of the customer email")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Email metadata like sender, original timestamp")
    status: str = Field(..., description="Current status of the ticket processing")
    last_action_result: Optional[str] = Field(None, description="Result of the previous action")
    available_policies: Optional[List[Dict[str, Any]]] = Field(None, description="Relevant policies for decision making")

class Reward(BaseModel):
    """
    Structured reward object for partial progress signals.
    """
    value: float = Field(..., ge=0.0, le=1.0, description="Numerical reward value")
    reasoning: str = Field(..., description="Explanation of why this reward was assigned")

class State(BaseModel):
    """
    Internal state of the environment (not directly seen by the agent).
    """
    episode_id: str
    current_step: int
    max_steps: int
    ticket_data: Dict[str, Any]
    is_done: bool
    total_reward: float
