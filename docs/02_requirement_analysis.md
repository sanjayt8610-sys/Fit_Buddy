# 02. Requirement Analysis & Specifications

## 1. Functional Requirements (FR)

### FR-01: User Profile Registration & Input Validation
* **FR-01.1:** The system shall collect user parameters: Full Name, User ID (alphanumeric/hyphens), Age (13–120), Weight in kg (20–350 kg), Fitness Goal, and Workout Intensity.
* **FR-01.2:** Supported Fitness Goals: `Weight Loss`, `Muscle Gain`, `General Wellness`, `Flexibility`, and `Endurance`.
* **FR-01.3:** Supported Workout Intensities: `Low`, `Medium`, and `High`.
* **FR-01.4:** Input validation must occur on both client-side (HTML5/JavaScript) and server-side (FastAPI/Pydantic).

### FR-02: AI-Powered 7-Day Workout Generation
* **FR-02.1:** The system shall construct an engineered prompt combining user attributes and send it to the Google Gemini AI service.
* **FR-02.2:** The AI must return a structured 7-day schedule containing Day number, Title, Focus area, Warm-up, Exercise items (name, sets, reps, rest interval, coaching cues), and Cool-down.
* **FR-02.3:** Strategic rest and recovery days must be scheduled depending on the user's selected intensity.
* **FR-02.4:** The AI output must be validated and sanitized as structured JSON for rendering into UI cards.

### FR-03: Nutrition & Recovery Recommendations
* **FR-03.1:** The system shall generate personalized hydration, daily protein targets (per kg of bodyweight), meal timing, and sleep advice.
* **FR-03.2:** A wellness disclaimer must be attached to all output recommendations.

### FR-04: Dual-Plan Persistence & Database Storage
* **FR-04.1:** The system shall store the user profile in the `users` table and the workout routine in the `workout_plans` table using SQLite via SQLAlchemy ORM.
* **FR-04.2:** The original plan and updated plan must be stored in separate database columns (`original_plan` and `updated_plan`).

### FR-05: Adaptive Feedback Loop & Regeneration
* **FR-05.1:** Users can provide feedback (e.g. "Add more cardio", "I prefer home workouts").
* **FR-05.2:** The system transmits the user profile, original plan, and feedback to Gemini AI to generate an updated plan without overwriting the original.

### FR-06: Export, Printing, and Clipboard Support
* **FR-06.1:** Users can print the workout routine using browser print (`@media print` optimized).
* **FR-06.2:** Users can download a clean `.txt` document via the `/api/user/{user_id}/download` endpoint.
* **FR-06.3:** Users can copy the formatted plan to their system clipboard with 1 click.

### FR-07: Protected Admin Dashboard
* **FR-07.1:** Admin dashboard accessible at `/view-all-users`, protected by session authentication via `/admin/login`.
* **FR-07.2:** Dashboard displays key metrics: Total Users, Total Plans, Modified Plans, and Goal Ratio.
* **FR-07.3:** Includes dynamic search by name/ID, filtering by Goal, Intensity, and Plan Status.
* **FR-07.4:** Allows admins to inspect individual user plans in a modal dialog or delete records with confirmation.

---

## 2. Non-Functional Requirements (NFR)

| Category | Requirement Specification |
| :--- | :--- |
| **Performance** | Page rendering under 500ms; AI plan generation latency under 4 seconds |
| **Security** | Zero client-side API key exposure; HMAC-SHA256 authenticated admin sessions; parameterized SQL queries |
| **Reliability & Resilience** | Graceful fallback engine if Gemini API key is missing or encounters rate limits |
| **Usability & UX** | Dark mode fitness aesthetics with electric lime accents, glassmorphism cards, and smooth micro-animations |
| **Responsiveness** | Fluid compatibility across Mobile (320px+), Tablet, Laptop, and Desktop screens |
| **Maintainability** | Clean separation of concerns across `routes.py`, `models.py`, `schemas.py`, `gemini_service.py`, and `utils.py` |

---

## 3. Data Flow Diagram (DFD - Level 1)

```
 [ Athlete / User ]
         │
         │  1. Submit Profile Form
         ▼
 [ FastAPI Routes (/generate-workout) ]
         │
         ├── 2. Validate with Pydantic
         ├── 3. Upsert User in SQLite Database (users table)
         │
         ▼
 [ Gemini AI Service (app/gemini_service.py) ]
         │
         ├── 4. Call Google GenAI SDK (gemini-2.5-flash)
         └── 5. Receive Structured 7-Day Plan JSON + Nutrition
         │
         ▼
 [ Database Layer (workout_plans table) ]
         │
         ├── 6. Store original_plan JSON string
         │
         ▼
 [ Result Dashboard (/result/{user_id}) ] ◄── 7. Render 7-Day Cards & Actions
         │
         │  8. Submit Feedback ("Add more cardio")
         ▼
 [ Feedback Engine (/submit-feedback) ]
         │
         ├── 9. Retrieve Original Plan + Prompt Gemini
         ├── 10. Save into updated_plan column
         └── 11. Render Updated Plan View with Feedback Badge
```
