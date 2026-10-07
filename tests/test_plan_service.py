from types import SimpleNamespace

import pytest

from app.models.academic import STATUS_APPROVED, STATUS_DENIED, STATUS_DRAFT, STATUS_SUBMITTED
from app.services.plan_service import PlanError, PlanService


class FakeStudentRepository:
    def get_student(self, student_id):
        return SimpleNamespace(id=student_id, degree_id=1)

    def get_degree(self, degree_id):
        return SimpleNamespace(name="Degree")

    def get_passed_course_codes(self, student_id):
        return {"PASSED"}

    def get_degree_courses(self, degree_id):
        return [
            SimpleNamespace(course_code=code, semester=semester, is_core=False)
            for code, semester in [("PASSED", 1), ("SEM1", 1), ("SEM2", 2)]
        ]


class FakePlanRepository:
    def __init__(self):
        self.plan = SimpleNamespace(id=1, status=STATUS_DRAFT, date_submitted=None, comment=None)
        self.codes = set()

    def get_plan(self, student_id, year_semester):
        return self.plan

    def save(self, plan):
        return plan

    def get_course_codes(self, plan_id):
        return set(self.codes)

    def add_course(self, plan_id, course_code):
        self.codes.add(course_code)

    def remove_course(self, plan_id, course_code):
        self.codes.discard(course_code)

    def clear_courses(self, plan_id):
        self.codes.clear()


def make_service():
    return PlanService(FakePlanRepository(), FakeStudentRepository(), "2026-S1")


def test_only_unpassed_courses_for_the_terms_semester_can_be_planned():
    service = make_service()

    assert [c.course_code for c in service.get_plan(7)["available"]] == ["SEM1"]
    assert service.add_course(7, "SEM1")["planned_codes"] == {"SEM1"}
    for code in ["PASSED", "SEM2", "NOT A COURSE"]:
        with pytest.raises(PlanError):
            service.add_course(7, code)
    assert service.reset(7)["planned_codes"] == set()


def test_submitting_locks_the_plan():
    service = make_service()
    with pytest.raises(PlanError):
        service.submit(7)  # nothing planned yet
    service.add_course(7, "SEM1")

    view = service.submit(7)

    assert view["plan"].status == STATUS_SUBMITTED
    assert view["plan"].date_submitted is not None
    assert view["editable"] is False
    for change in [lambda: service.add_course(7, "SEM1"), lambda: service.remove_course(7, "SEM1"),
                   lambda: service.reset(7), lambda: service.submit(7)]:
        with pytest.raises(PlanError):
            change()
    assert view["planned_codes"] == {"SEM1"}


def test_removing_a_submission_makes_the_plan_a_draft_again():
    service = make_service()
    with pytest.raises(PlanError):
        service.withdraw(7)  # not submitted yet
    service.add_course(7, "SEM1")
    service.submit(7)

    view = service.withdraw(7)

    assert (view["status"], view["editable"], view["submitted"]) == (STATUS_DRAFT, True, False)
    assert view["planned_codes"] == {"SEM1"}


@pytest.mark.parametrize("stored, comment, shown", [
    (STATUS_DRAFT, None, STATUS_DRAFT),
    (STATUS_DRAFT, "reason", STATUS_DENIED),      # denied: back to draft, with the advisor's comment
    (STATUS_SUBMITTED, "reason", STATUS_SUBMITTED),  # resubmitted after a denial
    (STATUS_APPROVED, None, STATUS_APPROVED),
])
def test_status_shown_to_the_student(stored, comment, shown):
    service = make_service()
    service.plan_repo.plan.status = stored
    service.plan_repo.plan.comment = comment

    view = service.get_plan(7)

    assert view["status"] == shown
    assert view["denied"] is (shown == STATUS_DENIED)
