from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from app.models.academic import Plan, PlanCourse, Student
from app.models.user import User


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_plan(self, student_id: int, year_semester: str) -> Optional[Plan]:
        return self.db.exec(
            select(Plan).where(Plan.student_id == student_id, Plan.year_semester == year_semester)
        ).one_or_none()

    def get_by_id(self, plan_id: int) -> Optional[Plan]:
        return self.db.get(Plan, plan_id)

    def get_by_status(self, status: str, student_name: str = "") -> list[Plan]:
        """Plans in one status, oldest submission first, optionally only students whose name contains the text."""
        query = (
            select(Plan)
            .join(Student, Plan.student_id == Student.id)
            .join(User, Student.id == User.id)
            .where(Plan.status == status)
            .order_by(Plan.date_submitted)
            .options(
                selectinload(Plan.student).selectinload(Student.user),
                selectinload(Plan.student).selectinload(Student.degree),
            )
        )
        if student_name:
            full_name = User.first_name + " " + User.last_name
            query = query.where(full_name.icontains(student_name, autoescape=True))
        return self.db.exec(query).all()

    def create_plan(self, student_id: int, year_semester: str) -> Plan:
        return self.save(Plan(student_id=student_id, year_semester=year_semester))

    def save(self, plan: Plan) -> Plan:
        # ponytail: services check a plan's status and then save, so two changes to one plan at the
        # same moment let the last one win. Use a conditional UPDATE on status if that ever matters.
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_course_codes(self, plan_id: int) -> set[str]:
        return set(self.db.exec(
            select(PlanCourse.course_code).where(PlanCourse.plan_id == plan_id)
        ).all())

    def add_course(self, plan_id: int, course_code: str) -> None:
        self.db.add(PlanCourse(plan_id=plan_id, course_code=course_code))
        self.db.commit()

    def remove_course(self, plan_id: int, course_code: str) -> None:
        self.db.exec(delete(PlanCourse).where(
            PlanCourse.plan_id == plan_id, PlanCourse.course_code == course_code
        ))
        self.db.commit()

    def clear_courses(self, plan_id: int) -> None:
        self.db.exec(delete(PlanCourse).where(PlanCourse.plan_id == plan_id))
        self.db.commit()
