from app.models.academic import STATUS_APPROVED, STATUS_DRAFT, STATUS_SUBMITTED, Plan
from app.repositories.plan import PlanRepository
from app.repositories.student import StudentRepository
from app.services.plan_service import PlanError


class ReviewService:
    """What an advisor does with submitted plans. Any advisor can decide any submitted plan."""

    def __init__(self, plan_repo: PlanRepository, student_repo: StudentRepository):
        self.plan_repo = plan_repo
        self.student_repo = student_repo

    def get_pending(self, student_name: str = "") -> list[Plan]:
        """Submitted plans, oldest first, optionally only students whose name contains the text."""
        return self.plan_repo.get_by_status(STATUS_SUBMITTED, student_name.strip())

    def _submitted_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise PlanError("That plan does not exist")
        if plan.status == STATUS_APPROVED:
            raise PlanError("This plan has already been approved")
        if plan.status != STATUS_SUBMITTED:
            # Back with the student: they removed the submission, or another advisor denied it.
            raise PlanError("This plan has been removed")
        return plan

    def get_review(self, plan_id: int) -> dict:
        """A submitted plan with what the advisor needs to judge it."""
        plan = self._submitted_plan(plan_id)
        student = self.student_repo.get_student(plan.student_id)
        degree_courses = self.student_repo.get_degree_courses(student.degree_id)
        passed_codes = self.student_repo.get_passed_course_codes(student.id)
        planned_codes = self.plan_repo.get_course_codes(plan.id)
        semester = int(plan.year_semester[-1])  # "2026-S1" -> 1
        return {
            "plan": plan,
            "planned": [c for c in degree_courses if c.course_code in planned_codes],
            # The student's unpassed core courses that run in the plan's semester, across all years.
            "required": [
                c for c in degree_courses
                if c.is_core and c.semester == semester and c.course_code not in passed_codes
            ],
        }

    def approve(self, plan_id: int) -> Plan:
        plan = self._submitted_plan(plan_id)
        plan.status = STATUS_APPROVED
        plan.comment = None  # an approved plan carries no denial reason
        return self.plan_repo.save(plan)

    def deny(self, plan_id: int, comment: str) -> Plan:
        plan = self._submitted_plan(plan_id)
        comment = comment.strip()
        if not comment:
            raise PlanError("A comment is required to deny a plan")
        # There is no "denied" status: a denied plan is a draft again, with the advisor's comment.
        plan.status = STATUS_DRAFT
        plan.comment = comment  # replaces the comment from an earlier denial
        return self.plan_repo.save(plan)
