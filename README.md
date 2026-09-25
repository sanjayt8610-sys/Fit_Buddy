# FitBuddy – AI Fitness Plan Generator 🏋️‍♂️✨

> **Your AI-Powered Fitness Companion** — Generate personalized 7-day workout plans, custom nutrition & recovery blueprints, and adapt your routine in real-time with Google Gemini AI.

---

## 1. Project Title
**FitBuddy – AI Fitness Plan Generator**

-----------------------------------------------------

## 2. Project Description
**FitBuddy** is a full-stack AI-driven web application built with **FastAPI**, **Jinja2**, **SQLite (SQLAlchemy ORM)**, and **Google Gemini AI**. It collects athlete fitness parameters (age, weight, goal, and workout intensity) and formulates an exact, structured **7-day workout routine**, tailored **nutrition & hydration strategies**, and a dynamic **two-way feedback modification engine**.

-----------------------------------------------------

## 3. Problem Statement
Most fitness seekers rely on generic, static workout templates or expensive personal coaching. Static templates do not account for individual physiological differences, equipment availability, or fatigue levels. When adjustments are needed (e.g. recovering from joint pain or needing home workouts), standard apps fail to adapt. FitBuddy bridges this gap by leveraging Google Gemini AI to provide accessible, adaptive, and scientifically structured fitness intelligence.

-----------------------------------------------------

## 4. Objectives
* Collect and validate athlete profile metrics safely and accurately.
* Generate a structured 7-day schedule with focus areas, warm-ups, exercises, set/rep ranges, rest intervals, and cool-downs.
* Formulate personalized nutrition and recovery targets (daily protein calculation, hydration, and sleep hygiene).
* Provide an interactive feedback loop to regenerate routines based on user preferences while preserving original baselines.
* Store all athlete records and workout plans in an ACID-compliant relational SQLite database.
* Deliver a secure admin portal with analytics, search/filter tools, and modal plan inspectors.
* Ensure a sleek, dark-themed, mobile-responsive UI with glassmorphism aesthetics.

-----------------------------------------------------

## 5. Features
* 📅 **Structured 7-Day AI Routines:** Day 1 through Day 7 schedules with warm-ups, exercises, sets, reps, rest periods, and cool-downs.
* 🥗 **Targeted Nutrition & Hydration:** Goal-specific daily protein (per kg of bodyweight), hydration volume, and sleep hygiene.
* 🔄 **Adaptive AI Feedback Engine:** Submit feedback (e.g., "Add more cardio", "I prefer home dumbbells only") to instantly regenerate an updated routine.
* 💾 **Dual-Plan SQLite Storage:** Preserves both the original and modified workout editions in separate database columns.
* 🛡️ **Zero Client-Side API Key Exposure:** All Gemini AI calls execute exclusively on the server backend.
* ⚡ **Resilient Offline Fallback Engine:** Guarantees zero downtime during presentations and offline evaluation.
* 📊 **Protected Admin Dashboard:** Real-time metrics (Total Users, Plans, Modified Plans, Goal Ratios), search/filter toolbar, and delete confirmation modals.
* 👁️ **Live Plan Inspector Modal:** Inspect athlete plans and feedback directly in the admin dashboard.
* 🖨️ **Print & Download Support:** Clean `@media print` layout and 1-click `.txt` plan exports.
* 📱 **100% Mobile Responsive:** Fluid Grid/Flexbox layouts with animated hamburger navigation.

-----------------------------------------------------

## 6. Technology Stack

### Frontend
* **HTML5 & Jinja2 Templates** (Semantic HTML5, template inheritance)
* **Vanilla CSS3** (Custom design system, Dark mode, Electric Lime accents `#00e676`, Glassmorphism, CSS Grid, Flexbox)
* **Vanilla ES6 JavaScript** (Form validation, progress simulation, modals, clipboard copying)
* *No React, No Bootstrap, No Tailwind*

### Backend
* **Python 3.11**
* **FastAPI** (Asynchronous web framework)
* **Uvicorn** (Lightning-fast ASGI server)
* **Pydantic v2** (Strict data validation and sanitization)

### Artificial Intelligence
* **Google Gemini AI** (via modern `google-genai` SDK)
* Configurable model routing (default `gemini-2.5-flash` / `gemini-3.8-flash`)

### Database & Security
* **SQLite 3** & **SQLAlchemy 2.0 ORM** (Relational data persistence)
* **HMAC-SHA256** Cryptographically signed admin session cookies

-----------------------------------------------------

## 7. System Architecture

```
User Browser (HTML5 / Modern CSS3 / ES6 JS)
                    │
                    ▼
          FastAPI ASGI Server
          ├── Pydantic Input Validation
          ├── HMAC-SHA256 Admin Authentication
          ├── Gemini AI Service (google-genai SDK)
          └── SQLAlchemy ORM Layer
                    │
                    ▼
             SQLite Database (fitness.db)
             ├── users Table
             └── workout_plans Table (original_plan & updated_plan)
```

-----------------------------------------------------

## 8. Project Structure

```
FitBuddy/
│
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app instance, static mount, lifespan & error handlers
│   ├── routes.py            # API & presentation routes (Home, Generate, Result, Feedback, Admin)
│   ├── database.py          # SQLAlchemy engine, session maker, and DB initializer
│   ├── models.py            # Database tables (User, WorkoutPlan)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── gemini_service.py    # Google Gemini AI integration and fallback engine
│   └── utils.py             # Security tokens, JSON sanitization, and text exporters
│
├── templates/
│   ├── base.html            # Core layout with glassmorphism navbar and ambient glow
│   ├── index.html           # Landing page with interactive fitness form and loading overlay
│   ├── result.html          # 7-Day workout plan cards, profile summary, and action bar
│   ├── feedback.html        # Plan improvement page with quick suggestion tags
│   ├── dashboard.html       # Protected admin dashboard with KPI stats and user table
│   ├── all_users.html       # Dashboard template alias
│   ├── login.html           # Admin portal authentication card
│   └── error.html           # User-friendly error notifications
│
├── static/
│   ├── css/
│   │   └── style.css        # Modern stylesheet (Dark mode, glassmorphism, responsive grid)
│   └── js/
│       └── script.js        # Mobile navigation, validation, modals, and clipboard controller
│
├── tests/
│   ├── __init__.py
│   └── test_app.py          # 11 Automated unit and integration tests (Pytest)
│
├── docs/                    # College project documentation files
│   ├── 01_brainstorming.md
│   ├── 02_requirement_analysis.md
│   ├── 03_project_design.md
│   ├── 04_project_planning.md
│   ├── 05_project_development.md
│   ├── 06_project_testing.md
│   ├── 07_project_documentation.md
│   └── 08_project_demonstration.md
│
├── .env.example             # Example environment variables
├── .env                     # Local environment configuration
├── .gitignore               # Git ignore rules for Python, SQLite, and secrets
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

-----------------------------------------------------

## 9. Installation Steps

Clone the repository or open the project folder:
```bash
git clone https://github.com/your-username/fitbuddy.git
cd fitbuddy
```

-----------------------------------------------------

## 10. Virtual Environment Setup

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

-----------------------------------------------------

## 11. Environment Variable Setup

Copy `.env.example` to create your `.env` file:
```bash
cp .env.example .env
```

Contents of `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
DATABASE_URL=sqlite:///./fitness.db
SECRET_KEY=fitbuddy_dev_secret_key_987654321
```

-----------------------------------------------------

## 12. Gemini API Setup
1. Visit [Google AI Studio](https://aistudio.google.com/) and generate a free Gemini API Key.
2. Paste the key into your `.env` file for `GOOGLE_API_KEY`.
3. *Note:* If no key is configured, FitBuddy automatically engages its intelligent offline fallback engine, ensuring the app remains fully functional for testing and demonstration.

-----------------------------------------------------

## 13. Database Setup
The SQLite database (`fitness.db`) is automatically initialized when the FastAPI application starts. No manual SQL migrations or database setup commands are required.

-----------------------------------------------------

## 14. How to Run

Start the development server with Uvicorn:
```bash
uvicorn app.main:app --reload
```

Open your browser and navigate to:
* **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Admin Dashboard:** [http://127.0.0.1:8000/admin/login](http://127.0.0.1:8000/admin/login)
* **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative API Documentation (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

-----------------------------------------------------

## 15. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders Home page and user profile input form |
| `POST` | `/generate-workout` | Validates profile, invokes Gemini AI, saves plan, redirects |
| `GET` | `/result/{user_id}` | Renders 7-day workout plan, nutrition advice, and actions |
| `GET` | `/feedback/{user_id}` | Renders interactive plan refinement form |
| `POST` | `/submit-feedback` | Regenerates plan with feedback and stores updated edition |
| `GET` | `/api/user/{user_id}/download` | Exports plan as a downloadable plain-text file |
| `GET` | `/api/user/{user_id}/json` | Returns structured JSON representation of the plan |
| `GET` | `/admin/login` | Renders Admin authentication page |
| `POST` | `/admin/login` | Validates credentials and sets signed cookie |
| `GET` | `/admin/logout` | Clears admin session cookie |
| `GET` | `/view-all-users` | Protected Admin dashboard with user analytics and table |
| `POST` | `/admin/delete-user/{user_id}` | Admin endpoint to delete user and cascade plan |

-----------------------------------------------------

## 16. Screenshots Section

| Screen | Description |
| :--- | :--- |
| **Landing Page** | `[ Screenshot Placeholder: FitBuddy Landing Page & Hero ]` |
| **Fitness Profile Form** | `[ Screenshot Placeholder: User Profile Form with Validation ]` |
| **Animated Loading Overlay** | `[ Screenshot Placeholder: AI Loading Screen with Dumbbell Animation ]` |
| **7-Day Workout Dashboard** | `[ Screenshot Placeholder: Generated 7-Day Workout Cards ]` |
| **Nutrition & Recovery Tip** | `[ Screenshot Placeholder: AI Nutrition & Hydration Highlight Card ]` |
| **Feedback Adjustment Page** | `[ Screenshot Placeholder: Plan Modification View with Quick Tags ]` |
| **Admin Analytics Portal** | `[ Screenshot Placeholder: Admin Dashboard with KPIs & Filterable Table ]` |
| **Admin Plan Inspector Modal** | `[ Screenshot Placeholder: Live Plan Inspector Modal Dialog ]` |

---

## 17. Testing

FitBuddy includes a comprehensive automated test suite powered by `pytest`.

To execute all unit and integration tests:
```bash
pytest -v
```

### Test Coverage Summary:
* ✅ Home page rendering
* ✅ Client and server-side form validation
* ✅ User creation and 7-day workout plan generation
* ✅ Result page retrieval and 404 error handling
* ✅ Feedback submission and dual-plan persistence
* ✅ Plan downloading (`.txt` generation)
* ✅ Admin authentication and route protection
* ✅ Admin user deletion with cascading plan removal
* ✅ HMAC security token validation
* ✅ Offline algorithmic fallback AI generation

---

## 18. Future Enhancements
* 📱 **Progressive Web App (PWA):** Offline service workers for offline gym caching.
* ⏱️ **Interactive Rest Timers:** Built-in stopwatch audio alerts between sets.
* 📈 **Workout Completion Tracking:** Checkboxes to mark finished exercises and track weekly compliance.
* 🎥 **Video Exercise Demonstrations:** 3D animated GIF / video clips for exercise execution cues.

---

## 19. Team Members
* **Project Developer & Lead Architect:** Academic Team
* **Institution:** Department of Computer Science & Engineering
* **Course / Project:** Full-Stack Web Application / AI Capstone

---

## 20. License
This project is licensed under the **MIT License** — feel free to use and adapt for academic and educational demonstrations.
