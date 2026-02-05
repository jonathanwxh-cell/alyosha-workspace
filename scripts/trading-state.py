#!/usr/bin/env python3
"""
Trading Goal State Machine

Manages state transitions for the trading goal system.
Agents check current state to determine behavior.

Usage:
    python3 scripts/trading-state.py status          # Current state + context
    python3 scripts/trading-state.py transition <event>  # Trigger state change
    python3 scripts/trading-state.py set <key> <value>   # Update context
    python3 scripts/trading-state.py behavior <agent>    # Get agent behavior for current state
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path.home() / ".openclaw/workspace/memory/goals/trading/state.json"


def load_state():
    """Load current state."""
    if not STATE_FILE.exists():
        return None
    with open(STATE_FILE, 'r') as f:
        return json.load(f)


def save_state(state: dict):
    """Save state."""
    state['meta']['lastUpdated'] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_status():
    """Get current status summary."""
    state = load_state()
    if not state:
        return {"error": "No state file found"}
    
    current = state.get('currentState', 'UNKNOWN')
    state_def = state.get('states', {}).get(current, {})
    
    return {
        "currentState": current,
        "description": state_def.get('description', ''),
        "behaviors": state_def.get('behaviors', {}),
        "possibleTransitions": list(state_def.get('transitions', {}).keys()),
        "context": state.get('context', {}),
        "recentTransitions": state.get('recentTransitions', [])[-3:]
    }


def transition(event: str):
    """Trigger a state transition."""
    state = load_state()
    if not state:
        return {"error": "No state file found"}
    
    current = state.get('currentState', 'UNKNOWN')
    state_def = state.get('states', {}).get(current, {})
    transitions = state_def.get('transitions', {})
    
    if event not in transitions:
        return {
            "error": f"Invalid transition '{event}' from state '{current}'",
            "valid_transitions": list(transitions.keys())
        }
    
    new_state = transitions[event]
    old_state = current
    
    # Record transition
    transition_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "from": old_state,
        "to": new_state,
        "event": event
    }
    
    state['currentState'] = new_state
    if 'recentTransitions' not in state:
        state['recentTransitions'] = []
    state['recentTransitions'].append(transition_record)
    
    # Keep only last 10 transitions
    state['recentTransitions'] = state['recentTransitions'][-10:]
    
    save_state(state)
    
    return {
        "success": True,
        "transition": f"{old_state} -> {new_state}",
        "event": event,
        "newBehaviors": state['states'][new_state].get('behaviors', {})
    }


def set_context(key: str, value: str):
    """Set a context value."""
    state = load_state()
    if not state:
        return {"error": "No state file found"}
    
    # Try to parse value as JSON, otherwise use as string
    try:
        parsed_value = json.loads(value)
    except:
        # Try to parse as number
        try:
            parsed_value = float(value) if '.' in value else int(value)
        except:
            parsed_value = value
    
    if 'context' not in state:
        state['context'] = {}
    
    old_value = state['context'].get(key)
    state['context'][key] = parsed_value
    
    save_state(state)
    
    return {
        "success": True,
        "key": key,
        "oldValue": old_value,
        "newValue": parsed_value
    }


def get_behavior(agent: str):
    """Get the behavior mode for an agent in current state."""
    state = load_state()
    if not state:
        return {"error": "No state file found"}
    
    current = state.get('currentState', 'UNKNOWN')
    state_def = state.get('states', {}).get(current, {})
    behaviors = state_def.get('behaviors', {})
    
    behavior = behaviors.get(agent, 'default')
    
    return {
        "agent": agent,
        "currentState": current,
        "behavior": behavior,
        "allBehaviors": behaviors
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'status':
        result = get_status()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'transition':
        if len(sys.argv) < 3:
            print("Usage: trading-state.py transition <event>")
            status = get_status()
            print(f"Valid transitions from {status['currentState']}: {status['possibleTransitions']}")
            return
        event = sys.argv[2]
        result = transition(event)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'set':
        if len(sys.argv) < 4:
            print("Usage: trading-state.py set <key> <value>")
            return
        key = sys.argv[2]
        value = sys.argv[3]
        result = set_context(key, value)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'behavior':
        if len(sys.argv) < 3:
            print("Usage: trading-state.py behavior <agent>")
            print("Agents: opportunity_hunter, position_monitor, portfolio_manager")
            return
        agent = sys.argv[2]
        result = get_behavior(agent)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
