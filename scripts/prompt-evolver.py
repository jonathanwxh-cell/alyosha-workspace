#!/usr/bin/env python3
"""
Prompt Evolver - Self-Improving Exploration Prompts

Implements intrinsic metacognitive learning for the daemon:
1. Metacognitive Knowledge: Track which prompts led to engagement
2. Metacognitive Planning: Generate new prompts based on successful patterns
3. Metacognitive Evaluation: Disable consistently failing prompts

Based on:
- Reflexion (Shinn 2023): Verbal reinforcement learning
- ICML 2025 Position Paper: Intrinsic metacognitive learning
- Self-Evolving Agents (OpenAI Cookbook): Feedback → Meta-prompting → Evaluation

Usage:
    python3 scripts/prompt-evolver.py analyze          # Analyze prompt performance
    python3 scripts/prompt-evolver.py evolve           # Generate evolved prompts
    python3 scripts/prompt-evolver.py prune            # Disable failing prompts
    python3 scripts/prompt-evolver.py status           # Show evolution status
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

FEEDBACK_LOG = Path.home() / '.openclaw/workspace/memory/feedback-log.jsonl'
REFLECTIONS = Path.home() / '.openclaw/workspace/memory/reflections.jsonl'
EVOLUTION_STATE = Path.home() / '.openclaw/workspace/memory/prompt-evolution.json'
EVOLVED_PROMPTS = Path.home() / '.openclaw/workspace/memory/evolved-prompts.json'

def load_feedback():
    """Load feedback log entries."""
    entries = []
    if FEEDBACK_LOG.exists():
        with open(FEEDBACK_LOG) as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    return entries

def load_reflections():
    """Load reflection entries."""
    entries = []
    if REFLECTIONS.exists():
        with open(REFLECTIONS) as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    return entries

def load_evolution_state():
    """Load or initialize evolution state."""
    if EVOLUTION_STATE.exists():
        with open(EVOLUTION_STATE) as f:
            return json.load(f)
    return {
        "version": 1,
        "created": datetime.now(timezone.utc).isoformat(),
        "prompt_performance": {},
        "successful_patterns": [],
        "disabled_prompts": [],
        "evolution_history": []
    }

def save_evolution_state(state):
    """Save evolution state."""
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(EVOLUTION_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def analyze_prompt_performance():
    """
    Metacognitive Knowledge: Analyze which prompts/categories perform well.
    
    Returns performance metrics per category and identifies patterns.
    """
    feedback = load_feedback()
    reflections = load_reflections()
    
    # Track outcomes by category
    category_stats = defaultdict(lambda: {
        "surfaces": 0,
        "engaged": 0,
        "positive": 0,
        "negative": 0,
        "topics": []
    })
    
    # Process feedback log
    recent_surfaces = []
    for entry in feedback:
        if entry.get('type') == 'surface':
            cat = entry.get('category', 'unknown')
            category_stats[cat]['surfaces'] += 1
            category_stats[cat]['topics'].append(entry.get('topic', ''))
            recent_surfaces.append({
                'ts': entry.get('ts') or entry.get('timestamp'),
                'category': cat,
                'topic': entry.get('topic', ''),
                'engaged': False
            })
        elif entry.get('type') in ('reply', 'reaction'):
            # Mark recent surface as engaged
            for s in reversed(recent_surfaces):
                if not s['engaged']:
                    s['engaged'] = True
                    category_stats[s['category']]['engaged'] += 1
                    if entry.get('sentiment') == 'positive' or entry.get('type') == 'reaction':
                        category_stats[s['category']]['positive'] += 1
                    break
        elif entry.get('type') == 'negative':
            for s in reversed(recent_surfaces):
                if not s.get('negative_marked'):
                    s['negative_marked'] = True
                    category_stats[s['category']]['negative'] += 1
                    break
    
    # Process reflections for outcome patterns
    outcome_patterns = defaultdict(list)
    for r in reflections:
        outcome = r.get('outcome', 'unknown')
        task = r.get('task', '')
        lesson = r.get('lesson', '')
        if lesson:
            outcome_patterns[outcome].append({
                'task': task[:50],
                'lesson': lesson[:100]
            })
    
    # Calculate engagement rates
    performance = {}
    for cat, stats in category_stats.items():
        if stats['surfaces'] > 0:
            engagement_rate = stats['engaged'] / stats['surfaces']
            positive_rate = stats['positive'] / stats['surfaces'] if stats['surfaces'] > 0 else 0
            negative_rate = stats['negative'] / stats['surfaces'] if stats['surfaces'] > 0 else 0
            
            performance[cat] = {
                'surfaces': stats['surfaces'],
                'engagement_rate': round(engagement_rate, 2),
                'positive_rate': round(positive_rate, 2),
                'negative_rate': round(negative_rate, 2),
                'score': round(engagement_rate + positive_rate - negative_rate * 2, 2),
                'sample_topics': stats['topics'][-3:]
            }
    
    # Identify successful patterns
    successful_patterns = []
    for cat, perf in performance.items():
        if perf['engagement_rate'] >= 0.5 and perf['surfaces'] >= 2:
            successful_patterns.append({
                'category': cat,
                'engagement_rate': perf['engagement_rate'],
                'topics': perf['sample_topics']
            })
    
    # Identify failing patterns
    failing_patterns = []
    for cat, perf in performance.items():
        if perf['engagement_rate'] < 0.2 and perf['surfaces'] >= 3:
            failing_patterns.append({
                'category': cat,
                'engagement_rate': perf['engagement_rate'],
                'surfaces': perf['surfaces']
            })
    
    return {
        'performance': performance,
        'successful_patterns': successful_patterns,
        'failing_patterns': failing_patterns,
        'outcome_lessons': {
            'success': outcome_patterns.get('success', [])[-5:],
            'partial': outcome_patterns.get('partial', [])[-3:],
            'failure': outcome_patterns.get('failure', [])[-3:]
        },
        'total_surfaces': sum(p['surfaces'] for p in performance.values()),
        'avg_engagement': round(
            sum(p['engagement_rate'] * p['surfaces'] for p in performance.values()) / 
            max(sum(p['surfaces'] for p in performance.values()), 1), 2
        )
    }

def generate_evolved_prompts(analysis):
    """
    Metacognitive Planning: Generate new prompt variations based on successful patterns.
    
    This is the self-modification step - the daemon creates new exploration directions
    based on what has worked.
    """
    evolved = []
    
    # Learn from successful categories
    for pattern in analysis.get('successful_patterns', []):
        cat = pattern['category']
        topics = pattern['topics']
        
        if cat == 'creative' and topics:
            # Creative worked - generate variation
            evolved.append({
                'type': 'variation',
                'parent_category': cat,
                'new_prompt': f"CREATIVE EXPANSION: Take a recent insight and express it in a new medium. "
                             f"Recent successful topics: {', '.join(topics[:2])}. "
                             f"Try: visual metaphor, micro-fiction, or conceptual diagram.",
                'rationale': f"Creative category had {pattern['engagement_rate']:.0%} engagement"
            })
        
        if cat == 'synthesis' and topics:
            evolved.append({
                'type': 'variation', 
                'parent_category': cat,
                'new_prompt': f"CROSS-DOMAIN SYNTHESIS: Find unexpected connection between domains. "
                             f"Successful pattern: {topics[0] if topics else 'cross-field bridges'}. "
                             f"Aim for non-obvious insight that neither field alone provides.",
                'rationale': f"Synthesis category performed well ({pattern['engagement_rate']:.0%})"
            })
        
        if cat in ('geopolitics', 'tail_risks'):
            evolved.append({
                'type': 'variation',
                'parent_category': cat,
                'new_prompt': f"RISK CASCADE ANALYSIS: Pick a current tension and trace 3rd-order effects. "
                             f"Who loses from apparent good news? Who wins from apparent bad news? "
                             f"Apply Talebian fragility lens.",
                'rationale': f"Risk-focused content ({cat}) shows engagement"
            })
    
    # Learn from successful reflection lessons
    for lesson in analysis.get('outcome_lessons', {}).get('success', []):
        if 'deep' in lesson.get('lesson', '').lower() or 'analysis' in lesson.get('lesson', '').lower():
            evolved.append({
                'type': 'lesson_derived',
                'lesson_source': lesson['lesson'][:50],
                'new_prompt': "DEEP ANALYSIS MODE: Pick ONE topic. Spend 20 minutes going deep. "
                             "Read primary sources. Extract non-obvious insight. "
                             "Success = genuine understanding, not surface summary.",
                'rationale': "Deep analysis appears in successful task reflections"
            })
            break
    
    # Learn from failures - generate OPPOSITE approaches
    for pattern in analysis.get('failing_patterns', []):
        cat = pattern['category']
        evolved.append({
            'type': 'anti_pattern',
            'failing_category': cat,
            'adjustment': f"REDUCE frequency of {cat} prompts. "
                         f"Only surface if genuinely novel (not routine check). "
                         f"Engagement rate was {pattern['engagement_rate']:.0%} over {pattern['surfaces']} surfaces.",
            'rationale': f"Low engagement suggests overuse or poor timing"
        })
    
    return evolved

def evaluate_and_prune(analysis, state):
    """
    Metacognitive Evaluation: Disable consistently failing prompt patterns.
    
    This implements the self-correction aspect - stopping behaviors that don't work.
    """
    pruned = []
    
    for pattern in analysis.get('failing_patterns', []):
        cat = pattern['category']
        # Only prune if we have enough data and it's consistently bad
        if pattern['surfaces'] >= 5 and pattern['engagement_rate'] < 0.15:
            if cat not in state.get('disabled_prompts', []):
                pruned.append({
                    'category': cat,
                    'reason': f"Engagement {pattern['engagement_rate']:.0%} over {pattern['surfaces']} surfaces",
                    'action': 'reduce_weight',  # Don't fully disable, just reduce
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
    
    return pruned

def show_status():
    """Show current evolution status."""
    state = load_evolution_state()
    analysis = analyze_prompt_performance()
    
    print("=" * 60)
    print("🧬 PROMPT EVOLUTION STATUS")
    print("=" * 60)
    
    print(f"\n📊 Overall: {analysis['total_surfaces']} surfaces, "
          f"{analysis['avg_engagement']:.0%} avg engagement")
    
    print("\n✅ HIGH PERFORMERS (evolve these):")
    for p in analysis['successful_patterns'][:5]:
        print(f"   {p['category']}: {p['engagement_rate']:.0%} engagement")
    
    print("\n⚠️  LOW PERFORMERS (reduce these):")
    for p in analysis['failing_patterns'][:5]:
        print(f"   {p['category']}: {p['engagement_rate']:.0%} over {p['surfaces']} surfaces")
    
    print("\n📈 Category Performance:")
    for cat, perf in sorted(analysis['performance'].items(), 
                           key=lambda x: -x[1]['score'])[:8]:
        bar = "█" * int(perf['engagement_rate'] * 10)
        print(f"   {cat:20} {bar:10} {perf['engagement_rate']:.0%} ({perf['surfaces']} surfaces)")
    
    if state.get('evolution_history'):
        print(f"\n🔄 Evolution History: {len(state['evolution_history'])} iterations")
        last = state['evolution_history'][-1]
        print(f"   Last: {last.get('timestamp', 'unknown')[:10]}")
    
    return analysis

def main():
    if len(sys.argv) < 2:
        print("Usage: prompt-evolver.py [analyze|evolve|prune|status]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'analyze':
        analysis = analyze_prompt_performance()
        print(json.dumps(analysis, indent=2))
    
    elif cmd == 'evolve':
        analysis = analyze_prompt_performance()
        state = load_evolution_state()
        
        evolved = generate_evolved_prompts(analysis)
        
        # Record evolution
        state['evolution_history'].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'prompts_generated': len(evolved),
            'based_on_surfaces': analysis['total_surfaces']
        })
        state['successful_patterns'] = analysis['successful_patterns']
        
        save_evolution_state(state)
        
        # Save evolved prompts
        with open(EVOLVED_PROMPTS, 'w') as f:
            json.dump({
                'generated': datetime.now(timezone.utc).isoformat(),
                'prompts': evolved
            }, f, indent=2)
        
        print(f"🧬 Generated {len(evolved)} evolved prompts")
        for e in evolved:
            print(f"\n[{e['type']}] {e.get('parent_category', e.get('failing_category', 'general'))}")
            if 'new_prompt' in e:
                print(f"   {e['new_prompt'][:80]}...")
            if 'adjustment' in e:
                print(f"   {e['adjustment'][:80]}...")
            print(f"   Rationale: {e['rationale']}")
    
    elif cmd == 'prune':
        analysis = analyze_prompt_performance()
        state = load_evolution_state()
        
        pruned = evaluate_and_prune(analysis, state)
        
        if pruned:
            state['disabled_prompts'].extend([p['category'] for p in pruned])
            save_evolution_state(state)
            
            print(f"✂️  Pruned {len(pruned)} underperforming patterns:")
            for p in pruned:
                print(f"   {p['category']}: {p['reason']}")
        else:
            print("No patterns meet pruning threshold (need 5+ surfaces, <15% engagement)")
    
    elif cmd == 'status':
        show_status()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == '__main__':
    main()
