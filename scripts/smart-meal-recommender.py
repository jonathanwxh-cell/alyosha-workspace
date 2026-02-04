#!/usr/bin/env python3
"""
Smart Meal Recommender - Learns from Jon's choices to improve suggestions
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

class SmartMealRecommender:
    def __init__(self, log_file="memory/kids-meals-log.jsonl"):
        self.log_file = Path(log_file)
        self.preferences = self._load_preferences()
    
    def _load_preferences(self):
        """Learn preferences from historical data"""
        if not self.log_file.exists():
            return {"cuisines": {}, "dishes": {}, "patterns": {}}
        
        cuisines = Counter()
        dishes = Counter()
        patterns = {"weekday": Counter(), "avoided": []}
        
        with open(self.log_file) as f:
            for line in f:
                try:
                    meal = json.loads(line.strip())
                    if meal.get("chosen"):
                        cuisine = meal.get("cuisine", "unknown")
                        cuisines[cuisine] += 1
                        for dish in meal.get("dishes", []):
                            dishes[dish] += 1
                        
                        # Track weekday patterns
                        date_str = meal.get("date")
                        if date_str:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            patterns["weekday"][date_obj.strftime("%A")] += 1
                except:
                    continue
        
        return {
            "cuisines": dict(cuisines),
            "dishes": dict(dishes), 
            "patterns": {
                "weekday": dict(patterns["weekday"]),
                "avoided": patterns["avoided"]
            }
        }
    
    def get_smart_suggestions(self, exclude_recent_days=5):
        """Generate personalized suggestions based on preferences"""
        # Get recent meals to avoid repetition
        recent_cuisines = self._get_recent_cuisines(exclude_recent_days)
        
        # Base meal templates with kid-friendly options
        templates = {
            "japanese": {
                "protein": ["chicken katsu bites", "teriyaki salmon", "chicken teriyaki", "tamagoyaki strips"],
                "veg": ["sesame spinach", "steamed broccoli", "edamame", "corn kernels"],
                "carb": ["japanese rice with furikake", "udon noodles", "onigiri balls"]
            },
            "chinese": {
                "protein": ["sweet & sour pork", "honey garlic chicken", "mini dumplings", "egg fried tofu"],
                "veg": ["stir-fried bok choy", "steamed vegetables", "corn and carrots"],
                "carb": ["egg fried rice", "plain rice", "soft noodles"]
            },
            "western": {
                "protein": ["mini meatballs", "chicken nuggets", "fish fingers", "scrambled eggs"],
                "veg": ["steamed broccoli trees", "roasted carrots", "cucumber sticks"],
                "carb": ["mashed potatoes", "pasta", "dinner rolls"]
            },
            "korean": {
                "protein": ["beef bulgogi strips", "korean fried chicken", "egg rolls", "tofu squares"],
                "veg": ["seasoned spinach", "steamed corn", "pickled radish"],
                "carb": ["white rice", "korean rice cakes", "rice balls"]
            },
            "italian": {
                "protein": ["turkey meatballs", "grilled chicken strips", "cheese ravioli"],
                "veg": ["steamed zucchini", "roasted peppers", "green beans"],
                "carb": ["penne pasta", "garlic bread", "risotto"]
            }
        }
        
        # Prioritize cuisines Jon has chosen before, but not recently
        preferred_cuisines = self.preferences["cuisines"]
        available_cuisines = [c for c in templates.keys() if c not in recent_cuisines]
        
        # Sort by preference score
        def preference_score(cuisine):
            base_score = preferred_cuisines.get(cuisine, 0) * 2  # 2x weight for chosen cuisines
            if cuisine in recent_cuisines:
                base_score -= 5  # Penalty for recent cuisines
            return base_score + len(templates[cuisine]["protein"])  # Variety bonus
        
        sorted_cuisines = sorted(available_cuisines, key=preference_score, reverse=True)
        
        suggestions = []
        for i, cuisine in enumerate(sorted_cuisines[:3]):  # Top 3
            template = templates[cuisine]
            
            # Pick components (prioritize dishes Jon has chosen)
            def pick_best(options, category):
                dish_prefs = self.preferences["dishes"]
                return max(options, key=lambda x: dish_prefs.get(x, 0) + 1)
            
            protein = pick_best(template["protein"], "protein")
            veg = pick_best(template["veg"], "veg")
            carb = pick_best(template["carb"], "carb")
            
            suggestions.append({
                "option": i + 1,
                "theme": f"{cuisine.title()} Family Style",
                "protein": protein,
                "veg": veg,
                "carb": carb,
                "cuisine": cuisine,
                "confidence": min(100, preference_score(cuisine) * 10 + 50)
            })
        
        return suggestions
    
    def _get_recent_cuisines(self, days=5):
        """Get cuisines used in recent days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        if not self.log_file.exists():
            return recent
        
        with open(self.log_file) as f:
            for line in f:
                try:
                    meal = json.loads(line.strip())
                    date_str = meal.get("date")
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj >= cutoff and meal.get("cuisine"):
                            recent.append(meal["cuisine"])
                except:
                    continue
        
        return recent
    
    def log_choice(self, chosen_option, suggestions):
        """Log Jon's choice to improve future suggestions"""
        if not chosen_option or chosen_option > len(suggestions):
            return
        
        choice = suggestions[chosen_option - 1]
        
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "meal": choice["theme"],
            "dishes": [choice["protein"], choice["veg"], choice["carb"]],
            "cuisine": choice["cuisine"],
            "chosen": True,
            "confidence": choice["confidence"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Append to log
        os.makedirs(self.log_file.parent, exist_ok=True)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_stats(self):
        """Get learning statistics"""
        return {
            "total_choices": sum(self.preferences["cuisines"].values()),
            "favorite_cuisine": max(self.preferences["cuisines"].items(), 
                                   key=lambda x: x[1], default=("none", 0))[0],
            "favorite_dishes": sorted(self.preferences["dishes"].items(), 
                                    key=lambda x: x[1], reverse=True)[:5],
            "weekday_patterns": self.preferences["patterns"]["weekday"]
        }

def main():
    import sys
    
    recommender = SmartMealRecommender()
    
    if len(sys.argv) == 1 or sys.argv[1] == "suggest":
        suggestions = recommender.get_smart_suggestions()
        
        print("🍽️ **Smart Dinner Suggestions**")
        print("")
        for s in suggestions:
            print(f"**Option {s['option']}: {s['theme']}** (confidence: {s['confidence']}%)")
            print(f"• {s['protein']}")
            print(f"• {s['veg']}")
            print(f"• {s['carb']}")
            print("")
        
        print("📝 Reply with number (1-3) to log choice and improve future suggestions")
        
    elif sys.argv[1] == "choose" and len(sys.argv) > 2:
        try:
            choice_num = int(sys.argv[2])
            suggestions = recommender.get_smart_suggestions()
            recommender.log_choice(choice_num, suggestions)
            chosen = suggestions[choice_num - 1]
            print(f"✅ Logged choice: {chosen['theme']}")
            print("Future suggestions will learn from this preference.")
        except (ValueError, IndexError):
            print("❌ Invalid choice number")
    
    elif sys.argv[1] == "stats":
        stats = recommender.get_stats()
        print("📊 **Learning Statistics**")
        print(f"Total logged meals: {stats['total_choices']}")
        print(f"Favorite cuisine: {stats['favorite_cuisine']}")
        print(f"Top dishes: {[dish for dish, count in stats['favorite_dishes']]}")
        print(f"Weekday patterns: {stats['weekday_patterns']}")
    
    else:
        print("Usage:")
        print("  python3 smart-meal-recommender.py suggest")
        print("  python3 smart-meal-recommender.py choose <1-3>") 
        print("  python3 smart-meal-recommender.py stats")

if __name__ == "__main__":
    main()