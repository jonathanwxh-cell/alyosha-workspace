# Smart Meal Automation

**Problem Solved:** Daily dinner decision fatigue with generic suggestions that don't learn

**Before:**
- Static meal suggestions
- No learning from Jon's choices
- Generic options that don't improve

**After:**
- Personalized suggestions based on past choices
- Avoids recent cuisines 
- Learns preferred dishes and patterns
- Builds confidence scores

## How It Works

1. **Learning:** Tracks Jon's meal choices from `memory/kids-meals-log.jsonl`
2. **Intelligence:** Avoids recent cuisines, prioritizes chosen ones
3. **Personalization:** Ranks dishes by past selection frequency
4. **Improvement:** Each choice improves future suggestions

## Usage

```bash
# Get smart suggestions
python3 scripts/smart-meal-recommender.py suggest

# Log a choice (to learn)
python3 scripts/smart-meal-recommender.py choose 2

# View learning stats
python3 scripts/smart-meal-recommender.py stats
```

## Integration Options

### Option 1: Replace Daily Cron
Update "Kids Dinner Ideas" cron to use smart recommender instead of generic suggestions.

### Option 2: Learning Layer
Keep current cron, add feedback mechanism that learns from reactions/choices.

### Option 3: Hybrid
Use smart recommender on weekdays, creative/experimental suggestions on weekends.

## Current Learning

From existing data (2 Japanese meals chosen):
- **Favorite cuisine:** Japanese
- **Preferred dishes:** Chicken katsu bites, Sesame spinach, Japanese rice with furikake
- **Pattern:** Recent Japanese choices → system now avoids suggesting Japanese to prevent repetition

## Next Steps

1. **Test period:** Try for 1 week, track engagement
2. **Feedback loop:** Add reaction tracking to learn from 👍/👎 
3. **Expand:** Add breakfast, lunch, or weekend activity learning
4. **Visual:** Generate meal photos/planning charts

## Files Created

- `scripts/smart-meal-recommender.py` - Core learning system
- `automations/smart-meal-automation.md` - This documentation

## Impact

**Reduces:** Daily decision fatigue, generic suggestions
**Increases:** Personalization, learning, success rate
**Time saved:** ~5 minutes daily of meal planning decisions