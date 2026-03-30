from typing import Dict, Any, List
import json

class TaskGrader:
    """
    Programmatic evaluator for the tasks.
    Returns a score between 0.0 and 1.0.
    """
    def __init__(self):
        # Specific patterns to look for in action history
        pass

    @staticmethod
    def grade_easy(history: List[Dict[str, Any]]) -> float:
        """
        Grades Task 1 (Easy): Categorize and extract Order ID.
        """
        score = 0.0
        categorized = False
        extracted_order = False
        
        for step in history:
            action = step.get("action", {})
            cmd = action.get("command", "").lower()
            data = action.get("data", {})
            
            if cmd == "categorize" and data.get("category") == "Refund Request":
                score += 0.3
                categorized = True
            if cmd == "resolve" and data.get("order_id") == "ORD-9872":
                score += 0.7
                extracted_order = True
        
        return min(1.0, score) if (categorized and extracted_order) else (0.3 if categorized else 0.0)

    @staticmethod
    def grade_medium(history: List[Dict[str, Any]]) -> float:
        """
        Grades Task 2 (Medium): Multi-issue and draft response.
        """
        score = 0.0
        categories_found = []
        order_found = False
        
        for step in history:
            action = step.get("action", {})
            cmd = action.get("command", "").lower()
            data = action.get("data", {})
            
            if cmd == "categorize":
                cats = data.get("categories", [])
                if "Damaged Item" in cats: score += 0.2
                if "Address Change" in cats: score += 0.2
            
            if cmd == "resolve":
                if data.get("order_id") == "ORD-1234":
                    score += 0.3
                if data.get("draft") and "shipping address" in data.get("draft").lower():
                    score += 0.3
        
        return min(1.0, score)

    @staticmethod
    def grade_hard(history: List[Dict[str, Any]]) -> float:
        """
        Grades Task 3 (Hard): Policy check and eligibility calculation.
        """
        score = 0.0
        policy_checked = False
        
        for step in history:
            action = step.get("action", {})
            cmd = action.get("command", "").lower()
            data = action.get("data", {})
            
            # The agent might have a 'read_policy' action or just think about it
            if cmd == "resolve":
                # Must determine ineligible correctly
                if data.get("eligible") is False:
                    score += 0.5
                    # Reasoning check
                    reason = str(data.get("reason", "")).lower()
                    if "14" in reason or "window" in reason or "exceeded" in reason:
                        score += 0.5
        
        return score

# Task definitions for OpenEnv metadata
TASKS = [
    {
        "id": "easy",
        "name": "Refund Request Triage",
        "description": "Categorize email and extract the order ID for a simple refund request.",
        "difficulty": "easy"
    },
    {
        "id": "medium",
        "name": "Multi-Issue Support",
        "description": "Handle an email with both a damaged item issue and an address change request.",
        "difficulty": "medium"
    },
    {
        "id": "hard",
        "name": "Policy Eligibility",
        "description": "Evaluate a refund request against a 14-day policy window and provide a reasoned decision.",
        "difficulty": "hard"
    }
]
