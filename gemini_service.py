import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configurable Gemini Model via environment variable
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()


def get_gemini_client():
    """Initializes and returns the Google GenAI client if API key is provided."""
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Client: {e}")
        return None


def generate_workout_plan(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a personalized 7-day workout plan and nutrition/recovery recommendations
    using Google Gemini AI based on user profile.
    """
    name = user_data.get("name", "User")
    age = user_data.get("age", 25)
    weight = user_data.get("weight", 70.0)
    goal = user_data.get("goal", "General Wellness")
    intensity = user_data.get("intensity", "Medium")

    client = get_gemini_client()
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    prompt = f"""
You are FitBuddy AI, an expert, certified fitness coach and sports nutritionist.
Create a personalized, scientifically sound, safe, and engaging 7-day workout and recovery plan for this user:

User Profile:
- Name: {name}
- Age: {age} years old
- Weight: {weight} kg
- Fitness Goal: {goal}
- Workout Intensity: {intensity}

Requirements:
1. Generate an exact 7-day schedule (Day 1 through Day 7).
2. For each day, specify:
   - day: integer from 1 to 7
   - title: engaging title (e.g., "Day 1 - Push & Core Foundation")
   - focus: primary muscle group or training objective
   - is_rest_day: boolean (true if active recovery or full rest day, false otherwise)
   - warm_up: specific 5-10 min dynamic warm-up
   - exercises: array of exercises (at least 4-6 exercises on workout days, empty or light mobility on rest days). Each exercise object must have:
       - name: exercise name
       - sets: number of sets (e.g. "3-4 sets")
       - reps: repetition range or time duration (e.g. "10-12 reps" or "45 secs")
       - rest: rest interval (e.g. "60-90s")
       - notes: brief coaching cue for good posture and safety
   - cool_down: 5 min cooldown and static stretching routine
3. Include 1 to 2 smart rest/active recovery days strategically placed across the 7 days depending on the intensity ({intensity}).
4. Provide a tailored "nutrition_tip" with practical hydration, macro balance, and sleep/recovery advice specific to their goal ({goal}) and weight ({weight}kg).
5. Output strict valid JSON only with NO markdown formatting around it, matching this schema:
{{
  "plan_title": "7-Day {goal} AI Fitness Blueprint",
  "summary": "Tailored 7-day workout plan for {name} to achieve {goal} with {intensity} intensity.",
  "days": [
    {{
      "day": 1,
      "title": "Day 1 - Focus Title",
      "focus": "Muscle Group / Activity",
      "is_rest_day": false,
      "warm_up": "Warm-up steps...",
      "exercises": [
        {{
          "name": "Exercise Name",
          "sets": "3 sets",
          "reps": "12 reps",
          "rest": "60s",
          "notes": "Coaching cue"
        }}
      ],
      "cool_down": "Cool-down steps..."
    }}
  ],
  "nutrition_tip": "Specific hydration, protein, meal timing, and sleep recovery advice...",
  "disclaimer": "This information is for general wellness and educational purposes and is not a substitute for professional medical or nutritional advice."
}}
"""

    if client:
        try:
            # Call Gemini using Google GenAI SDK (interactions API)
            response = client.interactions.create(
                model=model_name,
                input=prompt,
            )
            raw_text = response.output_text
            if raw_text:
                from app.utils import safe_json_loads, sanitize_workout_plan
                parsed = safe_json_loads(raw_text)
                if parsed and "days" in parsed:
                    return sanitize_workout_plan(parsed, user_name=name, goal=goal)
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {e}. Falling back to rule-based AI engine.")

    # Fallback algorithmic generation if API key is not configured or network error occurs
    return generate_fallback_plan(user_data)


def update_workout_plan(user_data: Dict[str, Any], original_plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
    """
    Regenerates/updates an existing 7-day workout plan based on user feedback
    (e.g., 'Add more cardio', 'I have only home dumbbells', 'Reduce intensity')
    using Google Gemini AI.
    """
    name = user_data.get("name", "User")
    goal = user_data.get("goal", "General Wellness")
    intensity = user_data.get("intensity", "Medium")

    client = get_gemini_client()
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    prompt = f"""
You are FitBuddy AI. A user has received their initial 7-day workout plan and provided specific feedback to improve and adapt it.

User Profile:
- Name: {name}
- Age: {user_data.get('age', 25)}
- Weight: {user_data.get('weight', 70.0)} kg
- Fitness Goal: {goal}
- Intensity: {intensity}

User's Feedback / Requested Adjustments:
"{feedback}"

Original Plan Overview:
- Original Title: {original_plan.get('plan_title', 'Original Plan')}
- Original Summary: {original_plan.get('summary', '')}

Instructions:
1. Modify the 7-day workout plan so that it directly fulfills the user's feedback (e.g., if they asked for yoga, bodyweight, extra cardio, more rest days, or low impact, incorporate those changes directly).
2. Maintain the safety and structural integrity of a 7-day schedule (Days 1 to 7).
3. Update the summary to highlight exactly how the plan was modified in response to: "{feedback}".
4. Update or refine the nutrition/recovery advice if relevant.
5. Output strictly valid JSON matching this schema:
{{
  "plan_title": "Updated 7-Day {goal} AI Plan (Customized)",
  "summary": "Plan updated based on your feedback: '{feedback}'. Here is your revised schedule.",
  "days": [
    {{
      "day": 1,
      "title": "Day 1 - Focus Title",
      "focus": "Focus Area",
      "is_rest_day": false,
      "warm_up": "Warm-up steps...",
      "exercises": [
        {{
          "name": "Exercise Name",
          "sets": "3 sets",
          "reps": "12 reps",
          "rest": "60s",
          "notes": "Coaching cue"
        }}
      ],
      "cool_down": "Cool-down steps..."
    }}
  ],
  "nutrition_tip": "Refined nutrition and recovery advice...",
  "disclaimer": "This information is for general wellness and educational purposes and is not a substitute for professional medical or nutritional advice."
}}
"""

    if client:
        try:
            response = client.interactions.create(
                model=model_name,
                input=prompt,
            )
            raw_text = response.output_text
            if raw_text:
                from app.utils import safe_json_loads, sanitize_workout_plan
                parsed = safe_json_loads(raw_text)
                if parsed and "days" in parsed:
                    return sanitize_workout_plan(parsed, user_name=name, goal=goal)
        except Exception as e:
            logger.warning(f"Gemini API update error: {e}. Falling back to intelligent feedback modifier.")

    # Fallback feedback modifier
    return modify_fallback_plan(original_plan, user_data, feedback)


def generate_fallback_plan(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent algorithmic fallback generator for offline testing or missing API keys.
    Provides complete, highly realistic 7-day customized fitness plans.
    """
    name = user_data.get("name", "Athlete")
    age = user_data.get("age", 25)
    goal = user_data.get("goal", "General Wellness")
    intensity = user_data.get("intensity", "Medium")
    weight = user_data.get("weight", 70.0)

    # Goal-tailored schedules
    if goal == "Weight Loss":
        days = [
            {
                "day": 1,
                "title": "Day 1 - High-Intensity Full Body & Metabolic Conditioning",
                "focus": "Full Body Calorie Burn & Core",
                "is_rest_day": False,
                "warm_up": "6 mins: Arm circles, high knees, jumping jacks, hip openers",
                "exercises": [
                    {"name": "Bodyweight Jump Squats", "sets": "4 sets", "reps": "15 reps", "rest": "45s", "notes": "Land softly on midfoot and explode upwards"},
                    {"name": "Mountain Climbers", "sets": "4 sets", "reps": "30 secs", "rest": "30s", "notes": "Maintain plank position with fast knees"},
                    {"name": "Push-Ups to T-Spine Rotation", "sets": "3 sets", "reps": "10 reps", "rest": "45s", "notes": "Engage obliques on the top twist"},
                    {"name": "Dumbbell/Kettlebell Goblet Squats", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Keep chest proud, elbows tucked"},
                    {"name": "Bicycle Crunches", "sets": "3 sets", "reps": "20 reps total", "rest": "30s", "notes": "Rotate from ribcage, don't pull on neck"}
                ],
                "cool_down": "5 mins: Child's pose, cat-cow stretch, quad stretches"
            },
            {
                "day": 2,
                "title": "Day 2 - Steady-State Cardio & Core Endurance",
                "focus": "Aerobic Capacity & Fat Oxidation",
                "is_rest_day": False,
                "warm_up": "5 mins: Light jog in place, leg swings, torso twists",
                "exercises": [
                    {"name": "Brisk Incline Walk or Light Jogging", "sets": "1 continuous session", "reps": "25-30 mins", "rest": "N/A", "notes": "Maintain Zone 2 target heart rate (65-75% max HR)"},
                    {"name": "Plank with Shoulder Taps", "sets": "3 sets", "reps": "16 taps", "rest": "45s", "notes": "Resist hip rocking as hands lift"},
                    {"name": "Side Plank Hold", "sets": "3 sets", "reps": "30 secs/side", "rest": "30s", "notes": "Stack hips and shoulders in one line"},
                    {"name": "Flutter Kicks", "sets": "3 sets", "reps": "30 secs", "rest": "30s", "notes": "Press lower back firmly into floor"}
                ],
                "cool_down": "5 mins: Cobra pose, calf and hamstring stretches"
            },
            {
                "day": 3,
                "title": "Day 3 - Lower Body Strength & Glute Power",
                "focus": "Legs, Glutes & Posterior Chain",
                "is_rest_day": False,
                "warm_up": "6 mins: Glute bridges, bodyweight air squats, walking knee hugs",
                "exercises": [
                    {"name": "Romanian Deadlifts (Dumbbells/Barbell)", "sets": "4 sets", "reps": "12 reps", "rest": "60s", "notes": "Hinge hips backward with soft knees"},
                    {"name": "Walking Lunges with DBs", "sets": "3 sets", "reps": "12 reps/leg", "rest": "60s", "notes": "90 degree bend in both knees"},
                    {"name": "Glute Bridges (or Hip Thrusts)", "sets": "3 sets", "reps": "15 reps", "rest": "45s", "notes": "Squeeze glutes hard for 2 secs at top"},
                    {"name": "Calf Raises on Step", "sets": "3 sets", "reps": "20 reps", "rest": "30s", "notes": "Full stretch at bottom, strong calf contraction"}
                ],
                "cool_down": "5 mins: Pigeon pose, seated forward fold"
            },
            {
                "day": 4,
                "title": "Day 4 - Active Recovery & Mobility Reset",
                "focus": "Cardio Flush, Joint Mobility & Flexibility",
                "is_rest_day": True,
                "warm_up": "5 mins: Gentle diaphragmatic breathing and neck rolls",
                "exercises": [
                    {"name": "Outdoor Nature Walk", "sets": "1 session", "reps": "30-40 mins", "rest": "N/A", "notes": "Low intensity, leisurely pace for mental and physical recovery"},
                    {"name": "Full Body Foam Rolling & Mobility Routine", "sets": "1 session", "reps": "15 mins", "rest": "N/A", "notes": "Target tight quads, upper back, and lats"}
                ],
                "cool_down": "5 mins: Supine spinal twists and deep breathing"
            },
            {
                "day": 5,
                "title": "Day 5 - Upper Body Tone & HIIT Circuit",
                "focus": "Chest, Back, Arms & Metabolic Burn",
                "is_rest_day": False,
                "warm_up": "6 mins: Arm circles, band pull-aparts, light shadow boxing",
                "exercises": [
                    {"name": "Dumbbell Overhead Press", "sets": "4 sets", "reps": "10-12 reps", "rest": "60s", "notes": "Core locked tight, press directly overhead"},
                    {"name": "Bent-Over Dumbbell Rows", "sets": "4 sets", "reps": "12 reps", "rest": "60s", "notes": "Pull with elbows grazing your ribs"},
                    {"name": "Push-Ups (or Kneeling Push-Ups)", "sets": "3 sets", "reps": "10-15 reps", "rest": "45s", "notes": "Full chest depth"},
                    {"name": "Burpees with Jump", "sets": "3 sets", "reps": "10 reps", "rest": "60s", "notes": "Fluid motion, modify without push-up if fatigued"}
                ],
                "cool_down": "5 mins: Chest doorway stretch, triceps overhead stretch"
            },
            {
                "day": 6,
                "title": "Day 6 - Total Body Interval Shred",
                "focus": "Full Body Conditioning & Core Circuit",
                "is_rest_day": False,
                "warm_up": "5 mins: Dynamic lunges with torso twists, butt kicks",
                "exercises": [
                    {"name": "Kettlebell / Dumbbell Swings", "sets": "4 sets", "reps": "15 reps", "rest": "45s", "notes": "Explosive hip drive, maintain straight back"},
                    {"name": "Step-Ups onto Bench", "sets": "3 sets", "reps": "12 reps/leg", "rest": "45s", "notes": "Drive through the lead heel"},
                    {"name": "Plank Jack to Tuck", "sets": "3 sets", "reps": "12 reps", "rest": "45s", "notes": "Keep hips stable and level"},
                    {"name": "Russian Twists", "sets": "3 sets", "reps": "20 reps", "rest": "30s", "notes": "Control the rotation, touch floor on both sides"}
                ],
                "cool_down": "5 mins: Hamstring stretches, child's pose"
            },
            {
                "day": 7,
                "title": "Day 7 - Rest, Recharge & Weekly Review",
                "focus": "Complete Rest & Restoration",
                "is_rest_day": True,
                "warm_up": "Light stretching if desired",
                "exercises": [],
                "cool_down": "Hydration review and meal prep for the upcoming week"
            }
        ]
        nutrition_tip = f"For Weight Loss ({weight} kg): Maintain a moderate caloric deficit (300-500 kcal below maintenance). Prioritize 1.6-2.0g of lean protein per kg of bodyweight ({int(weight * 1.8)}g/day) to preserve lean muscle while burning fat. Drink at least 3 liters of pure water daily and stop caffeine 8 hours before bedtime."
    
    elif goal == "Muscle Gain":
        days = [
            {
                "day": 1,
                "title": "Day 1 - Push Hypertrophy (Chest, Shoulders, Triceps)",
                "focus": "Upper Body Push Strength & Volume",
                "is_rest_day": False,
                "warm_up": "8 mins: Arm circles, light pushups, resistance band pull-aparts",
                "exercises": [
                    {"name": "Barbell or Dumbbell Bench Press", "sets": "4 sets", "reps": "8-10 reps", "rest": "90s", "notes": "Controlled 2-second eccentric descent, drive upward"},
                    {"name": "Incline Dumbbell Press", "sets": "3 sets", "reps": "10-12 reps", "rest": "75s", "notes": "Set bench to 30 degrees, feel the upper chest stretch"},
                    {"name": "Dumbbell Lateral Raises", "sets": "4 sets", "reps": "12-15 reps", "rest": "60s", "notes": "Slight forward lean, raise elbows to shoulder height"},
                    {"name": "Overhead Tricep Extension", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Keep elbows fixed pointing toward ceiling"},
                    {"name": "Push-Ups to Failure", "sets": "2 burnout sets", "reps": "Max reps", "rest": "60s", "notes": "Finish with strict form until fatigue"}
                ],
                "cool_down": "5 mins: Pec doorway stretch, tricep stretch, shoulder rolls"
            },
            {
                "day": 2,
                "title": "Day 2 - Pull Hypertrophy (Back, Rear Delts, Biceps)",
                "focus": "Upper Body Pull & Posterior Width",
                "is_rest_day": False,
                "warm_up": "8 mins: Dead hangs, cat-cow, thoracic spine rotations",
                "exercises": [
                    {"name": "Lat Pulldown (or Pull-Ups)", "sets": "4 sets", "reps": "8-10 reps", "rest": "90s", "notes": "Pull elbows down to hips, squeeze lats"},
                    {"name": "Seated Cable Row / Barbell Row", "sets": "4 sets", "reps": "10 reps", "rest": "75s", "notes": "Retract shoulder blades and hold for 1 sec"},
                    {"name": "Face Pulls with Rope", "sets": "3 sets", "reps": "15 reps", "rest": "60s", "notes": "Great for posture and rear deltoid strength"},
                    {"name": "Incline Dumbbell Bicep Curls", "sets": "3 sets", "reps": "10-12 reps", "rest": "60s", "notes": "Full range of motion, avoid swinging"},
                    {"name": "Hammer Curls", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Builds brachialis and forearm thickness"}
                ],
                "cool_down": "5 mins: Lat stretch on wall, bicep and forearm stretches"
            },
            {
                "day": 3,
                "title": "Day 3 - Leg Day Quad & Calf Focus",
                "focus": "Lower Body Quad Drive & Explosiveness",
                "is_rest_day": False,
                "warm_up": "8 mins: Leg swings, bodyweight squats, hip 90/90 mobility",
                "exercises": [
                    {"name": "Barbell / Dumbbell Back Squats", "sets": "4 sets", "reps": "8-10 reps", "rest": "120s", "notes": "Hit parallel depth, drive through whole foot"},
                    {"name": "Bulgarian Split Squats", "sets": "3 sets", "reps": "10 reps/leg", "rest": "75s", "notes": "Deep stretch on the rear hip flexor"},
                    {"name": "Leg Extension Machine", "sets": "3 sets", "reps": "12-15 reps", "rest": "60s", "notes": "Hold peak contraction at the top"},
                    {"name": "Standing Calf Raises", "sets": "4 sets", "reps": "15-20 reps", "rest": "45s", "notes": "Pause 2 seconds at the stretch"}
                ],
                "cool_down": "6 mins: Quad stretch, hip flexor stretch, foam rolling"
            },
            {
                "day": 4,
                "title": "Day 4 - Rest, Growth & Muscle Recovery",
                "focus": "Active Recovery & Muscle Glycogen Reload",
                "is_rest_day": True,
                "warm_up": "Gentle mobility and walking",
                "exercises": [
                    {"name": "Light 20-minute Recovery Walk", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "notes": "Enhances blood flow to recovering muscles"}
                ],
                "cool_down": "10 mins full body stretching and hydration"
            },
            {
                "day": 5,
                "title": "Day 5 - Upper Body Power & Weak-Point Focus",
                "focus": "Chest, Back & Shoulder Strength",
                "is_rest_day": False,
                "warm_up": "8 mins: Resistance band circles, scapular push-ups",
                "exercises": [
                    {"name": "Overhead Barbell / DB Military Press", "sets": "4 sets", "reps": "6-8 reps", "rest": "90s", "notes": "Squeeze glutes and core to protect lower back"},
                    {"name": "Chest Supported Dumbbell Row", "sets": "4 sets", "reps": "10-12 reps", "rest": "75s", "notes": "Eliminate momentum for pure back activation"},
                    {"name": "Dips (Bodyweight or Weighted)", "sets": "3 sets", "reps": "10-12 reps", "rest": "75s", "notes": "Forward lean for chest, upright for triceps"},
                    {"name": "EZ-Bar Preacher Curls", "sets": "3 sets", "reps": "10-12 reps", "rest": "60s", "notes": "Strict bicep isolation"}
                ],
                "cool_down": "5 mins: Upper body static stretches"
            },
            {
                "day": 6,
                "title": "Day 6 - Hamstrings, Glutes & Abs",
                "focus": "Posterior Chain Hypertrophy & Core",
                "is_rest_day": False,
                "warm_up": "8 mins: Glute bridges, inchworms, high knees",
                "exercises": [
                    {"name": "Romanian Deadlifts (RDLs)", "sets": "4 sets", "reps": "8-10 reps", "rest": "90s", "notes": "Feel deep stretch in hamstrings before snapping hips up"},
                    {"name": "Lying or Seated Hamstring Curls", "sets": "3 sets", "reps": "12-15 reps", "rest": "60s", "notes": "Slow 3-second negative"},
                    {"name": "Barbell / DB Hip Thrusts", "sets": "4 sets", "reps": "10-12 reps", "rest": "90s", "notes": "Tuck chin, full hip extension at top"},
                    {"name": "Hanging Knee / Leg Raises", "sets": "3 sets", "reps": "12-15 reps", "rest": "45s", "notes": "Avoid swinging, curl pelvis upward"}
                ],
                "cool_down": "5 mins: Pigeon pose, hamstring wall stretch"
            },
            {
                "day": 7,
                "title": "Day 7 - Complete Rest & Recovery",
                "focus": "Anabolic Sleep & Full Restoration",
                "is_rest_day": True,
                "warm_up": "Relaxation and breathing",
                "exercises": [],
                "cool_down": "8 hours sleep priority and hydration check"
            }
        ]
        nutrition_tip = f"For Muscle Hypertrophy ({weight} kg): Consume a slight caloric surplus (+300 to 400 kcal/day). Target 1.8-2.2g of quality protein per kg of bodyweight ({int(weight * 2.0)}g protein/day) distributed across 4-5 meals. Ensure a 30g protein snack with complex carbs within 60 minutes post-workout."

    else:
        # General Wellness / Endurance / Flexibility
        days = [
            {
                "day": 1,
                "title": f"Day 1 - {goal} Foundation & Total Body Tone",
                "focus": "Functional Movement, Posture & Core Stability",
                "is_rest_day": False,
                "warm_up": "6 mins: Arm circles, hip openers, cat-cow, bird-dog",
                "exercises": [
                    {"name": "Goblet Squats", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Maintain proud chest and steady breathing"},
                    {"name": "Dumbbell Bench / Floor Press", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Control the descent"},
                    {"name": "Single-Arm Dumbbell Rows", "sets": "3 sets", "reps": "10 reps/side", "rest": "60s", "notes": "Keep back flat and pull through elbow"},
                    {"name": "Deadbugs", "sets": "3 sets", "reps": "12 reps total", "rest": "30s", "notes": "Lower opposite arm and leg while bracing core"}
                ],
                "cool_down": "5 mins: Cobra stretch, child's pose, gentle deep breaths"
            },
            {
                "day": 2,
                "title": "Day 2 - Cardiovascular Flow & Core Endurance",
                "focus": "Heart Health & Aerobic Conditioning",
                "is_rest_day": False,
                "warm_up": "5 mins: Light jumping jacks, dynamic ankle and knee mobility",
                "exercises": [
                    {"name": "Moderate Intensity Cycling / Rowing / Jogging", "sets": "1 continuous session", "reps": "25 mins", "rest": "N/A", "notes": "Comfortable conversational pace"},
                    {"name": "Bodyweight Reverse Lunges", "sets": "3 sets", "reps": "10 reps/leg", "rest": "45s", "notes": "Step backward gently to protect knees"},
                    {"name": "Forearm Plank Hold", "sets": "3 sets", "reps": "45 seconds", "rest": "45s", "notes": "Keep glutes squeezed and neck neutral"}
                ],
                "cool_down": "5 mins: Quad stretches and standing hamstring stretches"
            },
            {
                "day": 3,
                "title": "Day 3 - Functional Strength & Balance",
                "focus": "Unilateral Strength, Core & Balance",
                "is_rest_day": False,
                "warm_up": "6 mins: Inchworms, glute bridges, shoulder rolls",
                "exercises": [
                    {"name": "Step-Ups with Light Dumbbells", "sets": "3 sets", "reps": "10 reps/leg", "rest": "60s", "notes": "Smooth single leg drive"},
                    {"name": "Standing Overhead Press", "sets": "3 sets", "reps": "10-12 reps", "rest": "60s", "notes": "Engage abdominal wall"},
                    {"name": "Glute Bridge with 2-sec hold", "sets": "3 sets", "reps": "15 reps", "rest": "45s", "notes": "Target glutes without arching lower back"},
                    {"name": "Bird-Dog Extensions", "sets": "3 sets", "reps": "10 reps/side", "rest": "30s", "notes": "Slow and controlled movement"}
                ],
                "cool_down": "5 mins: Downward dog, pigeon pose, deep diaphragmatic breathing"
            },
            {
                "day": 4,
                "title": "Day 4 - Rest & Dynamic Mobility Restoration",
                "focus": "Flexibility, Spine Health & Active Recovery",
                "is_rest_day": True,
                "warm_up": "Gentle neck and shoulder rolls",
                "exercises": [
                    {"name": "Full Body Mobility & Yoga Flow", "sets": "1 session", "reps": "25 mins", "rest": "N/A", "notes": "Sun salutations, warriors, and gentle hip openers"},
                    {"name": "20-minute Fresh Air Walk", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "notes": "Leisurely recovery walk"}
                ],
                "cool_down": "5 mins: Savasana / deep relaxation breathing"
            },
            {
                "day": 5,
                "title": "Day 5 - Full Body Circuit & Stamina",
                "focus": "Endurance, Muscular Tone & Heart Rate",
                "is_rest_day": False,
                "warm_up": "5 mins: High knees, arm swings, bodyweight squats",
                "exercises": [
                    {"name": "Kettlebell/Dumbbell Deadlifts", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Drive through heels, stand tall"},
                    {"name": "Push-Ups (Incline or Standard)", "sets": "3 sets", "reps": "10-12 reps", "rest": "60s", "notes": "Keep body in one straight line"},
                    {"name": "Lat Pulldown / Resistance Band Rows", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "notes": "Focus on squeezing back muscles"},
                    {"name": "Side Plank Hold", "sets": "3 sets", "reps": "30s/side", "rest": "30s", "notes": "Keep body aligned"}
                ],
                "cool_down": "5 mins: Doorway chest stretch, hip flexor stretch"
            },
            {
                "day": 6,
                "title": "Day 6 - Active Cardio, Core & Agility",
                "focus": "Agility, Core Power & Calorie Burn",
                "is_rest_day": False,
                "warm_up": "5 mins: Butt kicks, arm circles, torso twists",
                "exercises": [
                    {"name": "Interval Cardio (Run/Walk or Cycling)", "sets": "6 intervals", "reps": "1 min fast / 1 min easy", "rest": "N/A", "notes": "Elevate heart rate safely"},
                    {"name": "Bicycle Crunches", "sets": "3 sets", "reps": "20 reps total", "rest": "30s", "notes": "Control every rep"},
                    {"name": "Russian Twists", "sets": "3 sets", "reps": "16 reps", "rest": "30s", "notes": "Keep spine elongated"}
                ],
                "cool_down": "5 mins: Full body static stretching"
            },
            {
                "day": 7,
                "title": "Day 7 - Complete Mind & Body Restoration",
                "focus": "Sleep, Hydration & Wellness Reset",
                "is_rest_day": True,
                "warm_up": "Gentle stretching if desired",
                "exercises": [],
                "cool_down": "Hydration and nutrition check for next week"
            }
        ]
        nutrition_tip = f"For {goal} ({weight} kg): Focus on whole, nutrient-dense foods: colorful vegetables, whole grains, healthy fats (avocados, nuts), and lean proteins ({int(weight * 1.4)}g/day). Drink at least 2.5–3 liters of water and prioritize 7–8 hours of consistent sleep."

    return {
        "plan_title": f"7-Day {goal} AI Fitness Blueprint",
        "summary": f"Personalized 7-day fitness regimen generated for {name} ({age} yrs, {weight} kg) targeting {goal} at {intensity} intensity.",
        "days": days,
        "nutrition_tip": nutrition_tip,
        "disclaimer": "This information is for general wellness and educational purposes and is not a substitute for professional medical or nutritional advice."
    }


def modify_fallback_plan(original_plan: Dict[str, Any], user_data: Dict[str, Any], feedback: str) -> Dict[str, Any]:
    """
    Algorithmic modifier to adjust the workout plan when Gemini API is offline.
    """
    import copy
    updated = copy.deepcopy(original_plan)
    feedback_lower = feedback.lower()

    updated["plan_title"] = f"{original_plan.get('plan_title', 'AI Fitness Plan')} (Modified: {feedback[:30]}...)"
    updated["summary"] = f"Customized 7-day schedule adjusted specifically based on your feedback: '{feedback}'."

    # If feedback asks for home / bodyweight workouts
    if any(w in feedback_lower for w in ["home", "bodyweight", "no equipment", "calisthenics"]):
        for d in updated.get("days", []):
            if not d.get("is_rest_day", False):
                d["title"] = f"{d.get('title', '')} (Home Bodyweight Edition)"
                for ex in d.get("exercises", []):
                    if "barbell" in ex["name"].lower() or "cable" in ex["name"].lower() or "machine" in ex["name"].lower():
                        ex["name"] = ex["name"].replace("Barbell", "Bodyweight / Banded").replace("Cable", "Resistance Band").replace("Machine", "Bodyweight")
                        ex["notes"] = f"Adapted for Home Workout: {ex.get('notes', '')}"

    # If feedback asks for more cardio or HIIT
    elif any(w in feedback_lower for w in ["cardio", "hiit", "aerobic", "running", "burn"]):
        for d in updated.get("days", []):
            if not d.get("is_rest_day", False):
                d["exercises"].append({
                    "name": "HIIT Finisher (Jumping Jacks / Mountain Climbers)",
                    "sets": "3 sets",
                    "reps": "45 secs on / 15 secs off",
                    "rest": "30s",
                    "notes": f"Added based on your request for more cardio ({feedback})"
                })

    # If feedback asks for yoga / stretching / flexibility
    elif any(w in feedback_lower for w in ["yoga", "stretch", "flexibility", "mobility"]):
        for d in updated.get("days", []):
            d["cool_down"] = f"Extended 15-min Yoga Flow & Mobility: {d.get('cool_down', '')}"
            if d.get("is_rest_day", False):
                d["title"] = f"{d.get('title', '')} - Restorative Yoga & Mindfulness"
                d["exercises"] = [
                    {"name": "Vinyasa Sun Salutations", "sets": "4 rounds", "reps": "Flow with breath", "rest": "30s", "notes": "Focus on deep spinal extension"},
                    {"name": "Pigeon Pose & Hip Openers", "sets": "2 sets", "reps": "90 secs/side", "rest": "N/A", "notes": "Deep relaxation for hips and lower back"}
                ]

    # If feedback asks for lower intensity or injury safe
    elif any(w in feedback_lower for w in ["low intensity", "reduce", "easier", "lighter", "knee", "back", "injury", "gentle"]):
        for d in updated.get("days", []):
            if not d.get("is_rest_day", False):
                d["title"] = f"{d.get('title', '')} (Low-Impact Modified)"
                for ex in d.get("exercises", []):
                    ex["sets"] = "2-3 sets"
                    ex["rest"] = "75-90s"
                    ex["notes"] = f"Low impact variation: {ex.get('notes', '')}"

    # If feedback asks for more rest
    elif any(w in feedback_lower for w in ["rest", "recovery", "tired", "fewer days"]):
        if len(updated.get("days", [])) >= 5:
            updated["days"][4]["is_rest_day"] = True
            updated["days"][4]["title"] = "Day 5 - Additional Active Recovery & Hydration"
            updated["days"][4]["focus"] = "Added Recovery Day based on your feedback"
            updated["days"][4]["exercises"] = [
                {"name": "Light 20-min Nature Walk", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "notes": "Low intensity walk for recovery"}
            ]

    return updated
