#!/usr/bin/env python3
"""
Exploration Engine - Tree of Thoughts + Intrinsic Curiosity
============================================================

Implements branching exploration with novelty scoring.
Based on: ToT (Yao 2023), ICM (Pathak 2017), Plan-and-Execute (LangChain)

Usage:
    python3 exploration-engine.py branch "topic"    # Generate exploration branches
    python3 exploration-engine.py evaluate          # Score recent explorations
    python3 exploration-engine.py novelty "topic"   # Check topic novelty
    python3 exploration-engine.py suggest           # Get best exploration for now
    python3 exploration-engine.py status            # Show exploration state
"""

import json
import sys
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path.home() / '.openclaw/workspace'
EXPLORATION_STATE = WORKSPACE / 'memory/exploration-state.json'
TOPIC_GRAPH = WORKSPACE / 'memory/topic-graph.json'
REFLECTIONS = WORKSPACE / 'memory/reflections.jsonl'
DAILY_LOGS = WORKSPACE / 'memory'

# Exploration templates for different modes
BRANCH_TEMPLATES = {
    'depth': "Go deeper on {topic}: What's the underlying mechanism? What are experts debating?",
    'breadth': "Connect {topic} to adjacent fields: What parallel exists in biology/physics/economics?",
    'contrarian': "Challenge {topic}: What's the strongest counter-argument? What if consensus is wrong?",
    'temporal': "Project {topic} forward: How does this evolve in 1/5/10 years? What are the second-order effects?",
    'practical': "Apply {topic}: What's the actionable insight? How would Jon use this?",
    'surprise': "Find surprise in {topic}: What's the most counter-intuitive finding? What would shock people?",
}

# Novelty weights
NOVELTY_FACTORS = {
    'never_explored': 1.0,      # Topic never seen
    'not_recent': 0.7,          # Not explored in 7 days
    'low_success': 0.5,         # Previous attempts had low engagement
    'recently_explored': 0.2,   # Explored in last 3 days
    'over_explored': 0.1,       # Explored >3 times recently
}


def load_json(path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_recent_topics(days=7):
    """Get topics explored in recent days from daily logs."""
    topics = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for log_file in DAILY_LOGS.glob('202*.md'):
        try:
            date_str = log_file.stem  # e.g., "2026-02-04"
            log_date = datetime.strptime(date_str, '%Y-%m-%d')
            if log_date > cutoff:
                content = log_file.read_text().lower()
                # Extract likely topics (simple heuristic)
                for keyword in ['research', 'explore', 'analysis', 'deep dive', 'study']:
                    if keyword in content:
                        # Get surrounding context
                        topics.append(log_file.stem)
        except:
            continue
    return topics


def get_topic_history():
    """Get exploration history from state file."""
    state = load_json(EXPLORATION_STATE, {'explored': {}, 'branches': []})
    return state.get('explored', {})


def calculate_novelty(topic):
    """Calculate novelty score for a topic (0-1)."""
    topic_lower = topic.lower()
    history = get_topic_history()
    
    # Check if topic or related terms were explored
    related_found = False
    last_explored = None
    explore_count = 0
    
    for explored_topic, data in history.items():
        if topic_lower in explored_topic.lower() or explored_topic.lower() in topic_lower:
            related_found = True
            explore_count += data.get('count', 1)
            ts = data.get('last_explored')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    if last_explored is None or dt > last_explored:
                        last_explored = dt
                except:
                    pass
    
    if not related_found:
        return NOVELTY_FACTORS['never_explored']
    
    if last_explored:
        days_ago = (datetime.now(timezone.utc) - last_explored).days
        if days_ago > 7:
            return NOVELTY_FACTORS['not_recent']
        elif days_ago <= 3:
            if explore_count > 3:
                return NOVELTY_FACTORS['over_explored']
            return NOVELTY_FACTORS['recently_explored']
    
    return 0.5  # Default middle ground


def generate_branches(topic, n=3):
    """Generate N exploration branches for a topic using ToT approach."""
    # Select diverse branch types
    branch_types = random.sample(list(BRANCH_TEMPLATES.keys()), min(n, len(BRANCH_TEMPLATES)))
    
    branches = []
    for i, branch_type in enumerate(branch_types):
        template = BRANCH_TEMPLATES[branch_type]
        prompt = template.format(topic=topic)
        
        # Calculate branch score
        novelty = calculate_novelty(f"{topic} {branch_type}")
        
        # Heuristic scoring (in real implementation, would use LLM)
        type_weights = {
            'surprise': 0.9,     # High value - unexpected findings
            'contrarian': 0.85,  # High value - challenges assumptions
            'depth': 0.7,        # Good - builds understanding
            'breadth': 0.75,     # Good - finds connections
            'temporal': 0.6,     # Medium - speculation
            'practical': 0.8,    # High - actionable
        }
        
        base_score = type_weights.get(branch_type, 0.5)
        final_score = (novelty * 0.4) + (base_score * 0.6)
        
        branches.append({
            'id': i + 1,
            'type': branch_type,
            'prompt': prompt,
            'novelty': round(novelty, 2),
            'base_score': round(base_score, 2),
            'final_score': round(final_score, 2),
        })
    
    # Sort by final score
    branches.sort(key=lambda x: -x['final_score'])
    
    return branches


def record_exploration(topic, branch_type, outcome='started'):
    """Record an exploration attempt."""
    state = load_json(EXPLORATION_STATE, {'explored': {}, 'branches': []})
    
    key = f"{topic.lower()}:{branch_type}"
    if key not in state['explored']:
        state['explored'][key] = {'count': 0, 'outcomes': []}
    
    state['explored'][key]['count'] += 1
    state['explored'][key]['last_explored'] = datetime.now(timezone.utc).isoformat()
    state['explored'][key]['outcomes'].append({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'outcome': outcome
    })
    
    # Keep last 10 branches
    state['branches'] = state.get('branches', [])[-9:] + [{
        'topic': topic,
        'type': branch_type,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }]
    
    save_json(EXPLORATION_STATE, state)


def suggest_exploration():
    """Suggest the best exploration for right now."""
    # Get seed topics from various sources
    topic_graph = load_json(TOPIC_GRAPH, {})
    
    # Seed topics with weights
    seeds = [
        ('consciousness', 0.9),
        ('AI architectures', 0.8),
        ('geopolitical risk', 0.8),
        ('cross-domain patterns', 0.85),
        ('emerging science', 0.7),
        ('philosophy of mind', 0.75),
        ('tail risks', 0.8),
    ]
    
    # Add high-engagement topics from graph
    if 'topics' in topic_graph:
        for topic, data in topic_graph.get('topics', {}).items():
            engagement = data.get('engagement', 0.5)
            if engagement > 0.7:
                seeds.append((topic, engagement))
    
    # Score each seed by novelty
    scored_seeds = []
    for topic, base_weight in seeds:
        novelty = calculate_novelty(topic)
        score = novelty * 0.5 + base_weight * 0.5
        scored_seeds.append((topic, score, novelty))
    
    # Sort and pick top
    scored_seeds.sort(key=lambda x: -x[1])
    
    if not scored_seeds:
        return None, []
    
    best_topic = scored_seeds[0][0]
    branches = generate_branches(best_topic)
    
    return best_topic, branches


def show_status():
    """Show exploration engine status."""
    state = load_json(EXPLORATION_STATE, {'explored': {}, 'branches': []})
    
    print("🔭 Exploration Engine Status\n")
    print("=" * 50)
    
    # Recent branches
    recent = state.get('branches', [])[-5:]
    if recent:
        print("\n📊 Recent Explorations:")
        for b in reversed(recent):
            ts = b.get('timestamp', '')[:10]
            print(f"   [{ts}] {b.get('topic')} ({b.get('type')})")
    
    # Exploration counts by type
    type_counts = Counter()
    for key, data in state.get('explored', {}).items():
        if ':' in key:
            _, branch_type = key.rsplit(':', 1)
            type_counts[branch_type] += data.get('count', 1)
    
    if type_counts:
        print("\n📈 Exploration Types:")
        for t, count in type_counts.most_common():
            print(f"   {t}: {count}")
    
    # Novelty check on common topics
    print("\n🆕 Novelty Scores (sample):")
    for topic in ['NVIDIA', 'consciousness', 'geopolitics', 'AI safety', 'Singapore']:
        novelty = calculate_novelty(topic)
        bar = "█" * int(novelty * 10)
        print(f"   {topic:15} {bar:10} {novelty:.1f}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'branch' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        branches = generate_branches(topic)
        
        print(f"🌳 Tree of Thoughts: Branches for '{topic}'\n")
        print("=" * 50)
        
        for b in branches:
            emoji = "⭐" if b['final_score'] > 0.7 else "📍"
            print(f"\n{emoji} Branch {b['id']}: {b['type'].upper()}")
            print(f"   Prompt: {b['prompt']}")
            print(f"   Novelty: {b['novelty']:.1f} | Base: {b['base_score']:.1f} | Final: {b['final_score']:.1f}")
        
        if branches:
            best = branches[0]
            print(f"\n✅ RECOMMENDED: Branch {best['id']} ({best['type']})")
            print(f"   → {best['prompt']}")
    
    elif cmd == 'novelty' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        novelty = calculate_novelty(topic)
        
        level = "🆕 HIGH" if novelty > 0.7 else "🔄 MEDIUM" if novelty > 0.4 else "⏪ LOW"
        print(f"Novelty for '{topic}': {novelty:.2f} ({level})")
    
    elif cmd == 'suggest':
        topic, branches = suggest_exploration()
        
        if topic:
            print(f"💡 Suggested Exploration: {topic}\n")
            print("Branches (ranked by promise):")
            for b in branches[:3]:
                print(f"   {b['id']}. [{b['type']}] {b['prompt'][:60]}... ({b['final_score']:.2f})")
        else:
            print("No suggestions available")
    
    elif cmd == 'record' and len(sys.argv) >= 4:
        topic = sys.argv[2]
        branch_type = sys.argv[3]
        outcome = sys.argv[4] if len(sys.argv) > 4 else 'completed'
        record_exploration(topic, branch_type, outcome)
        print(f"✅ Recorded: {topic} ({branch_type}) → {outcome}")
    
    elif cmd == 'status':
        show_status()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
