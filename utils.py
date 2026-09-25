import os
import json
import re
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fitbuddy_fallback_secret_key_2026")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def create_admin_token(username: str) -> str:
    """Create a signed, time-stamped admin session token."""
    timestamp = str(int(time.time()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_admin_token(token: Optional[str], max_age_seconds: int = 86400) -> bool:
    """Verify signed admin session token and check expiration."""
    if not token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, timestamp_str, signature = parts
    if username != ADMIN_USERNAME:
        return False
    try:
        ts = int(timestamp_str)
        if time.time() - ts > max_age_seconds:
            return False  # Expired
    except ValueError:
        return False

    payload = f"{username}:{timestamp_str}"
    expected_sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_sig)


def safe_json_loads(data: Any, default: Optional[Dict] = None) -> Dict:
    """Safely parse JSON string or return default dictionary."""
    if default is None:
        default = {}
    if not data:
        return default
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        # Clean markdown codeblocks if present
        clean_str = data.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:]
        elif clean_str.startswith("```"):
            clean_str = clean_str[3:]
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3]
        clean_str = clean_str.strip()

        try:
            return json.loads(clean_str)
        except json.JSONDecodeError:
            # Try to extract first JSON object via regex
            match = re.search(r"(\{.*\})", clean_str, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
    return default


def sanitize_workout_plan(raw_data: Any, user_name: str = "User", goal: str = "Fitness") -> Dict[str, Any]:
    """
    Ensure the workout plan dictionary contains all required fields and days
    so the template renders reliably without KeyError or missing data.
    """
    plan = safe_json_loads(raw_data)
    
    if not isinstance(plan, dict):
        plan = {}

    plan_title = plan.get("plan_title") or f"7-Day {goal} AI Workout Plan for {user_name}"
    summary = plan.get("summary") or f"Personalized plan tailored for {user_name} targeting {goal}."
    nutrition_tip = plan.get("nutrition_tip") or "Stay hydrated with at least 2.5–3 liters of water daily, consume adequate protein per kg of bodyweight, and prioritize 7-8 hours of quality sleep for muscular recovery."
    disclaimer = plan.get("disclaimer") or "This information is for general wellness and educational purposes and is not a substitute for professional medical or nutritional advice."

    raw_days = plan.get("days", [])
    days = []

    # Map existing days or create defaults up to 7
    for day_num in range(1, 8):
        found_day = None
        if isinstance(raw_days, list):
            for d in raw_days:
                if isinstance(d, dict) and d.get("day") == day_num:
                    found_day = d
                    break
        
        if not found_day and isinstance(raw_days, list) and len(raw_days) >= day_num and isinstance(raw_days[day_num - 1], dict):
            found_day = raw_days[day_num - 1]

        if found_day and isinstance(found_day, dict):
            # Clean exercises
            raw_exercises = found_day.get("exercises", [])
            exercises = []
            if isinstance(raw_exercises, list):
                for ex in raw_exercises:
                    if isinstance(ex, dict):
                        exercises.append({
                            "name": ex.get("name", "Exercise"),
                            "sets": str(ex.get("sets", "3 sets")),
                            "reps": str(ex.get("reps", "10-12 reps")),
                            "rest": str(ex.get("rest", "60s")),
                            "notes": str(ex.get("notes", ""))
                        })
                    elif isinstance(ex, str):
                        exercises.append({
                            "name": ex,
                            "sets": "3 sets",
                            "reps": "10-12 reps",
                            "rest": "60s",
                            "notes": ""
                        })

            is_rest = bool(found_day.get("is_rest_day", day_num in [4, 7] and len(exercises) == 0))
            days.append({
                "day": day_num,
                "title": found_day.get("title", f"Day {day_num} - Workout"),
                "focus": found_day.get("focus", "Active Recovery" if is_rest else "Full Body"),
                "is_rest_day": is_rest,
                "warm_up": found_day.get("warm_up", "5-10 mins light dynamic warm-up"),
                "exercises": exercises,
                "cool_down": found_day.get("cool_down", "5 mins static stretching & hydration")
            })
        else:
            # Fallback default day
            is_rest = (day_num == 4 or day_num == 7)
            focus_title = "Active Recovery & Mobility" if is_rest else f"Day {day_num} Training"
            days.append({
                "day": day_num,
                "title": f"Day {day_num} - {focus_title}",
                "focus": "Active Recovery & Stretching" if is_rest else f"Conditioning & Strength for {goal}",
                "is_rest_day": is_rest,
                "warm_up": "5-10 mins joint circles, brisk walk or jump rope",
                "exercises": [] if is_rest else [
                    {"name": "Bodyweight Squats", "sets": "3 sets", "reps": "12-15 reps", "rest": "60s", "notes": "Keep chest up and knees tracking over toes"},
                    {"name": "Push-ups (or Incline Push-ups)", "sets": "3 sets", "reps": "8-12 reps", "rest": "60s", "notes": "Engage core, elbows at 45 degrees"},
                    {"name": "Plank Hold", "sets": "3 sets", "reps": "30-45 seconds", "rest": "45s", "notes": "Maintain neutral spine"},
                    {"name": "Walking Lunges", "sets": "3 sets", "reps": "10 reps per leg", "rest": "60s", "notes": "Step forward firmly with controlled tempo"}
                ],
                "cool_down": "5-10 mins deep breathing, hamstring and quad stretches"
            })

    return {
        "plan_title": plan_title,
        "summary": summary,
        "days": days,
        "nutrition_tip": nutrition_tip,
        "disclaimer": disclaimer
    }
