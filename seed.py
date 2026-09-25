import json
import logging
from app.database import SessionLocal, init_db
from app.models import User, WorkoutPlan
from app.gemini_service import generate_fallback_plan, modify_fallback_plan

logger = logging.getLogger(__name__)


def seed_database():
    """Seeds sample athlete profiles and AI workout routines if DB is empty."""
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding initial demo athletes and AI plans...")

        demo_users = [
            {
                "user_id": "marcus_hyper",
                "name": "Marcus Vance",
                "age": 26,
                "weight": 82.0,
                "goal": "Muscle Gain",
                "intensity": "High",
                "feedback": "I only have dumbbells and a pull-up bar at home"
            },
            {
                "user_id": "sarah_fit",
                "name": "Sarah Connor",
                "age": 31,
                "weight": 64.5,
                "goal": "Weight Loss",
                "intensity": "High",
                "feedback": None  # Original plan
            },
            {
                "user_id": "priya_wellness",
                "name": "Priya Sharma",
                "age": 28,
                "weight": 58.0,
                "goal": "General Wellness",
                "intensity": "Medium",
                "feedback": "Please add more restorative yoga on weekends"
            },
            {
                "user_id": "david_endurance",
                "name": "David Miller",
                "age": 35,
                "weight": 76.0,
                "goal": "Endurance",
                "intensity": "Medium",
                "feedback": None
            },
            {
                "user_id": "elena_flex",
                "name": "Elena Rostova",
                "age": 24,
                "weight": 54.0,
                "goal": "Flexibility",
                "intensity": "Low",
                "feedback": "Focus on hips and hamstring mobility"
            }
        ]

        for u in demo_users:
            user = User(
                user_id=u["user_id"],
                name=u["name"],
                age=u["age"],
                weight=u["weight"],
                goal=u["goal"],
                intensity=u["intensity"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Generate original plan
            user_data = {
                "name": user.name,
                "user_id": user.user_id,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity
            }
            orig_plan = generate_fallback_plan(user_data)
            orig_json = json.dumps(orig_plan)

            # Check if updated plan exists
            updated_json = None
            if u["feedback"]:
                updated_plan = modify_fallback_plan(orig_plan, user_data, u["feedback"])
                updated_json = json.dumps(updated_plan)

            plan_record = WorkoutPlan(
                user_id=user.user_id,
                original_plan=orig_json,
                updated_plan=updated_json,
                feedback=u["feedback"],
                nutrition_tip=orig_plan.get("nutrition_tip")
            )
            db.add(plan_record)

        db.commit()
        print(f"Successfully seeded {len(demo_users)} sample athletes!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
