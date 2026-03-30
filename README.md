---
title: Ai Support Triage
emoji: ⚡
colorFrom: red
colorTo: green
sdk: docker
pinned: false
---

# Support Triage OpenEnv

## Overview
`support-triage-env` is a real-world OpenEnv-compliant environment designed to evaluate AI agents on customer support tasks. It simulates the triage process of incoming customer emails, requiring the agent to categorize issues, extract relevant identifiers, and make policy-based decisions.

### Why this environment?
Customer support triage is a high-impact real-world task. Accurate categorization and policy enforcement are critical for ensuring customer satisfaction and operational efficiency. This environment tests an agent's ability to:
- **Understand** unstructured text.
- **Extract** structured data (Order IDs).
- **Reason** over business policies (knowledge base).
- **Multi-task** across several customer intents.

## Environment Spec
- **Observation Space**: Typed Pydantic model including `email_content`, `metadata`, `status`, `last_action_result`, and `available_policies`.
- **Action Space**: Typed Pydantic model with commands: `categorize`, `resolve`, and custom data payloads.

## Tasks & Difficulty
| Task ID | Name | Difficulty | Description |
| :--- | :--- | :--- | :--- |
| `easy` | Refund Triage | Easy | Basic categorization and Order ID extraction for a single-intent refund request. |
| `medium` | Multi-Issue Support | Medium | Handling an email with multiple requests (Damaged Item + Address Change). |
| `hard` | Policy Eligibility | Hard | Verifying a refund request against a 14-day policy window using timestamps and logical reasoning. |

## Scoring & Rewards
- **Rewards**: Partial progress signals are provided at each state transition. A reward of `1.0` is given for complete task success.
- **Graders**: Deterministic programmatic graders evaluate the agent's history and assign a final score between `0.0` and `1.0`.

## Setup & Usage

### Local Development
1. Install dependencies:
   ```bash
   pip install fastapi pydantic uvicorn openai pyyaml
   ```
2. Run the environment server:
   ```bash
   python app.py
   ```
3. Run the baseline inference script:
   ```bash
   export OPENAI_API_KEY="your-key"
   python inference.py
   ```

### Docker
Build and run the container locally:
```bash
docker build -t support-triage-env .
docker run -p 8000:7860 support-triage-env
```

### Deployment
This environment is ready for deployment to **Hugging Face Spaces** as a container. Tag with `openenv` to be discoverable in the ecosystem.

## Baseline Scores
Calculated using `gpt-3.5-turbo` as the agent:
- **Easy**: 1.0/1.0
- **Medium**: 0.9/1.0
- **Hard**: 0.8/1.0
