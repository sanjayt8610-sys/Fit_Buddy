# 04. Project Planning & Work Breakdown Structure (WBS)

## 1. Project Timeline & Milestones

The FitBuddy development lifecycle was structured across 6 core sprints:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase 1    │ ──► │   Phase 2    │ ──► │   Phase 3    │
│ Requirements │     │   Backend &  │     │   Gemini AI  │
│  & DB Models │     │  FastAPI Core│     │ Integration  │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase 6    │ ◄── │   Phase 5    │ ◄── │   Phase 4    │
│ Testing, Docs│     │ Admin Portal │     │  Modern UI & │
│  & Deployment│     │  & Security  │     │ Glassmorphism│
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 2. Work Breakdown Structure (WBS)

### Work Package 1: Foundation & Data Layer
* [x] Initialize Python virtual environment and dependencies (`requirements.txt`).
* [x] Configure SQLAlchemy engine and session factory (`app/database.py`).
* [x] Define `User` and `WorkoutPlan` models with foreign key constraints (`app/models.py`).
* [x] Setup environment configuration and `.env.example`.

### Work Package 2: AI Engine & Business Logic
* [x] Integrate Google GenAI SDK (`google-genai`).
* [x] Engineer Gemini prompts for 7-day structured JSON generation (`generate_workout_plan`).
* [x] Create adaptive feedback loop for routine modification (`update_workout_plan`).
* [x] Implement robust offline algorithmic fallback engine for offline development and testing.

### Work Package 3: FastAPI Routing & Controller Layer
* [x] Implement landing page (`GET /`) and plan generation (`POST /generate-workout`).
* [x] Implement result dashboard route (`GET /result/{user_id}`).
* [x] Implement feedback submission and dual-plan storage (`POST /submit-feedback`).
* [x] Implement download endpoint (`GET /api/user/{user_id}/download`) and JSON API.

### Work Package 4: Frontend & Aesthetic Design System
* [x] Build master Jinja2 layout (`templates/base.html`) with ambient background glow.
* [x] Create hero landing page with animated badges and profile form (`templates/index.html`).
* [x] Create interactive result dashboard with 7-day workout cards (`templates/result.html`).
* [x] Create feedback view with quick tags (`templates/feedback.html`).
* [x] Style with dark theme, electric lime accents, and CSS glassmorphism (`static/css/style.css`).
* [x] Implement JavaScript controllers for form validation, progress simulation, and modals (`static/js/script.js`).

### Work Package 5: Admin Cockpit & Security
* [x] Implement HMAC-SHA256 session token generation and verification (`app/utils.py`).
* [x] Create admin login route (`/admin/login`) and protected dashboard (`/view-all-users`).
* [x] Add search bar, filters (Goal, Intensity, Plan status), and deletion confirmation modal.
* [x] Build live plan inspector modal with real-time JSON API fetching.

### Work Package 6: Verification, Testing & Academic Documentation
* [x] Develop comprehensive Pytest test suite with 11 automated test cases (`tests/test_app.py`).
* [x] Generate academic project documentation (`docs/01_brainstorming.md` through `08_project_demonstration.md`).
* [x] Create detailed, beginner-friendly `README.md`.
