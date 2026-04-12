import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI

# Mock or local environment import
# For a standalone script, we import the environment logic locally or interact via API
# Given the containerized nature, the baseline script usually interacts with the environment
from env import SupportTriageEnv
from models import Action
from tasks import TaskGrader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaselineAgent:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    def get_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interacts with the LLM to determine the next action.
        """
        # Convert observation to a prompt
        prompt = f"""
        You are a Customer Support Agent. Your task is to process the following customer email.
        
        Email Content: {observation.get('email_content')}
        Metadata: {observation.get('metadata')}
        Available Policies: {observation.get('available_policies')}
        Status: {observation.get('status')}
        Last Action Result: {observation.get('last_action_result')}
        
        Available Commands:
        1. 'categorize': data={{'category': '...'}} OR data={{'categories': ['...', '...']}}
        2. 'resolve': data={{'order_id': '...', 'eligible': bool, 'reason': '...', 'draft': '...'}}
        
        Output your next action in JSON format:
        {{"command": "...", "data": {{...}}}}
        
        Strictly output valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()
            # Basic JSON extractor
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error getting action: {e}")
            return {"command": "resolve", "data": {"error": str(e)}}

def run_evaluation():
    # Load credentials
    api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")
    base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo") # Or Nemotron etc.

    agent = BaselineAgent(api_key, base_url, model_name)
    env = SupportTriageEnv()
    
    tasks = ["easy", "medium", "hard"]
    results = {}

    for task_id in tasks:
        logger.info(f"Running task: {task_id}")
        print(f"[START] task={task_id}", flush=True)
        
        obs = env.reset(task_id=task_id)
        done = False
        history = []
        step_count = 0
        
        while not done:
            step_count += 1
            
            # Prepare observation for agent (pydantic to dict)
            obs_dict = obs.model_dump()
            action_data = agent.get_action(obs_dict)
            
            # Create Action model
            action = Action(command=action_data.get("command", "resolve"), data=action_data.get("data", {}))
            
            # Step in environment
            obs, reward, done, info = env.step(action)
            
            print(f"[STEP] step={step_count} reward={float(reward.value)}", flush=True)
            
            # Track history for grading
            history.append({
                "action": action.model_dump(),
                "reward": reward.model_dump(),
                "observation": obs.model_dump()
            })
            
            if done:
                break
        
        # Grade the task based on history
        if task_id == "easy":
            score = TaskGrader.grade_easy(history)
        elif task_id == "medium":
            score = TaskGrader.grade_medium(history)
        else:
            score = TaskGrader.grade_hard(history)
            
        results[task_id] = score
        logger.info(f"Task {task_id} Score: {score}")
        print(f"[END] task={task_id} score={float(score)} steps={step_count}", flush=True)

    print("\n--- Final Assessment Scores ---")
    print(json.dumps(results, indent=2))
    
    # Save results to a file for confirmation
    with open("scores.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    run_evaluation()
