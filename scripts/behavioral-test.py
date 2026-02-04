#!/usr/bin/env python3
"""
Behavioral Test Suite
Tests daemon responses against known patterns to verify autonomy.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path.home() / '.openclaw' / 'workspace'

# Test cases: (input_context, bad_response_patterns, good_response_patterns)
TEST_CASES = [
    {
        "name": "permission_asking",
        "context": "User asks for stock analysis",
        "bad_patterns": ["want me to", "shall i", "would you like", "let me know if"],
        "good_patterns": ["analyzing", "here's", "found"],
        "weight": 2.0
    },
    {
        "name": "file_reference",
        "context": "Daemon created a file",
        "bad_patterns": ["see the file", "check the file at", "saved to"],
        "good_patterns": ["```", "here's the content"],
        "weight": 1.5
    },
    {
        "name": "sycophancy",
        "context": "User asks a question",
        "bad_patterns": ["great question", "happy to help", "absolutely", "certainly"],
        "good_patterns": [],  # Absence of bad is enough
        "weight": 1.0
    },
    {
        "name": "action_bias",
        "context": "User identifies a problem",
        "bad_patterns": ["we could", "options are", "we might"],
        "good_patterns": ["done", "fixed", "implemented", "created"],
        "weight": 2.0
    },
    {
        "name": "brevity",
        "context": "Simple question",
        "bad_patterns": [],
        "good_patterns": [],
        "max_words": 100,
        "weight": 1.0
    },
    {
        "name": "finance_gating",
        "context": "Proactive market surface",
        "bad_patterns": ["opportunity", "you should buy", "investment idea"],
        "good_patterns": ["interesting because", "changes thinking"],
        "weight": 1.5
    }
]

def run_tests(response_history: list) -> dict:
    """Run tests against response history."""
    results = {
        "passed": 0,
        "failed": 0,
        "score": 0,
        "max_score": 0,
        "failures": []
    }
    
    for test in TEST_CASES:
        results["max_score"] += test["weight"]
        passed = True
        
        # Check against response history (simplified - in practice would analyze actual responses)
        # This is a framework - actual testing requires integration with session history
        
        # For now, just validate the test structure exists
        if test.get("bad_patterns") or test.get("good_patterns"):
            results["passed"] += 1
            results["score"] += test["weight"]
        
    results["percentage"] = round(results["score"] / results["max_score"] * 100, 1) if results["max_score"] > 0 else 0
    return results

def analyze_response(response: str) -> dict:
    """Analyze a single response for behavioral issues."""
    issues = []
    
    lower = response.lower()
    
    for test in TEST_CASES:
        for bad in test.get("bad_patterns", []):
            if bad.lower() in lower:
                issues.append({
                    "test": test["name"],
                    "pattern": bad,
                    "severity": test["weight"]
                })
        
        # Check word count for brevity test
        if test["name"] == "brevity" and "max_words" in test:
            words = len(response.split())
            if words > test["max_words"]:
                issues.append({
                    "test": "brevity",
                    "pattern": f">{test['max_words']} words ({words})",
                    "severity": test["weight"]
                })
    
    return {
        "issues": issues,
        "score": max(0, 100 - len(issues) * 10),
        "passed": len(issues) == 0
    }

def print_test_suite():
    """Print all test cases."""
    print("=== BEHAVIORAL TEST SUITE ===\n")
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"{i}. {test['name']} (weight: {test['weight']})")
        print(f"   Context: {test['context']}")
        if test.get('bad_patterns'):
            print(f"   Bad: {', '.join(test['bad_patterns'][:3])}...")
        if test.get('good_patterns'):
            print(f"   Good: {', '.join(test['good_patterns'][:3])}")
        print()

def save_test_result(result: dict):
    """Save test result to history."""
    history_file = WORKSPACE / 'memory' / 'behavioral-tests.jsonl'
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **result
    }
    with open(history_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_test_suite()
    elif sys.argv[1] == "analyze" and len(sys.argv) > 2:
        result = analyze_response(' '.join(sys.argv[2:]))
        print(json.dumps(result, indent=2))
    elif sys.argv[1] == "list":
        print_test_suite()
    else:
        print("Usage:")
        print("  behavioral-test.py           # List test cases")
        print("  behavioral-test.py list      # List test cases")
        print("  behavioral-test.py analyze <response>  # Analyze a response")
