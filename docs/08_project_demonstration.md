# 08. Project Demonstration & Viva Presentation Script

## 1. College Viva / Demonstration Flow

When demonstrating **FitBuddy** to professors, evaluators, or project reviewers, follow this structured 5-step script:

---

### Step 1: Landing Page & Architectural Overview (1–2 minutes)
* **Open:** `http://127.0.0.1:8000`
* **Highlight:**
  * Modern, dark-themed fitness design with electric lime glowing accents and ambient background orbs.
  * Clear explanation of the 3-step process: Input Profile ➔ Gemini AI Synthesis ➔ Execute & Refine.
  * Zero exposure of AI API keys in the client-side code (demonstrating security best practices).

> *Screenshot Placeholder 1: FitBuddy Landing Page & Hero Section*
> `[ SCREENSHOT: Landing Page / Hero Section ]`

---

### Step 2: Generating a Personalized 7-Day Workout (2 minutes)
* **Navigate to Form:** Scroll down or click **"Create My Fitness Plan"**.
* **Demonstrate Validation:**
  * Enter invalid values (e.g. negative weight or age < 13) to demonstrate real-time client & server validation.
* **Submit Valid Data:**
  * Name: `Jordan Lee`
  * User ID: `jordan_fit`
  * Age: `24`
  * Weight: `74.5`
  * Goal: `Muscle Gain` (or `Weight Loss`)
  * Intensity: `High`
* **Observe Loading Experience:**
  * Point out the animated dumbbell, progress bar, and AI step badges.

> *Screenshot Placeholder 2: Interactive Fitness Profile Form & Validation*
> `[ SCREENSHOT: Fitness Profile Form ]`

> *Screenshot Placeholder 3: Animated AI Loading Overlay*
> `[ SCREENSHOT: Loading Screen with Dumbbell Animation ]`

---

### Step 3: Result Dashboard & AI Plan Inspection (2 minutes)
* **Result Page Overview:**
  * Point out the athlete greeting: **"Hi, Jordan Lee! 👋"**
  * Profile metric cards (Age, Weight, Goal, Intensity).
  * Day 1 to Day 7 cards showing structured warm-ups, exercise tables (Sets, Reps, Rest, Coaching cues), and cool-downs.
  * Active Recovery / Rest Day badges.
  * AI Nutrition & Recovery card with tailored protein calculation and sleep guidelines.
  * Wellness & medical disclaimer.

> *Screenshot Placeholder 4: Result Dashboard & 7-Day Workout Cards*
> `[ SCREENSHOT: 7-Day Workout Plan Result Dashboard ]`

---

### Step 4: Adaptive Feedback Loop (2 minutes)
* **Click:** **"Improve / Give Feedback"**
* **Select Quick Tag:** Click `+ Home Workouts Only` or type *"I don't have gym equipment, please adjust to bodyweight exercises and add yoga stretches"*.
* **Submit:** Click **"Update My AI Plan"**.
* **Observe:**
  * The plan is regenerated with home bodyweight exercises and yoga cooldowns.
  * Notice the **"Updated with Feedback"** amber badge.
  * Emphasize to evaluators that **both** the original plan and updated plan remain preserved in SQLite!

> *Screenshot Placeholder 5: Interactive Feedback Page*
> `[ SCREENSHOT: Feedback Input with Suggestion Chips ]`

> *Screenshot Placeholder 6: Updated Plan Dashboard with Modification Badge*
> `[ SCREENSHOT: Updated Plan View ]`

---

### Step 5: Exporting & Admin Dashboard (2 minutes)
* **Exporting:**
  * Click **"Print Plan"** (show clean white-paper `@media print` view).
  * Click **"Download Plan"** (opens formatted `.txt` file).
  * Click **"Copy Plan"** (copies to clipboard with toast notification).
* **Admin Dashboard:**
  * Go to `http://127.0.0.1:8000/view-all-users`
  * Show login authentication (`admin` / `admin123`).
  * Point out KPI statistics (Total Users, Total Plans, Updated Plans, Goal Distribution).
  * Demonstrate search and filtering (Goal, Intensity, Plan status).
  * Click **"👁️ Inspect"** on a user to demonstrate the dynamic Plan Inspector modal.
  * Demonstrate delete confirmation modal.

> *Screenshot Placeholder 7: Admin Login Portal*
> `[ SCREENSHOT: Admin Authentication Card ]`

> *Screenshot Placeholder 8: Admin Analytics Dashboard & User Table*
> `[ SCREENSHOT: Admin Analytics Dashboard with Filterable Table ]`

> *Screenshot Placeholder 9: Live Plan Inspector Modal*
> `[ SCREENSHOT: Admin Plan Inspector Modal Dialog ]`

---

## 2. Common Viva Q&A Guide

| Question | Recommended Answer |
| :--- | :--- |
| **Q1: Why did you choose FastAPI over Flask or Django?** | FastAPI provides native asynchronous execution, automatic Pydantic data validation, built-in Swagger/OpenAPI documentation (`/docs`), and superior performance. |
| **Q2: How is the Gemini API key protected?** | The API key is stored strictly in server-side environment variables (`.env`) and invoked solely within `app/gemini_service.py` on the backend. No frontend JavaScript or HTML ever sees the key. |
| **Q3: What happens if Gemini API experiences network downtime?** | FitBuddy includes an intelligent offline algorithmic fallback engine that calculates biomechanically sound 7-day plans, ensuring zero downtime during demonstrations. |
| **Q4: How does the feedback loop preserve historical data?** | The `workout_plans` table stores both `original_plan` and `updated_plan` as distinct columns, enabling version tracking and side-by-side comparison. |
| **Q5: How is Admin access secured?** | We use HMAC-SHA256 cryptographically signed session tokens with expiration timestamps, verified on protected administrative endpoints. |
