from datetime import datetime

from app.models.academic import STATUS_APPROVED, STATUS_DENIED, STATUS_DRAFT, STATUS_SUBMITTED, Plan
from app.repositories.plan import PlanRepository
from app.repositories.student import StudentRepository


class PlanError(ValueError):
    """A change to a plan that is not allowed."""


class PlanService:
    def __init__(self, plan_repo: PlanRepository, student_repo: StudentRepository, year_semester: str):
        self.plan_repo = plan_repo
        self.student_repo = student_repo
        self.year_semester = year_semester
        self.semester = int(year_semester[-1])  # "2026-S1" -> 1

    def _plan(self, student_id: int) -> Plan:
        # The term's plan is created on the first visit and reused afterwards.
        # ponytail: two first visits at once make the unique constraint fail one of them; retry on IntegrityError if that shows up.
        return (
            self.plan_repo.get_plan(student_id, self.year_semester)
            or self.plan_repo.create_plan(student_id, self.year_semester)
        )

    def _editable_plan(self, student_id: int) -> Plan:
        plan = self._plan(student_id)
        if plan.status != STATUS_DRAFT:
            raise PlanError("This plan is no longer a draft, so it cannot be changed")
        return plan

    def _shown_status(self, plan: Plan) -> str:
        """What the status line reads for this plan: one of the STATUS_ constants."""
        if (plan.status == STATUS_DRAFT and plan.comment):
            return STATUS_DENIED
        return plan.status

    def get_plan(self, student_id: int) -> dict:
        """The student's plan for the current term and the courses they can pick from."""
        student = self.student_repo.get_student(student_id)
        plan = self._plan(student_id)
        degree_courses = self.student_repo.get_degree_courses(student.degree_id)
        passed_codes = self.student_repo.get_passed_course_codes(student_id)
        planned_codes = self.plan_repo.get_course_codes(plan.id)
        status = self._shown_status(plan)
        return {
            "plan": plan,
            "status": status,
            "denied": status == STATUS_DENIED,
            "editable": plan.status == STATUS_DRAFT,
            "submitted": plan.status == STATUS_SUBMITTED,
            "degree": self.student_repo.get_degree(student.degree_id),
            "planned": [c for c in degree_courses if c.course_code in planned_codes],
            # Every unpassed course on the degree that runs in the term's semester, across all years.
            "available": [
                c for c in degree_courses
                if c.semester == self.semester and c.course_code not in passed_codes
            ],
            "planned_codes": planned_codes,
        }

    def add_course(self, student_id: int, course_code: str) -> dict:
        plan = self._editable_plan(student_id)
        view = self.get_plan(student_id)
        if course_code not in {c.course_code for c in view["available"]}:
            raise PlanError(f"{course_code} is not one of your courses for this semester")
        if course_code not in view["planned_codes"]:
            self.plan_repo.add_course(plan.id, course_code)
        return self.get_plan(student_id)

    def remove_course(self, student_id: int, course_code: str) -> dict:
        self.plan_repo.remove_course(self._editable_plan(student_id).id, course_code)
        return self.get_plan(student_id)

    def reset(self, student_id: int) -> dict:
        self.plan_repo.clear_courses(self._editable_plan(student_id).id)
        return self.get_plan(student_id)

    def withdraw(self, student_id: int) -> dict:
        """Take a submitted plan back before an advisor decides, so it can be changed again."""
        plan = self._plan(student_id)
        if plan.status != STATUS_SUBMITTED:
            raise PlanError("Only a submitted plan can be removed from submission")
        plan.status = STATUS_DRAFT
        self.plan_repo.save(plan)
        return self.get_plan(student_id)

    def submit(self, student_id: int) -> dict:
        """Hand the plan to the advisors. It is locked from changes until one of them decides."""
        plan = self._editable_plan(student_id)
        if not self.plan_repo.get_course_codes(plan.id):
            raise PlanError("Add at least one course before submitting")
        plan.status = STATUS_SUBMITTED
        plan.date_submitted = datetime.now()  # overwritten on a resubmit
        self.plan_repo.save(plan)
        return self.get_plan(student_id)
