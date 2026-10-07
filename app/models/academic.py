from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import UniqueConstraint

from app.models.user import User


class Degree(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Course(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str


class Student(SQLModel, table=True):
    # Shares its primary key with User: one Student row per student account.
    id: int = Field(primary_key=True, foreign_key="user.id")
    degree_id: int = Field(foreign_key="degree.id")
    gpa: float

    user: User = Relationship()
    degree: Degree = Relationship()


class DegreeCourse(SQLModel, table=True):
    degree_id: int = Field(primary_key=True, foreign_key="degree.id")
    course_code: str = Field(primary_key=True, foreign_key="course.code")
    is_core: bool = Field(default=False)
    year: int
    semester: int

    course: Course = Relationship()


class StudentPassedCourse(SQLModel, table=True):
    student_id: int = Field(primary_key=True, foreign_key="student.id")
    course_code: str = Field(primary_key=True, foreign_key="course.code")


# Plan.status values. Other files import these instead of typing the strings.
STATUS_DRAFT = "draft"
STATUS_SUBMITTED = "submitted"
STATUS_APPROVED = "approved"
STATUS_DENIED = "denied" # This is display only and not stored in the database, a plan is denied if it is draft and has a comment.


class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    year_semester: str
    status: str = Field(default=STATUS_DRAFT)
    comment: Optional[str] = Field(default=None)
    date_submitted: Optional[datetime] = Field(default=None)

    student: Student = Relationship()

    __table_args__ = (
        UniqueConstraint("student_id", "year_semester", name="unique_plan_per_term"),
    )


class PlanCourse(SQLModel, table=True):
    plan_id: int = Field(primary_key=True, foreign_key="plan.id")
    course_code: str = Field(primary_key=True, foreign_key="course.code")