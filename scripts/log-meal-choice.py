#!/usr/bin/env python3
"""
Quick meal choice logger - called when Jon replies with a number to meal suggestions
"""

import sys
import subprocess
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 log-meal-choice.py <1-3>")
        sys.exit(1)
    
    try:
        choice = int(sys.argv[1])
        if choice not in [1, 2, 3]:
            print("Choice must be 1, 2, or 3")
            sys.exit(1)
        
        # Call the main recommender script with choose command
        script_dir = os.path.dirname(__file__)
        recommender_path = os.path.join(script_dir, 'smart-meal-recommender.py')
        
        result = subprocess.run([
            'python3', recommender_path, 'choose', str(choice)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            sys.exit(1)
            
    except ValueError:
        print("Choice must be a number")
        sys.exit(1)

if __name__ == "__main__":
    main()