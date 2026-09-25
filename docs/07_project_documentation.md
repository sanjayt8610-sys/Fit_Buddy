# 07. Project Documentation & Deployment Guide

## 1. System Requirements

* **Operating System:** Windows 10/11, macOS, or Linux
* **Python Runtime:** Python 3.9+ (Python 3.11 recommended)
* **Web Browser:** Modern browser (Chrome, Firefox, Edge, Safari)
* **Internet Connection:** Required for Google Gemini AI API calls (offline fallback is automatically engaged if unavailable)

---

## 2. Installation & Setup Walkthrough

### Step 1: Clone or Navigate to Project
```bash
cd C:\Fit_Buddy
```

### Step 2: Create and Activate Virtual Environment
```bash
# On Windows:
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your desired configuration:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password
DATABASE_URL=sqlite:///./fitness.db
SECRET_KEY=fitbuddy_super_secret_session_key_2026
```

### Step 5: Run Application with Uvicorn
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the application in your browser:
* **Web Application:** `http://127.0.0.1:8000`
* **Admin Dashboard:** `http://127.0.0.1:8000/admin/login` (or `/view-all-users`)
* **Interactive API Docs (Swagger):** `http://127.0.0.1:8000/docs`
* **Alternative API Docs (ReDoc):** `http://127.0.0.1:8000/redoc`

---

## 3. Database Management & Schema Initialization

The SQLite database (`fitness.db`) is automatically generated with all tables and relationships during application startup via the FastAPI lifespan event in `app/main.py`.

To inspect or reset the database:
```bash
# To reset database (delete and restart app to regenerate fresh tables):
rm fitness.db
```
