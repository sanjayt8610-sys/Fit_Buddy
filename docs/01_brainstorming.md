# 01. Brainstorming & Ideation Phase

## Project Name: FitBuddy – AI Fitness Plan Generator
**Tagline:** Your AI-Powered Fitness Companion

---

## 1. Executive Summary & Problem Space

### Problem Statement
In modern lifestyle routines, physical fitness and healthy nutrition are critical for longevity and well-being. However, the majority of beginners and intermediate fitness enthusiasts face severe bottlenecks:
1. **High Financial Barrier:** Hiring a certified personal fitness coach or sports nutritionist costs hundreds of dollars monthly.
2. **Generic Static Workout Templates:** Most online workout PDFs and cookie-cutter apps fail to take an individual's unique age, weight, goal, and workout intensity into account.
3. **Lack of Feedback Adaptability:** When a user experiences knee discomfort, lack of gym machines (requiring home bodyweight workouts), or requests more cardio, static plans cannot modify themselves.
4. **Information Overload & Misinformation:** Conflicting fitness advice online often leads to burnout, overtraining, and lack of injury prevention guidance.

### Proposed Solution
**FitBuddy** is an intelligent, full-stack web application powered by **Google Gemini AI**, **FastAPI**, **SQLite (SQLAlchemy ORM)**, and **Modern CSS3/ES6 JavaScript**. It collects an athlete's vital parameters, formulates a scientifically structured **7-Day Workout Routine**, calculates targeted **Nutrition & Recovery Strategies**, and allows continuous **Interactive Feedback-Driven Plan Adaptation** while maintaining historical plan integrity in an SQLite database.

---

## 2. Target Audience & Personas

| Persona | Demographics & Context | Primary Need | FitBuddy Value Proposition |
| :--- | :--- | :--- | :--- |
| **Beginner Athlete (e.g., Alex, 21)** | College student, no gym experience | Safe, easy-to-follow introductory workout routine | Provides structured warm-up, clear set/rep ranges, and safety cues with moderate intensity |
| **Busy Professional (e.g., Priya, 29)** | Work-from-home, limited equipment | Home bodyweight workouts, time efficiency | Generates customized routines and modifies them instantly via feedback (e.g. "home dumbbells only") |
| **Hypertrophy Enthusiast (e.g., Marcus, 24)** | Gym goer seeking progressive overload | Muscle gain periodization & protein intake calculation | Generates Push/Pull/Legs splits, recovery windows, and tailored protein grams per kg of bodyweight |
| **Fitness Coach / Administrator (e.g., Coach Dave)** | Gym instructor managing multiple trainees | Centralized dashboard to track athlete telemetry | Protected admin portal with user metrics, goal distribution, and plan inspection |

---

## 3. Core Feature Ideation Matrix

```
                      HIGH IMPACT
                          │
         7-Day AI Plan    │   Adaptive Feedback Loop
         Generation       │   (Plan Modification)
                          │
  ────────────────────────┼──────────────────────── LOW EFFORT
  HIGH EFFORT             │
         Admin Analytics  │   Print & Text Export
         & User Inspector │   Form Validation & Loading State
                          │
                      LOW IMPACT
```

### Core Value Deliverables
1. **Instant AI 7-Day Periodization:** Day-by-day breakdown with focus areas, warm-ups, exercises, set/rep ranges, rest times, and cooldowns.
2. **Intelligent Nutrition & Recovery Engine:** Goal-specific protein, hydration, and sleep hygiene guidelines based on user bodyweight.
3. **Two-Way Feedback Engine:** Users provide conversational feedback (e.g., "Add more cardio", "Reduce intensity") and Gemini regenerates an updated edition while keeping the original baseline intact.
4. **Secure Admin Portal:** Authenticated administrative cockpit with live KPIs, search/filter capabilities, and user plan inspection modals.

---

## 4. Technology Stack Justification

* **FastAPI (Python):** High-performance asynchronous backend with native Pydantic data validation and auto-generated OpenAPI (`/docs` and `/redoc`) documentation.
* **Google Gemini AI (`google-genai` SDK):** State-of-the-art multimodal reasoning with configurable model routing (e.g., `gemini-2.5-flash` / `gemini-3.8-flash`) and structured JSON schema outputs.
* **SQLAlchemy ORM & SQLite:** Lightweight, ACID-compliant relational persistence that requires zero external server setup for seamless evaluation and deployment.
* **Jinja2 & Vanilla CSS3 / ES6:** Clean, framework-free frontend architecture utilizing CSS Grid, Flexbox, and Glassmorphism design aesthetics.

---

## 5. Risk Assessment & AI Safety Considerations

| Risk | Mitigation Strategy in FitBuddy |
| :--- | :--- |
| **Inaccurate or dangerous medical claims** | Explicit general wellness disclaimer on all plans; conservative set/rep progression guidelines |
| **Gemini API rate limit / Network disruption** | Resilient offline algorithmic fallback engine; prevents app crash and supplies high-fidelity plans |
| **Client-side API Key Leakage** | Gemini SDK calls are strictly executed on the FastAPI backend; zero keys in frontend JavaScript |
| **Unsanitized input injection** | Multi-layer validation via Pydantic schemas, regex constraints, and SQLAlchemy parameterized queries |
