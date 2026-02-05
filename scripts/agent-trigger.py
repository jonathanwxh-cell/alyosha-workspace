#!/usr/bin/env python3
"""
Agent Trigger System

Enables agents to trigger other agents based on conditions.
Replaces fixed schedules with event-driven execution.

Usage:
    python3 scripts/agent-trigger.py trigger <agent_name> <context_json>
    python3 scripts/agent-trigger.py status
    python3 scripts/agent-trigger.py history [limit]

Agents available:
    - deep_analyst: Full analysis on a ticker
    - proposal_generator: Create trade proposal
    - position_alert: Alert on position status
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

TRIGGER_LOG = Path.home() / ".openclaw/workspace/memory/agent-triggers.jsonl"
TRIGGER_LOG.parent.mkdir(parents=True, exist_ok=True)

# Agent definitions - prompts for each triggerable agent
AGENTS = {
    "deep_analyst": {
        "description": "Full deep-dive analysis on a specific ticker",
        "prompt_template": """TRIGGERED: Deep Analyst

**Trigger Source:** {source}
**Ticker:** {ticker}
**Initial Score:** {score}/10
**Reason:** {reason}

## STEP 1: Run the Analysis Framework

Execute this command to gather all data:
```bash
python3 scripts/deep-analyst-runner.py {ticker}
```

This runs Jon's 7-dimension framework:
- Transcript tone analysis (FMP)
- Tone trends over 4 quarters
- Insider activity (Finnhub)
- Analyst sentiment (Finnhub)
- FMP fundamentals snapshot
- Valuation metrics & peers

## STEP 2: Read Additional Context

- memory/goals/trading/thesis.md (current market view)
- memory/goals/trading/goal.md (constraints)

## STEP 3: Synthesize & Score

Based on framework output, score ruthlessly:
- Transcript signals: /10
- Insider/analyst alignment: /10
- Valuation: /10
- Thesis fit: /10
- **FINAL: /10**

**DUAL-LOOP:**
- Introspection: Am I seeing what I want to see?
- Extrospection: What would a short seller say?

## STEP 4: Act on Score

If FINAL >= 8.0:
  → Write full analysis to memory/goals/trading/research-log.md
  → Use sessions_spawn to trigger proposal_generator with ticker + thesis
  → Surface summary to Jon

If FINAL < 8.0:
  → Log brief note: "{ticker} analyzed, score X, not compelling because Y"
  → Stay silent

Be ruthless. Most opportunities don't deserve 8+.""",
        "model": "anthropic/claude-sonnet-4-0",
        "timeout": 300
    },
    
    "proposal_generator": {
        "description": "Generate formal trade proposal for approval",
        "prompt_template": """TRIGGERED: Proposal Generator

**Ticker:** {ticker}
**Thesis:** {thesis}
**Analysis Score:** {score}/10

Your job: Create a formal trade proposal for Jon's approval.

**Read:**
- memory/goals/trading/research-log.md (recent analysis)
- memory/goals/trading/positions.md (current exposure)
- memory/goals/trading/goal.md (risk limits)

**Generate Proposal:**

## Trade Proposal: {ticker}

**Strategy:** [Wheel CSP / PMCC / Credit Spread / etc.]
**Direction:** [Bullish / Bearish / Neutral]

**Entry:**
- Instrument: [Stock / Option details]
- Entry price: $X
- Position size: $X (Y% of portfolio)

**Exit:**
- Target: $X (+Z%)
- Stop: $X (-Z%)
- Time limit: [Expiry / X weeks]

**Risk/Reward:**
- Max loss: $X (Y% of portfolio)
- Max gain: $X
- R:R ratio: X:1

**Thesis (1 paragraph):**
[Why this trade, why now]

**What would invalidate:**
[Specific conditions that mean exit]

---
👍 = Approve | 👎 = Reject | Reply with questions

**Send to Jon immediately.**
**Log to memory/goals/trading/proposals.md**""",
        "model": "anthropic/claude-sonnet-4-0",
        "timeout": 180
    },
    
    "position_alert": {
        "description": "Alert on position hitting trigger levels",
        "prompt_template": """TRIGGERED: Position Alert

**Position:** {ticker}
**Alert Type:** {alert_type}
**Current Price:** ${current_price}
**Trigger Level:** ${trigger_level}

**Action Required:**
{action_required}

**Context:**
- Entry: ${entry_price}
- Current P/L: {pnl}%
- Days held: {days_held}

Send alert to Jon immediately with recommended action.""",
        "model": "anthropic/claude-sonnet-4-0",
        "timeout": 60
    }
}


def log_trigger(agent: str, context: dict, status: str = "triggered"):
    """Log a trigger event."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "context": context,
        "status": status
    }
    with open(TRIGGER_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    return entry


def trigger_agent(agent_name: str, context: dict):
    """
    Trigger an agent with context.
    Returns the command to execute (for the calling agent to run).
    """
    if agent_name not in AGENTS:
        return {"error": f"Unknown agent: {agent_name}", "available": list(AGENTS.keys())}
    
    agent = AGENTS[agent_name]
    
    # Format the prompt with context
    try:
        prompt = agent["prompt_template"].format(**context)
    except KeyError as e:
        return {"error": f"Missing context field: {e}"}
    
    # Log the trigger
    log_trigger(agent_name, context)
    
    # Return spawn command for sessions_spawn
    return {
        "status": "ready",
        "agent": agent_name,
        "task": prompt,
        "model": agent.get("model", "anthropic/claude-sonnet-4-0"),
        "timeout": agent.get("timeout", 300),
        "spawn_command": f"sessions_spawn with task=<prompt>, model={agent.get('model')}"
    }


def get_status():
    """Get trigger system status."""
    if not TRIGGER_LOG.exists():
        return {"total_triggers": 0, "agents": list(AGENTS.keys())}
    
    triggers = []
    with open(TRIGGER_LOG, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    triggers.append(json.loads(line))
                except:
                    pass
    
    # Count by agent
    by_agent = {}
    for t in triggers:
        agent = t.get('agent', 'unknown')
        by_agent[agent] = by_agent.get(agent, 0) + 1
    
    # Recent triggers
    recent = triggers[-5:] if triggers else []
    
    return {
        "total_triggers": len(triggers),
        "by_agent": by_agent,
        "recent": recent,
        "available_agents": list(AGENTS.keys())
    }


def get_history(limit: int = 10):
    """Get trigger history."""
    if not TRIGGER_LOG.exists():
        return []
    
    triggers = []
    with open(TRIGGER_LOG, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    triggers.append(json.loads(line))
                except:
                    pass
    
    return triggers[-limit:]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'trigger':
        if len(sys.argv) < 4:
            print("Usage: agent-trigger.py trigger <agent_name> '<context_json>'")
            print(f"Available agents: {list(AGENTS.keys())}")
            return
        
        agent_name = sys.argv[2]
        try:
            context = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            print("Error: context must be valid JSON")
            return
        
        result = trigger_agent(agent_name, context)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'status':
        result = get_status()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'history':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        history = get_history(limit)
        for h in history:
            ts = h.get('timestamp', '')[:19]
            agent = h.get('agent', '?')
            ctx = json.dumps(h.get('context', {}))[:60]
            print(f"[{ts}] {agent}: {ctx}...")
    
    elif cmd == 'agents':
        for name, config in AGENTS.items():
            print(f"\n{name}:")
            print(f"  {config['description']}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
