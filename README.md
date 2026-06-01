# fleet-analysis-agent

# Fleet Intelligence Agent

An agentic AI system built on the Claude API that monitors fleet performance and delivers plain-English operational briefings — automatically.

Built to demonstrate production-grade LLM API usage: prompt engineering, context window management, token economics, and tool-use patterns.

---

## What it does

An operations manager can ask:

> "Check vehicle V-103 on route R-7"

And the agent:
1. Calls the anomaly detection model (Isolation Forest) to get a risk score
2. Calls the delay forecasting model to get route probability
3. Decides whether to fire a Slack alert based on thresholds
4. Returns a structured plain-English briefing — no dashboard, no manual report

```
SITUATION: Vehicle V-103 shows anomaly score 0.9 with 73% delay probability on route R-7.
RISK LEVEL: HIGH
RECOMMENDED ACTION: Pre-position backup vehicle at depot nearest R-7 checkpoint 3.
ALERT SENT: YES
```

---

## Architecture

```
User query
    │
    ▼
context.py — trim history, estimate tokens, log cost
    │
    ▼
Claude API (claude-sonnet-4-6)
    │
    ├── calls get_anomaly_scores()   → Isolation Forest model output
    ├── calls forecast_delay()       → scikit-learn delay probability
    └── calls send_slack_alert()     → ops channel notification
    │
    ▼
Structured briefing → returned to user
```

The agent loop runs until `stop_reason == "end_turn"` — Claude decides when it has enough information to answer, not the code.

---

## Project structure

```
fleet-agent/
├── agent.py        # main agent loop — tool-use orchestration
├── tools.py        # tool definitions (schema) + execution functions
├── prompts.py      # system prompt, few-shot examples (not inline)
├── context.py      # history trimming, token estimation, cost logging
├── requirements.txt
├── .env.example
└── README.md
```

---

## Design decisions

**Prompts are a separate file, not inline strings**
`prompts.py` holds the system prompt and few-shot examples. Prompts are engineering artifacts — they should be versioned, reviewed, and changed deliberately, not scattered through business logic.

**Context window is actively managed**
`context.py` trims conversation history to the last 5 turns before every API call. Unbounded history growth is the most common cause of silent cost blowup and context overflow in production LLM systems.

**Token cost is logged on every call**
Every API response logs input tokens, output tokens, and estimated cost. You cannot optimise what you do not measure. This also makes it immediately obvious if a prompt change causes unexpected token usage.

**Tool definitions are separated from execution**
`TOOLS` (the JSON schema Claude sees) and `execute_tool()` (the actual function call) are in the same file but clearly separated. The schema is what the LLM reasons about; the execution is what your infrastructure runs. Keeping them together but distinct makes both easier to test independently.

**Few-shot examples show the reasoning chain**
The example in `prompts.py` shows Claude calling both tools before forming an answer — not just the final output format. This teaches the model the correct reasoning sequence, not just the correct output shape.

**Mock data makes the demo runnable without infrastructure**
`execute_tool()` returns hardcoded scores for known vehicle and route IDs. Swap these one function at a time with real model calls when connecting to actual infrastructure — the agent loop does not change.

---

## Setup

```bash
# 1. Clone and create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env
# Edit .env and add your Anthropic API key

# 4. Export key to environment
export ANTHROPIC_API_KEY=your_key_here

# 5. Run
python agent.py
```

---

## Example queries to try

```
Check vehicle V-103 on route R-7       ← triggers HIGH alert
Check vehicle V-101 on route R-5       ← LOW risk, no alert
How is the fleet looking overall?      ← multi-vehicle reasoning
What happened with V-104?              ← uses conversation history
```

---

## How it would work in production

| Component | Demo (current) | Production |
|---|---|---|
| `get_anomaly_scores()` | hardcoded dict | call live Isolation Forest endpoint |
| `forecast_delay()` | hardcoded dict | call scikit-learn model service |
| `send_slack_alert()` | print to console | POST to Slack webhook API |
| Scheduling | manual query | cron job or Airflow DAG every 15 min |
| History storage | in-memory list | Redis or database per session |
| Auth | env var | secrets manager (AWS SSM / GCP Secret Manager) |

---

## Origin

This project reimagines the fleet performance and logistics delay forecasting work done at JUNA Technologies. The ML models (Isolation Forest for anomaly detection, scikit-learn for delay forecasting) represent the existing prediction layer. The agent wraps that layer so operational insights reach the team in plain English, automatically — eliminating the manual report preparation that was the primary bottleneck.

---

## Requirements

- Python 3.10+
- Anthropic API key (get one at console.anthropic.com)
- See `requirements.txt` for full dependency list
