import os
import json
import logging
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import UserProfileCreate, FeedbackSubmission
from app.gemini_service import generate_workout_plan, update_workout_plan
from app.utils import (
    create_admin_token,
    verify_admin_token,
    safe_json_loads,
    sanitize_workout_plan,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------------
# 1. Home Page
# -------------------------------------------------------------
@router.get("/", response_class=HTMLResponse, summary="Home Page")
async def home(request: Request):
    """Renders the FitBuddy modern landing page and user profile input form."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "goals": ["Weight Loss", "Muscle Gain", "General Wellness", "Flexibility", "Endurance"],
            "intensities": ["Low", "Medium", "High"]
        }
    )


# -------------------------------------------------------------
# 2. Generate Workout Plan
# -------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse, summary="Generate 7-Day AI Workout Plan")
async def generate_workout(
    request: Request,
    name: str = Form(default=""),
    user_id: str = Form(default=""),
    age: str = Form(default=""),
    weight: str = Form(default=""),
    goal: str = Form(default=""),
    intensity: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Validates form data, saves/updates user in database,
    calls Gemini AI service to generate a 7-day plan,
    saves the workout plan, and displays the result page.
    """
    # 1. Parse numbers safely
    parsed_age = None
    parsed_weight = None
    validation_error = None

    try:
        if not age or not age.strip():
            validation_error = "Please enter your age."
        else:
            parsed_age = int(age.strip())
    except ValueError:
        validation_error = "Please enter a valid age between 13 and 120."

    if not validation_error:
        try:
            if not weight or not weight.strip():
                validation_error = "Please enter your weight in kg."
            else:
                parsed_weight = float(weight.strip())
        except ValueError:
            validation_error = "Please enter a valid weight between 20 kg and 350 kg."

    if not validation_error:
        # Pydantic validation
        try:
            profile_data = UserProfileCreate(
                name=name,
                user_id=user_id,
                age=parsed_age,
                weight=parsed_weight,
                goal=goal,
                intensity=intensity
            )
        except Exception as e:
            error_msg = str(e)
            if "Name" in error_msg or "name" in error_msg:
                validation_error = "Please enter a valid name (at least 2 characters)."
            elif "User ID" in error_msg or "user_id" in error_msg:
                validation_error = "User ID must contain only alphanumeric characters, underscores, or hyphens (3-50 chars)."
            elif "Age" in error_msg or "age" in error_msg:
                validation_error = "Please enter a valid age between 13 and 120."
            elif "Weight" in error_msg or "weight" in error_msg:
                validation_error = "Please enter a valid weight between 20 kg and 350 kg."
            elif "Goal" in error_msg or "goal" in error_msg:
                validation_error = "Please select a valid fitness goal."
            elif "Intensity" in error_msg or "intensity" in error_msg:
                validation_error = "Please select a workout intensity."
            else:
                validation_error = "Please check your input values and try again."

    if validation_error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": validation_error,
                "form_data": {
                    "name": name,
                    "user_id": user_id,
                    "age": age,
                    "weight": weight,
                    "goal": goal,
                    "intensity": intensity
                },
                "goals": ["Weight Loss", "Muscle Gain", "General Wellness", "Flexibility", "Endurance"],
                "intensities": ["Low", "Medium", "High"]
            },
            status_code=400
        )

    try:
        # 2. Save or update user in database
        clean_user_id = profile_data.user_id.lower().strip()
        existing_user = db.query(User).filter(User.user_id == clean_user_id).first()

        if existing_user:
            existing_user.name = profile_data.name
            existing_user.age = profile_data.age
            existing_user.weight = profile_data.weight
            existing_user.goal = profile_data.goal
            existing_user.intensity = profile_data.intensity
            user = existing_user
        else:
            user = User(
                user_id=clean_user_id,
                name=profile_data.name,
                age=profile_data.age,
                weight=profile_data.weight,
                goal=profile_data.goal,
                intensity=profile_data.intensity
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)

        # 3. Call Gemini AI Service
        user_dict = {
            "name": user.name,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        }
        
        plan_dict = generate_workout_plan(user_dict)

        # 4. Save workout plan in database
        existing_plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.user_id).first()
        plan_json_str = json.dumps(plan_dict)
        nutrition_tip = plan_dict.get("nutrition_tip", "")

        if existing_plan:
            existing_plan.original_plan = plan_json_str
            existing_plan.updated_plan = None
            existing_plan.feedback = None
            existing_plan.nutrition_tip = nutrition_tip
            workout_plan_record = existing_plan
        else:
            workout_plan_record = WorkoutPlan(
                user_id=user.user_id,
                original_plan=plan_json_str,
                updated_plan=None,
                feedback=None,
                nutrition_tip=nutrition_tip
            )
            db.add(workout_plan_record)

        db.commit()

        # Redirect to result page
        return RedirectResponse(url=f"/result/{user.user_id}", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        db.rollback()
        logger.error(f"Error generating workout for {user_id}: {e}", exc_info=True)
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "Plan Generation Issue",
                "error_message": "AI service encountered an unexpected error while generating your plan. Please try again in a few moments."
            },
            status_code=500
        )


# -------------------------------------------------------------
# 3. Result Page
# -------------------------------------------------------------
@router.get("/result/{user_id}", response_class=HTMLResponse, summary="View User Workout Plan")
async def view_result(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Displays the generated 7-day workout plan, nutrition advice, and profile summary."""
    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "User Not Found",
                "error_message": f"No workout plan or profile found for User ID: '{user_id}'."
            },
            status_code=404
        )

    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == clean_user_id).first()
    if not plan_record or not plan_record.original_plan:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "No Plan Generated",
                "error_message": f"A profile exists for {user.name}, but no 7-day plan has been generated yet."
            },
            status_code=404
        )

    # Determine whether to show updated plan or original plan
    is_updated = bool(plan_record.updated_plan)
    active_plan_raw = plan_record.updated_plan if is_updated else plan_record.original_plan
    plan_data = sanitize_workout_plan(active_plan_raw, user_name=user.name, goal=user.goal)

    original_plan_data = None
    if is_updated:
        original_plan_data = sanitize_workout_plan(plan_record.original_plan, user_name=user.name, goal=user.goal)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan_data,
            "is_updated": is_updated,
            "feedback_text": plan_record.feedback,
            "original_plan": original_plan_data,
            "nutrition_tip": plan_data.get("nutrition_tip") or plan_record.nutrition_tip
        }
    )


# -------------------------------------------------------------
# 4. Feedback View & Submission
# -------------------------------------------------------------
@router.get("/feedback/{user_id}", response_class=HTMLResponse, summary="Feedback Form Page")
async def feedback_page(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Renders the interactive feedback page for fine-tuning the workout plan."""
    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "User Not Found",
                "error_message": f"User '{user_id}' was not found."
            },
            status_code=404
        )

    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == clean_user_id).first()
    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context={
            "user": user,
            "plan_record": plan_record
        }
    )


@router.post("/submit-feedback", response_class=HTMLResponse, summary="Submit Feedback & Regenerate Plan")
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Receives user feedback, retrieves original plan,
    prompts Gemini AI to adapt/regenerate the 7-day plan,
    saves the updated plan alongside the original, and redirects to result page.
    """
    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "User Not Found",
                "error_message": f"User ID '{user_id}' does not exist."
            },
            status_code=404
        )

    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == clean_user_id).first()
    if not plan_record or not plan_record.original_plan:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "Original Plan Missing",
                "error_message": "Original workout plan was not found to apply feedback on."
            },
            status_code=400
        )

    clean_feedback = feedback.strip()
    if not clean_feedback:
        return templates.TemplateResponse(
            request=request,
            name="feedback.html",
            context={
                "user": user,
                "plan_record": plan_record,
                "error": "Feedback cannot be empty. Please tell us what to adjust!"
            },
            status_code=400
        )

    try:
        user_dict = {
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        }
        original_dict = safe_json_loads(plan_record.original_plan)

        # Call Gemini AI to adapt plan based on feedback
        updated_dict = update_workout_plan(user_dict, original_dict, clean_feedback)

        # Store updated plan without overwriting original
        plan_record.updated_plan = json.dumps(updated_dict)
        plan_record.feedback = clean_feedback
        if updated_dict.get("nutrition_tip"):
            plan_record.nutrition_tip = updated_dict.get("nutrition_tip")

        db.commit()

        return RedirectResponse(url=f"/result/{user.user_id}", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting feedback for {user_id}: {e}", exc_info=True)
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error_title": "Feedback Processing Failed",
                "error_message": "AI could not update your workout plan at this time. Please try again."
            },
            status_code=500
        )


# -------------------------------------------------------------
# 5. Admin Authentication & Dashboard
# -------------------------------------------------------------
@router.get("/admin/login", response_class=HTMLResponse, summary="Admin Login Page")
async def admin_login_page(request: Request):
    """Renders the admin login form."""
    token = request.cookies.get("admin_session")
    if verify_admin_token(token):
        return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@router.post("/admin/login", response_class=HTMLResponse, summary="Authenticate Admin")
async def admin_login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Validates admin credentials from environment variables and sets session cookie."""
    env_user = os.getenv("ADMIN_USERNAME", "admin")
    env_pass = os.getenv("ADMIN_PASSWORD", "admin123")

    if username.strip() == env_user and password.strip() == env_pass:
        token = create_admin_token(username.strip())
        redirect_res = RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)
        redirect_res.set_cookie(
            key="admin_session",
            value=token,
            httponly=True,
            max_age=86400,
            samesite="lax"
        )
        return redirect_res

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid admin username or password. Please check your credentials."},
        status_code=401
    )


@router.get("/admin/logout", summary="Admin Logout")
async def admin_logout():
    """Logs out admin by clearing cookie."""
    res = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    res.delete_cookie("admin_session")
    return res


@router.get("/view-all-users", response_class=HTMLResponse, summary="Admin Dashboard")
async def view_all_users(
    request: Request,
    q: Optional[str] = None,
    goal: Optional[str] = None,
    intensity: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Protected Admin Dashboard:
    - Verifies admin authentication
    - Calculates platform statistics
    - Displays searchable & filterable user table
    - Provides modal / detail viewing for original and updated plans
    """
    token = request.cookies.get("admin_session")
    if not verify_admin_token(token):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    query = db.query(User).outerjoin(WorkoutPlan, User.user_id == WorkoutPlan.user_id)

    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter((User.name.ilike(search)) | (User.user_id.ilike(search)))

    if goal and goal.strip():
        query = query.filter(User.goal == goal.strip())

    if intensity and intensity.strip():
        query = query.filter(User.intensity == intensity.strip())

    users_list = query.order_by(User.created_at.desc()).all()

    processed_users = []
    for u in users_list:
        p = u.workout_plan
        has_plan = p is not None and bool(p.original_plan)
        is_updated = p is not None and bool(p.updated_plan)
        
        plan_status = "Updated" if is_updated else ("Original" if has_plan else "No Plan")

        if status_filter:
            if status_filter == "Updated" and not is_updated:
                continue
            elif status_filter == "Original" and (not has_plan or is_updated):
                continue
            elif status_filter == "No Plan" and has_plan:
                continue

        processed_users.append({
            "user": u,
            "plan_record": p,
            "has_plan": has_plan,
            "is_updated": is_updated,
            "plan_status": plan_status,
            "original_plan_json": safe_json_loads(p.original_plan) if p and p.original_plan else None,
            "updated_plan_json": safe_json_loads(p.updated_plan) if p and p.updated_plan else None
        })

    # Platform Statistics
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_plans = db.query(func.count(WorkoutPlan.id)).scalar() or 0
    updated_plans = db.query(func.count(WorkoutPlan.id)).filter(WorkoutPlan.updated_plan.isnot(None)).scalar() or 0
    
    goal_counts = dict(db.query(User.goal, func.count(User.id)).group_by(User.goal).all())

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "users": processed_users,
            "stats": {
                "total_users": total_users,
                "total_plans": total_plans,
                "updated_plans": updated_plans,
                "goal_counts": goal_counts
            },
            "filters": {
                "q": q or "",
                "goal": goal or "",
                "intensity": intensity or "",
                "status_filter": status_filter or ""
            },
            "goals": ["Weight Loss", "Muscle Gain", "General Wellness", "Flexibility", "Endurance"],
            "intensities": ["Low", "Medium", "High"]
        }
    )


@router.post("/admin/delete-user/{user_id}", summary="Admin Delete User & Plan")
async def delete_user(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Deletes a user record and their associated workout plan."""
    token = request.cookies.get("admin_session")
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)


# -------------------------------------------------------------
# 6. Export / Download & API Endpoints
# -------------------------------------------------------------
@router.get("/api/user/{user_id}/download", summary="Download Workout Plan as Text/Markdown")
async def download_plan(user_id: str, db: Session = Depends(get_db)):
    """Generates a downloadable clean text/markdown summary of the user's workout plan."""
    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == clean_user_id).first()
    if not plan_record or not plan_record.original_plan:
        raise HTTPException(status_code=404, detail="No plan found")

    raw_plan = plan_record.updated_plan if plan_record.updated_plan else plan_record.original_plan
    plan_dict = sanitize_workout_plan(raw_plan, user_name=user.name, goal=user.goal)

    lines = []
    lines.append("=" * 60)
    lines.append(" FITBUDDY - AI PERSONALIZED 7-DAY FITNESS BLUEPRINT")
    lines.append("=" * 60)
    lines.append(f"Athlete: {user.name} (ID: {user.user_id})")
    lines.append(f"Age: {user.age} yrs | Weight: {user.weight} kg")
    lines.append(f"Goal: {user.goal} | Intensity: {user.intensity}")
    if plan_record.updated_plan:
        lines.append(f"Status: Modified with user feedback: '{plan_record.feedback}'")
    lines.append("-" * 60)
    lines.append(f"Plan Title: {plan_dict.get('plan_title')}")
    lines.append(f"Summary: {plan_dict.get('summary')}")
    lines.append("=" * 60)
    lines.append("")

    for day in plan_dict.get("days", []):
        lines.append(f"--- {day.get('title')} ---")
        lines.append(f"Focus: {day.get('focus')}")
        lines.append(f"Warm-up: {day.get('warm_up')}")
        if day.get("is_rest_day"):
            lines.append("Status: REST & RECOVERY DAY")
        else:
            lines.append("Exercises:")
            for idx, ex in enumerate(day.get("exercises", []), 1):
                notes = f" | Notes: {ex.get('notes')}" if ex.get('notes') else ""
                lines.append(f"  {idx}. {ex.get('name')} -> {ex.get('sets')} x {ex.get('reps')} (Rest: {ex.get('rest')}){notes}")
        lines.append(f"Cool-down: {day.get('cool_down')}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("AI NUTRITION & RECOVERY RECOMMENDATION:")
    lines.append(plan_dict.get("nutrition_tip", ""))
    lines.append("")
    lines.append("DISCLAIMER:")
    lines.append(plan_dict.get("disclaimer", ""))
    lines.append("=" * 60)

    content = "\n".join(lines)
    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f"attachment; filename=FitBuddy_Plan_{user.user_id}.txt"}
    )


@router.get("/api/user/{user_id}/json", summary="Get User Plan as JSON")
async def get_user_plan_json(user_id: str, db: Session = Depends(get_db)):
    """REST API endpoint returning structured JSON representation of user plan."""
    clean_user_id = user_id.lower().strip()
    user = db.query(User).filter(User.user_id == clean_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == clean_user_id).first()
    return JSONResponse(content={
        "user": {
            "name": user.name,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": str(user.created_at)
        },
        "has_plan": plan_record is not None,
        "is_updated": plan_record is not None and bool(plan_record.updated_plan),
        "feedback": plan_record.feedback if plan_record else None,
        "plan": sanitize_workout_plan(plan_record.updated_plan if plan_record and plan_record.updated_plan else (plan_record.original_plan if plan_record else {}), user_name=user.name, goal=user.goal)
    })
