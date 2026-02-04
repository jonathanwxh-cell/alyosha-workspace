#!/usr/bin/env python3
"""
Behavior Tree prototype for heartbeat decision logic.

Based on research into BT patterns for autonomous agents.
Goal: Replace current if/elif chains with modular, reactive architecture.

References:
- SandGarden BT guide: https://www.sandgarden.com/learn/behavior-trees
- Nordeus GP-BT paper insights
"""

import json
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List
import subprocess

class Status(Enum):
    SUCCESS = "success"
    FAILURE = "failure" 
    RUNNING = "running"

class BTNode:
    """Base behavior tree node"""
    
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children = []
    
    def tick(self, context: Dict[str, Any]) -> Status:
        """Override in subclasses"""
        raise NotImplementedError
    
    def add_child(self, child: 'BTNode'):
        child.parent = self
        self.children.append(child)
        return self

class SequenceNode(BTNode):
    """Execute children left to right until one fails"""
    
    def tick(self, context: Dict[str, Any]) -> Status:
        for child in self.children:
            result = child.tick(context)
            if result == Status.FAILURE:
                return Status.FAILURE
            elif result == Status.RUNNING:
                return Status.RUNNING
        return Status.SUCCESS

class FallbackNode(BTNode):
    """Try children left to right until one succeeds"""
    
    def tick(self, context: Dict[str, Any]) -> Status:
        for child in self.children:
            result = child.tick(context)
            if result == Status.SUCCESS:
                return Status.SUCCESS
            elif result == Status.RUNNING:
                return Status.RUNNING
        return Status.FAILURE

class ConditionNode(BTNode):
    """Evaluate a condition function"""
    
    def __init__(self, name: str, condition_func):
        super().__init__(name)
        self.condition_func = condition_func
    
    def tick(self, context: Dict[str, Any]) -> Status:
        try:
            if self.condition_func(context):
                return Status.SUCCESS
            else:
                return Status.FAILURE
        except Exception as e:
            context['debug'] = f"Condition {self.name} error: {e}"
            return Status.FAILURE

class ActionNode(BTNode):
    """Execute an action function"""
    
    def __init__(self, name: str, action_func):
        super().__init__(name)
        self.action_func = action_func
    
    def tick(self, context: Dict[str, Any]) -> Status:
        try:
            result = self.action_func(context)
            if result is True:
                return Status.SUCCESS
            elif result is False:
                return Status.FAILURE
            else:
                # Assume string result means action taken, surface message
                context['surface_message'] = result
                return Status.SUCCESS
        except Exception as e:
            context['debug'] = f"Action {self.name} error: {e}"
            return Status.FAILURE

# Condition functions
def is_urgent_alert(context):
    """Check for urgent conditions that override all else"""
    # Placeholder - would check email alerts, system alerts, etc.
    return False

def is_active_conversation(context):
    """Check if Jon replied recently"""
    # Load recent session history, check if reply within 30min
    return False  # Placeholder

def has_significant_delta(context):
    """Run delta detection to see if anything changed"""
    try:
        result = subprocess.run(['python3', 'scripts/delta-detector.py'], 
                              capture_output=True, text=True, cwd='/home/ubuntu/.openclaw/workspace')
        if result.returncode == 0:
            # Parse result - if HIGH or MEDIUM significance, return True
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'HIGH' in line or 'MEDIUM' in line:
                    context['delta_message'] = line
                    return True
        return False
    except:
        return False

def should_do_creation(context):
    """Check if it's time for creative/generative work"""
    # Check time, last creation, mood indicators
    return True  # Bias toward creation as per HEARTBEAT.md

# Action functions  
def surface_urgent_alert(context):
    """Handle urgent alert"""
    return "🚨 URGENT: System alert detected"

def return_heartbeat_ok(context):
    """Silent heartbeat ack"""
    context['result'] = 'HEARTBEAT_OK'
    return True

def surface_delta(context):
    """Surface the detected change"""
    message = context.get('delta_message', 'Something changed')
    return f"🔄 {message}"

def do_creation_work(context):
    """Perform creative/generative work"""
    return "🎨 Creating something new..."

def build_heartbeat_bt():
    """Build the heartbeat behavior tree"""
    
    # Root fallback - try high priority actions first
    root = FallbackNode("HeartbeatRoot")
    
    # Branch 1: Urgent alerts (highest priority)
    urgent_branch = SequenceNode("UrgentBranch")
    urgent_branch.add_child(ConditionNode("IsUrgent", is_urgent_alert))
    urgent_branch.add_child(ActionNode("SurfaceUrgent", surface_urgent_alert))
    
    # Branch 2: Active conversation → silent work only
    silent_branch = SequenceNode("SilentBranch") 
    silent_branch.add_child(ConditionNode("IsActiveConvo", is_active_conversation))
    silent_branch.add_child(ActionNode("ReturnOK", return_heartbeat_ok))
    
    # Branch 3: Check for changes → surface if significant
    delta_branch = SequenceNode("DeltaBranch")
    delta_branch.add_child(ConditionNode("HasDelta", has_significant_delta))
    delta_branch.add_child(ActionNode("SurfaceDelta", surface_delta))
    
    # Branch 4: Do creative work (bias toward action)
    create_branch = SequenceNode("CreateBranch")
    create_branch.add_child(ConditionNode("ShouldCreate", should_do_creation))
    create_branch.add_child(ActionNode("DoCreation", do_creation_work))
    
    # Default: HEARTBEAT_OK
    default_action = ActionNode("DefaultOK", return_heartbeat_ok)
    
    # Assemble tree
    root.add_child(urgent_branch)
    root.add_child(silent_branch)
    root.add_child(delta_branch)
    root.add_child(create_branch)
    root.add_child(default_action)
    
    return root

def main():
    """Test the behavior tree"""
    
    # Build tree
    bt = build_heartbeat_bt()
    
    # Create context
    context = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'debug_mode': True
    }
    
    # Tick the tree
    result = bt.tick(context)
    
    # Output result
    if 'surface_message' in context:
        print(context['surface_message'])
    elif 'result' in context:
        print(context['result'])
    else:
        print(f"BT Result: {result.value}")
    
    # Debug info
    if context.get('debug'):
        print(f"DEBUG: {context['debug']}")

if __name__ == "__main__":
    main()