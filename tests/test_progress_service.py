"""Run with: python -m pytest tests"""

from types import SimpleNamespace

from app.services.progress_service import ProgressService


class FakeStudentRepository:
    def get_student(self, student_id):
        return SimpleNamespace(id=student_id, degree_id=1, gpa=3.0)

    def get_degree(self, degree_id):
        return SimpleNamespace(id=degree_id, name="Degree")

    def get_passed_course_codes(self, student_id):
        return {"A", "C"}

    def get_degree_courses(self, degree_id):
        return [
            SimpleNamespace(course_code=code, year=year, semester=semester, is_core=True)
            for code, year, semester in [("A", 1, 1), ("B", 1, 1), ("C", 1, 2), ("D", 2, 1)]
        ]


def test_progress_splits_passed_from_remaining_by_year_and_semester():
    progress = ProgressService(FakeStudentRepository()).get_progress(7)

    codes = lambda groups: {key: [c.course_code for c in courses] for key, courses in groups.items()}
    assert codes(progress["passed"]) == {(1, 1): ["A"], (1, 2): ["C"]}
    assert codes(progress["remaining"]) == {(1, 1): ["B"], (2, 1): ["D"]}
