# 05. Project Development & Implementation Details

## 1. Directory Structure Overview

```
FitBuddy/
│
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app initialization, middleware & static mounts
│   ├── routes.py            # Application HTTP endpoints and controllers
│   ├── database.py          # SQLAlchemy database engine and session generator
│   ├── models.py            # SQLite database entity models (User, WorkoutPlan)
│   ├── schemas.py           # Pydantic data validation and structured output schemas
│   ├── gemini_service.py    # Google GenAI / Gemini AI integration & fallback engine
│   └── utils.py             # Security tokens, JSON sanitization, and text exporters
│
├── templates/
│   ├── base.html            # Core layout with navigation, glow orbs, and footer
│   ├── index.html           # Landing page with interactive fitness form and loading overlay
│   ├── result.html          # 7-Day workout plan cards, profile summary, and action bar
│   ├── feedback.html        # Plan improvement page with quick pre-set tags
│   ├── dashboard.html       # Protected admin dashboard with KPI stats and user table
│   ├── all_users.html       # Template alias for dashboard
│   ├── login.html           # Admin portal authentication card
│   └── error.html           # Friendly error notifications and 404 handler
│
├── static/
│   ├── css/
│   │   └── style.css        # Vanilla CSS3 with dark fitness theme and glassmorphism
│   ├── js/
│   │   └── script.js        # Mobile menu, form validation, modals, and clipboard
│   └── images/
│
├── tests/
│   ├── __init__.py
│   └── test_app.py          # Automated Pytest suite covering all routes & models
│
├── docs/                    # College project documentation files
├── .env.example             # Template environment variables
├── .env                     # Local environment configuration
├── .gitignore               # Git ignore rules for Python, SQLite, and secrets
├── requirements.txt         # Production dependencies
└── README.md                # Project documentation and setup guide
```

---

## 2. Key Code Implementations

### A. Gemini Prompt Engineering (`app/gemini_service.py`)
```python
prompt = f"""
You are FitBuddy AI, an expert, certified fitness coach and sports nutritionist.
Create a personalized, scientifically sound, safe, and engaging 7-day workout and recovery plan:

User Profile:
- Name: {name}
- Age: {age} years old
- Weight: {weight} kg
- Fitness Goal: {goal}
- Workout Intensity: {intensity}

Requirements:
1. Generate an exact 7-day schedule (Day 1 through Day 7).
2. For each day specify: day, title, focus, is_rest_day, warm_up, exercises (name, sets, reps, rest, notes), and cool_down.
3. Include 1 to 2 smart rest/active recovery days strategically placed across the 7 days depending on the intensity.
4. Provide a tailored nutrition_tip with practical hydration and protein targets for {weight}kg.
5. Output strict valid JSON matching the schema.
"""
```

### B. Dual Plan Persistence Logic (`app/routes.py`)
```python
# Save initial plan
existing_plan.original_plan = plan_json_str
existing_plan.updated_plan = None
existing_plan.feedback = None
db.commit()

# When user submits feedback:
updated_dict = update_workout_plan(user_dict, original_dict, clean_feedback)
plan_record.updated_plan = json.dumps(updated_dict)
plan_record.feedback = clean_feedback
db.commit()
```

### C. Signed Admin Authentication (`app/utils.py`)
```python
def create_admin_token(username: str) -> str:
    timestamp = str(int(time.time()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"
```
