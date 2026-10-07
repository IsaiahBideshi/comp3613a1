from app.repositories.student import StudentRepository


class ProgressService:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    def get_progress(self, student_id: int) -> dict:
        """A student's degree checklist: passed and remaining courses, each grouped by (year, semester)."""
        student = self.student_repo.get_student(student_id)
        passed_codes = self.student_repo.get_passed_course_codes(student_id)

        passed, remaining = {}, {}
        for degree_course in self.student_repo.get_degree_courses(student.degree_id):
            group = passed if degree_course.course_code in passed_codes else remaining
            group.setdefault((degree_course.year, degree_course.semester), []).append(degree_course)

        return {
            "student": student,
            "degree": self.student_repo.get_degree(student.degree_id),
            "passed": passed,
            "remaining": remaining,
        }
