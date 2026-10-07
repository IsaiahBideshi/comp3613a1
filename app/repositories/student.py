from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.academic import Degree, DegreeCourse, Student, StudentPassedCourse


class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student(self, student_id: int) -> Optional[Student]:
        return self.db.get(Student, student_id)

    def get_degree(self, degree_id: int) -> Optional[Degree]:
        return self.db.get(Degree, degree_id)

    def get_degree_courses(self, degree_id: int) -> list[DegreeCourse]:
        return self.db.exec(
            select(DegreeCourse)
            .options(selectinload(DegreeCourse.course))
            .where(DegreeCourse.degree_id == degree_id)
            .order_by(DegreeCourse.year, DegreeCourse.semester, DegreeCourse.course_code)
        ).all()

    def get_passed_course_codes(self, student_id: int) -> set[str]:
        return set(self.db.exec(
            select(StudentPassedCourse.course_code)
            .where(StudentPassedCourse.student_id == student_id)
        ).all())
