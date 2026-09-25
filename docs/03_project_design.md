# 03. Project Design & System Architecture

## 1. High-Level Architectural Design

FitBuddy is structured using the **Model-View-Controller (MVC) / Layered Services** architecture in Python with FastAPI:

```
┌────────────────────────────────────────────────────────┐
│                   CLIENT BROWSER LAYER                 │
│   HTML5 / Modern CSS3 (Glassmorphism) / Vanilla ES6 JS  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP Requests / Form Data
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FASTAPI ROUTING LAYER                │
│    (GET /, POST /generate-workout, GET /result/...,    │
│     POST /submit-feedback, GET /view-all-users)        │
└──────────────┬────────────────────────────┬────────────┘
               │                            │
               ▼                            ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│     PYDANTIC SCHEMAS LAYER    │ │  ADMIN SECURITY &    │
│  (UserProfileCreate, Feedback)│ │  HMAC TOKEN HANDLER  │
└──────────────┬────────────────┘ └──────────┬───────────┘
               │                             │
               ▼                             ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│   GEMINI AI SERVICE LAYER     │ │   SQLITE DATABASE    │
│   (google-genai SDK Client /  │ │   (SQLAlchemy ORM    │
│    Prompt Engineering /       │ │    User & Workout    │
│    Resilient Fallback Engine) │ │    Plan Tables)      │
└───────────────────────────────┘ └──────────────────────┘
```

---

## 2. Database Entity-Relationship (ER) Design

The database schema utilizes an optimized **1-to-1 Relationship** between the `User` and `WorkoutPlan` entities with cascade deletion on delete.

```
┌────────────────────────────────────────┐
│                 users                  │
├────────────────────────────────────────┤
│  id          : INTEGER [PK]            │
│  user_id     : VARCHAR(64) [UNIQUE]    │
│  name        : VARCHAR(120)            │
│  age         : INTEGER                 │
│  weight      : FLOAT                   │
│  goal        : VARCHAR(60)             │
│  intensity   : VARCHAR(30)             │
│  created_at  : DATETIME                │
└──────────────────┬─────────────────────┘
                   │
                   │ 1-to-1 (CASCADE DELETE)
                   │
┌──────────────────▼─────────────────────┐
│             workout_plans              │
├────────────────────────────────────────┤
│  id            : INTEGER [PK]          │
│  user_id       : VARCHAR(64) [FK]      │
│  original_plan : TEXT (JSON string)    │
│  updated_plan  : TEXT (JSON string)    │
│  feedback      : TEXT                  │
│  nutrition_tip : TEXT                  │
│  created_at    : DATETIME              │
│  updated_at    : DATETIME              │
└────────────────────────────────────────┘
```

---

## 3. UI/UX Design System & Color Tokens

* **Primary Background:** `#0a0d14` (Deep Charcoal Black)
* **Surface Cards:** `rgba(18, 24, 38, 0.75)` with `16px` backdrop blur
* **Electric Accent:** `#00e676` (Neon Electric Lime)
* **Secondary Accent:** `#3b82f6` (Cyan / Electric Blue)
* **Feedback Amber:** `#fbbf24` / `#f59e0b`
* **Typography:**
  * Headings: `Outfit` (700/800/900 weight)
  * Body: `Inter` (400/500/600 weight)

---

## 4. RESTful & Presentation Endpoint Schema

| Method | Path | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Renders landing page & interactive generator form | Public |
| `POST` | `/generate-workout` | Validates profile, invokes Gemini, saves plan, redirects | Public |
| `GET` | `/result/{user_id}` | Renders 7-day workout cards, nutrition tip, and actions | Public |
| `GET` | `/feedback/{user_id}` | Renders feedback refinement view with quick tags | Public |
| `POST` | `/submit-feedback` | Regenerates plan with feedback and stores in `updated_plan` | Public |
| `GET` | `/api/user/{user_id}/download` | Generates plain-text export format of the 7-day routine | Public |
| `GET` | `/api/user/{user_id}/json` | Returns full plan JSON for modal inspection & external clients | Public |
| `GET` | `/admin/login` | Renders admin authentication view | Public |
| `POST` | `/admin/login` | Validates credentials against `.env`, sets signed cookie | Public |
| `GET` | `/admin/logout` | Clears admin session cookie and redirects | Admin |
| `GET` | `/view-all-users` | Renders admin KPI analytics, search/filter user table | Admin Protected |
| `POST` | `/admin/delete-user/{user_id}` | Deletes athlete profile and plan with cascade | Admin Protected |
| `GET` | `/docs` | Interactive Swagger API documentation | Public |
| `GET` | `/redoc` | OpenAPI ReDoc documentation | Public |
