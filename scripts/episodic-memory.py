#!/usr/bin/env python3
"""
Episodic Memory system for heartbeat continuity.

Based on research: Episodic memory = short-term, task-specific memory that tracks
"what did I do last time in this context?" for better autonomous decision-making.

Key features:
1. Track action patterns by context (time, day type, recent activity)
2. Learn from outcomes (was the action successful? did Jon engage?)
3. Provide "what would I normally do?" suggestions
4. Detect when breaking from patterns might be valuable

References:
- Codeo evaluation of memory systems in AI agents
- AutoGen shared memory architecture concepts
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class EpisodicEntry:
    """Single episodic memory entry"""
    timestamp: str
    context_hash: str
    action_type: str
    action_details: str
    outcome: str  # 'success', 'neutral', 'negative'
    engagement_score: float  # 0-1, based on Jon's response
    context_features: Dict[str, Any]

class EpisodicMemory:
    """Manages episodic memory for autonomous agents"""
    
    def __init__(self, memory_file: str = "memory/episodic-heartbeat.json"):
        self.memory_file = memory_file
        self.entries: List[EpisodicEntry] = []
        self.load_memory()
    
    def load_memory(self):
        """Load episodic memory from disk"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [EpisodicEntry(**entry) for entry in data.get('entries', [])]
            except Exception as e:
                print(f"Error loading episodic memory: {e}")
                self.entries = []
        else:
            self.entries = []
    
    def save_memory(self):
        """Save episodic memory to disk"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'entry_count': len(self.entries),
            'entries': [asdict(entry) for entry in self.entries]
        }
        
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def extract_context_features(self) -> Dict[str, Any]:
        """Extract current context features for matching"""
        now = datetime.now(timezone.utc)
        
        return {
            'hour': now.hour,
            'day_of_week': now.weekday(),  # 0=Monday
            'is_weekend': now.weekday() >= 5,
            'time_slot': self._get_time_slot(now.hour),
            'recent_activity': self._get_recent_activity()
        }
    
    def _get_time_slot(self, hour: int) -> str:
        """Categorize hour into time slots"""
        if 6 <= hour < 9:
            return 'early_morning'
        elif 9 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        elif 21 <= hour < 24:
            return 'night'
        else:
            return 'late_night'
    
    def _get_recent_activity(self) -> str:
        """Check for recent activity in session"""
        # Placeholder - would check session history
        return 'normal'
    
    def create_context_hash(self, features: Dict[str, Any]) -> str:
        """Create hash for similar contexts"""
        # Use features that matter for pattern matching
        key_features = {
            'time_slot': features['time_slot'],
            'is_weekend': features['is_weekend'],
            'day_of_week': features['day_of_week']
        }
        
        hash_input = json.dumps(key_features, sort_keys=True)
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def record_action(self, action_type: str, action_details: str, outcome: str = 'neutral', engagement_score: float = 0.5):
        """Record an action taken in the current context"""
        context_features = self.extract_context_features()
        context_hash = self.create_context_hash(context_features)
        
        entry = EpisodicEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            context_hash=context_hash,
            action_type=action_type,
            action_details=action_details,
            outcome=outcome,
            engagement_score=engagement_score,
            context_features=context_features
        )
        
        self.entries.append(entry)
        
        # Keep only last 200 entries to prevent bloat
        if len(self.entries) > 200:
            self.entries = self.entries[-200:]
        
        self.save_memory()
    
    def find_similar_contexts(self, max_results: int = 10) -> List[EpisodicEntry]:
        """Find entries from similar contexts"""
        current_features = self.extract_context_features()
        current_hash = self.create_context_hash(current_features)
        
        # Find exact context matches first
        exact_matches = [e for e in self.entries if e.context_hash == current_hash]
        
        # If not enough exact matches, find similar time slots
        if len(exact_matches) < max_results:
            time_slot = current_features['time_slot']
            similar_matches = [e for e in self.entries 
                             if e.context_features.get('time_slot') == time_slot 
                             and e.context_hash != current_hash]
            
            # Combine and dedupe
            all_matches = exact_matches + similar_matches
            seen = set()
            unique_matches = []
            for match in all_matches:
                key = (match.action_type, match.action_details[:50])  # Truncate for dedup
                if key not in seen:
                    seen.add(key)
                    unique_matches.append(match)
        else:
            unique_matches = exact_matches
        
        # Sort by recency and engagement
        unique_matches.sort(key=lambda e: (e.engagement_score, e.timestamp), reverse=True)
        
        return unique_matches[:max_results]
    
    def get_pattern_suggestions(self) -> Dict[str, Any]:
        """Get suggestions based on episodic patterns"""
        similar_contexts = self.find_similar_contexts()
        
        if not similar_contexts:
            return {
                'suggestion': 'no_pattern',
                'confidence': 0.0,
                'reasoning': 'No similar contexts found in episodic memory'
            }
        
        # Analyze patterns
        action_counts = {}
        engagement_by_action = {}
        
        for entry in similar_contexts:
            action = entry.action_type
            action_counts[action] = action_counts.get(action, 0) + 1
            
            if action not in engagement_by_action:
                engagement_by_action[action] = []
            engagement_by_action[action].append(entry.engagement_score)
        
        # Find best action by engagement + frequency
        best_action = None
        best_score = 0
        
        for action, count in action_counts.items():
            avg_engagement = sum(engagement_by_action[action]) / len(engagement_by_action[action])
            # Weight: 70% engagement, 30% frequency
            score = 0.7 * avg_engagement + 0.3 * (count / len(similar_contexts))
            
            if score > best_score:
                best_score = score
                best_action = action
        
        # Get example from best action
        best_example = next((e for e in similar_contexts if e.action_type == best_action), None)
        
        return {
            'suggestion': best_action,
            'confidence': best_score,
            'reasoning': f'Based on {len(similar_contexts)} similar contexts, {best_action} had highest success',
            'example_details': best_example.action_details if best_example else None,
            'pattern_strength': len(similar_contexts)
        }
    
    def should_break_pattern(self) -> Tuple[bool, str]:
        """Determine if it's time to break from usual patterns"""
        recent_actions = self.entries[-5:] if len(self.entries) >= 5 else self.entries
        
        if len(recent_actions) < 3:
            return False, "Insufficient history"
        
        # Check for repetition
        action_types = [e.action_type for e in recent_actions]
        if len(set(action_types)) <= 2:
            return True, "Breaking repetitive pattern"
        
        # Check for low engagement
        avg_engagement = sum(e.engagement_score for e in recent_actions) / len(recent_actions)
        if avg_engagement < 0.3:
            return True, "Recent low engagement, trying something different"
        
        return False, "Pattern working well"
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about episodic memory state"""
        if not self.entries:
            return {'status': 'empty', 'entries': 0}
        
        latest = self.entries[-1]
        context_counts = {}
        
        for entry in self.entries:
            context_counts[entry.context_hash] = context_counts.get(entry.context_hash, 0) + 1
        
        return {
            'status': 'active',
            'total_entries': len(self.entries),
            'unique_contexts': len(context_counts),
            'latest_action': latest.action_type,
            'latest_timestamp': latest.timestamp,
            'avg_engagement': sum(e.engagement_score for e in self.entries) / len(self.entries)
        }

def main():
    """Test episodic memory system"""
    memory = EpisodicMemory()
    
    # Test current context
    features = memory.extract_context_features()
    print(f"Current context: {features}")
    
    # Test pattern suggestions
    suggestions = memory.get_pattern_suggestions()
    print(f"Pattern suggestions: {suggestions}")
    
    # Test break pattern logic
    should_break, reason = memory.should_break_pattern()
    print(f"Should break pattern: {should_break} - {reason}")
    
    # Debug info
    debug = memory.get_debug_info()
    print(f"Debug info: {debug}")

if __name__ == "__main__":
    main()