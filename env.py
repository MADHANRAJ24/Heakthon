import uuid
import datetime
from typing import Tuple, Dict, Any, List
from models import Action, Observation, Reward, State

class SupportTriageEnv:
    """
    OpenEnv environment for customer support ticket triage and resolution.
    Tasks range from basic categorization to complex policy-driven decision making.
    """
    def __init__(self):
        self._state: State = None
        self._tasks: Dict[str, Dict[str, Any]] = {
            "easy": {
                "email": "Dear Support, I am writing about order #ORD-9872. I'd like a refund as it hasn't arrived.",
                "metadata": {"sender": "customer@example.com"},
                "solution": {"category": "Refund Request", "order_id": "ORD-9872"},
                "max_steps": 2
            },
            "medium": {
                "email": "Hello, my item arrived shattered, order #ORD-1234. I'm so disappointed! "
                         "By the way, I also want to update my shipping address to 5th Ave, NY.",
                "metadata": {"sender": "angry_customer@gmail.com"},
                "solution": {
                    "categories": ["Damaged Item", "Address Change"],
                    "order_id": "ORD-1234",
                    "requires_draft": True
                },
                "max_steps": 3
            },
            "hard": {
                "email": "I want a refund for #ORD-5555. I bought it on 2024-03-01. It's now 2024-03-30.",
                "metadata": {"sender": "policy_tester@test.com", "current_date": "2024-03-30"},
                "policies": [
                    {
                        "policy_name": "Standard Refund Policy",
                        "rule": "Refunds only within 14 days of purchase.",
                        "logic": {"max_days": 14}
                    }
                ],
                "solution": {"eligible": False, "reason": "Exceeded 14-day refund window."},
                "max_steps": 5
            }
        }

    def reset(self, task_id: str = "easy") -> Observation:
        """
        Resets the environment for a specific task.
        """
        if task_id not in self._tasks:
            task_id = "easy"
        
        task_info = self._tasks[task_id]
        self._state = State(
            episode_id=str(uuid.uuid4()),
            current_step=0,
            max_steps=task_info["max_steps"],
            ticket_data=task_info,
            is_done=False,
            total_reward=0.0
        )
        
        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Advances the environment state based on the agent's action.
        """
        if self._state.is_done:
            return self._get_observation(), Reward(value=0.0, reasoning="Episode already complete"), True, {}

        self._state.current_step += 1
        reward_val, reasoning, terminal = self._process_action(action)
        
        self._state.total_reward += reward_val
        self._state.is_done = terminal or (self._state.current_step >= self._state.max_steps)
        
        obs = self._get_observation(last_result=reasoning)
        reward = Reward(value=reward_val, reasoning=reasoning)
        
        return obs, reward, self._state.is_done, {"total_reward": self._state.total_reward}

    def state(self) -> Dict[str, Any]:
        """
        Returns the full hidden state of the environment.
        """
        if not self._state:
            return {}
        return self._state.model_dump()

    def _get_observation(self, last_result: str = None) -> Observation:
        """
        Constructs the observation for the agent.
        """
        task_data = self._state.ticket_data
        policies = task_data.get("policies", [])
        
        return Observation(
            email_content=task_data["email"],
            metadata=task_data["metadata"],
            status="OPEN" if not self._state.is_done else "CLOSED",
            last_action_result=last_result,
            available_policies=policies if policies else None
        )

    def _process_action(self, action: Action) -> Tuple[float, str, bool]:
        """
        Internal logic to evaluate actions and return (reward_value, reasoning, terminal).
        """
        cmd = action.command.lower()
        data = action.data
        task_id = "easy" # Default for simplistic logic or we could store task_id in state
        # Better: we can inspect state.ticket_data to determine task type
        
        # Determine current "task mode" from ticket_data
        email = self._state.ticket_data["email"]
        
        if cmd == "categorize":
            # Basic reward for correct categorization
            if "ORD-9872" in email and data.get("category") == "Refund Request":
                return 0.5, "Correct categorization of Task 1.", False
            elif "shattered" in email and "Damaged Item" in str(data.get("categories")):
                return 0.4, "Correct multi-categorization part 1.", False
            return 0.1, f"Categorization attempted: {data.get('category') or data.get('categories')}", False

        if cmd == "resolve":
            # Check Task-specific success
            if "ORD-9872" in email: # Task 1
                if data.get("order_id") == "ORD-9872":
                    return 0.5, "Task 1 completed successfully with correct Order ID.", True
            
            if "ORD-5555" in email: # Task 3 (Hard)
                eligible = data.get("eligible")
                if eligible is False:
                    # Check reason (fuzzy or exact)
                    if "14" in str(data.get("reason")).lower():
                        return 1.0, "Task 3 completed! Correct policy application.", True
                return 0.0, "Incorrect resolution for Task 3 policy check.", True

            return 0.2, "Ticket resolved, but potential errors in data extraction.", True

        return 0.0, f"Unrecognized command: {cmd}", False
