#!/usr/bin/env python3
"""
Weekend Activity Scout for Singapore
Finds kid-friendly activities based on weather and events.
Target: 3yo and 5yo kids.

Usage: python3 scripts/weekend-scout.py [--json]
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Singapore kid-friendly venues (indoor/outdoor categorized)
VENUES = {
    "indoor": [
        {"name": "KidsSTOP", "ages": "2-8", "notes": "Science centre for kids, hands-on exhibits"},
        {"name": "Amazonia", "ages": "1-12", "notes": "Indoor playground at Great World"},
        {"name": "Kiztopia", "ages": "1-12", "notes": "Large indoor playground, multiple locations"},
        {"name": "Art Science Museum", "ages": "3+", "notes": "Interactive digital exhibitions"},
        {"name": "S.E.A. Aquarium", "ages": "all", "notes": "Marine life, air-conditioned"},
        {"name": "Singapore Science Centre", "ages": "3+", "notes": "Interactive science exhibits"},
        {"name": "National Gallery", "ages": "3+", "notes": "Kids programs, Keppel Centre for Art Education"},
        {"name": "Changi Jewel", "ages": "all", "notes": "Rain Vortex, playground, air-con mall"},
    ],
    "outdoor": [
        {"name": "Gardens by the Bay", "ages": "all", "notes": "Children's Garden with water play"},
        {"name": "Singapore Zoo", "ages": "all", "notes": "Rainforest zoo, splash zone"},
        {"name": "Bird Paradise", "ages": "all", "notes": "New bird park, interactive feeding"},
        {"name": "East Coast Park", "ages": "all", "notes": "Beach, cycling, playgrounds"},
        {"name": "West Coast Park", "ages": "2-6", "notes": "Great playground for toddlers"},
        {"name": "Jurong Lake Gardens", "ages": "all", "notes": "Nature playgarden, free entry"},
        {"name": "Bishan-Ang Mo Kio Park", "ages": "all", "notes": "River playground, natural play"},
        {"name": "Coney Island", "ages": "3+", "notes": "Nature trails, beaches, cycling"},
    ]
}

# Special events file (manually maintained or scraped)
EVENTS_FILE = Path(__file__).parent.parent / "memory" / "sg-events.json"

def get_weather_forecast():
    """Get Singapore weekend weather (simplified)."""
    # Use wttr.in for quick forecast
    try:
        result = subprocess.run(
            ["curl", "-s", "wttr.in/Singapore?format=%C+%t+%p&1"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "Unknown"

def check_rain_likelihood():
    """Check if rain is likely this weekend."""
    try:
        result = subprocess.run(
            ["curl", "-s", "wttr.in/Singapore?format=j1"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Check next 2 days
            rain_likely = False
            for day in data.get("weather", [])[:2]:
                for hour in day.get("hourly", []):
                    chance = int(hour.get("chanceofrain", 0))
                    if chance > 60:
                        rain_likely = True
                        break
            return rain_likely
    except:
        pass
    return None  # Unknown

def load_special_events():
    """Load special events if file exists."""
    if EVENTS_FILE.exists():
        try:
            with open(EVENTS_FILE) as f:
                events = json.load(f)
            # Filter to this weekend
            today = datetime.now()
            saturday = today + timedelta(days=(5 - today.weekday()) % 7)
            sunday = saturday + timedelta(days=1)
            weekend_events = []
            for e in events:
                event_date = datetime.fromisoformat(e.get("date", "2000-01-01"))
                if saturday.date() <= event_date.date() <= sunday.date():
                    weekend_events.append(e)
            return weekend_events
        except:
            pass
    return []

def recommend_activities(rain_likely: bool = False, special_events: list = None):
    """Generate activity recommendations."""
    recommendations = []
    
    # Add special events first
    if special_events:
        for event in special_events[:2]:
            recommendations.append({
                "name": event.get("name", "Special Event"),
                "type": "event",
                "reason": event.get("notes", "Limited time event"),
                "ages": event.get("ages", "all"),
            })
    
    # Weather-based venue suggestions
    if rain_likely:
        # Prioritize indoor
        venues = VENUES["indoor"][:4]
        weather_note = "Rain likely - indoor options prioritized"
    else:
        # Mix of outdoor (morning) + indoor (afternoon backup)
        venues = VENUES["outdoor"][:2] + VENUES["indoor"][:1]
        weather_note = "Good weather expected - outdoor morning recommended"
    
    for v in venues:
        if len(recommendations) >= 3:
            break
        recommendations.append({
            "name": v["name"],
            "type": "outdoor" if v in VENUES["outdoor"] else "indoor",
            "reason": v["notes"],
            "ages": v["ages"],
        })
    
    return recommendations, weather_note

def format_output(recommendations, weather_note, weather_raw, as_json=False):
    """Format recommendations for output."""
    if as_json:
        return json.dumps({
            "weather": weather_raw,
            "weather_note": weather_note,
            "recommendations": recommendations,
            "generated": datetime.now().isoformat(),
        }, indent=2)
    
    lines = ["🎯 **Weekend Activity Scout**", ""]
    lines.append(f"**Weather:** {weather_raw}")
    lines.append(f"*{weather_note}*")
    lines.append("")
    lines.append("**Suggestions for this weekend:**")
    
    for i, rec in enumerate(recommendations, 1):
        emoji = "🎪" if rec["type"] == "event" else ("🏠" if rec["type"] == "indoor" else "🌳")
        lines.append(f"{i}. {emoji} **{rec['name']}** (ages {rec['ages']})")
        lines.append(f"   {rec['reason']}")
    
    lines.append("")
    lines.append("*Adjust based on nap schedules and energy levels.*")
    
    return "\n".join(lines)

def main():
    as_json = "--json" in sys.argv
    
    # Get weather
    weather_raw = get_weather_forecast()
    rain_likely = check_rain_likelihood()
    
    # Load events
    special_events = load_special_events()
    
    # Generate recommendations
    recommendations, weather_note = recommend_activities(
        rain_likely=rain_likely or False,
        special_events=special_events
    )
    
    # Output
    output = format_output(recommendations, weather_note, weather_raw, as_json)
    print(output)

if __name__ == "__main__":
    main()
