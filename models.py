from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(60), nullable=False)
    intensity = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 1-to-1 relationship with WorkoutPlan
    workout_plan = relationship(
        "WorkoutPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', name='{self.name}', goal='{self.goal}')>"


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    original_plan = Column(Text, nullable=False)  # JSON-serialized 7-day plan
    updated_plan = Column(Text, nullable=True)    # JSON-serialized updated plan if modified
    feedback = Column(Text, nullable=True)        # Feedback history/notes
    nutrition_tip = Column(Text, nullable=True)   # AI nutrition & recovery recommendation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="workout_plan")

    def __repr__(self):
        return f"<WorkoutPlan(user_id='{self.user_id}', updated={'Yes' if self.updated_plan else 'No'})>"
