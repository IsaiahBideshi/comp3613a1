"""Demo data: logins, one degree with its courses, and each student's passed courses.

DRAFT: the course codes, names, core flags and year/semester placement below were
written from memory of the BSc Computer Science (Special) listing. Check every row
against the university booklet.
"""

from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.config import get_settings
from app.models import Course, Degree, DegreeCourse, Plan, PlanCourse, Student, StudentPassedCourse
from app.models.academic import STATUS_SUBMITTED
from app.models.user import UserBase
from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password

# (university ID, first name, last name, email, password, role)
USERS = [
    ("816012345", "John", "Doe", "student@example.com", "studentpass", "student"),
    ("816012346", "Maria", "Ali", "maria.ali@example.com", "studentpass", "student"),
    ("816012347", "Kevin", "Singh", "kevin.singh@example.com", "studentpass", "student"),
    ("816012348", "Aaliyah", "Joseph", "aaliyah.joseph@example.com", "studentpass", "student"),
    ("816000001", "Jane", "Smith", "advisor@example.com", "advisorpass", "advisor"),
    ("admin", "Site", "Admin", "admin@example.com", "adminpass", "admin"),
]

DEGREE = "BSc Computer Science (Special)"

# (code, name, year, semester, is_core)
COURSES = [
    # Level 1 (Year 1)
    ("COMP 1600", "Introduction to Computing Concepts", 1, 1, True),
    ("COMP 1601", "Computer Programming I", 1, 1, True),
    ("INFO 1600", "Introduction to Information Technology Concepts", 1, 1, True),
    ("MATH 1115", "Fundamental Mathematics for the General Sciences I", 1, 1, True),
    ("COMP 1602", "Computer Programming II", 1, 2, True),
    ("COMP 1603", "Computer Programming III", 1, 2, True),
    ("COMP 1604", "Mathematics for Computing", 1, 2, True),
    ("INFO 1601", "Introduction to WWW Programming", 1, 2, True),

    # Level 2 (Year 2)
    ("COMP 2601", "Computer Architecture", 2, 1, True),
    ("COMP 2602", "Computer Networks", 2, 1, True),
    ("COMP 2605", "Enterprise Database Systems", 2, 1, True),
    ("COMP 2611", "Data Structures", 2, 1, True),
    ("MATH 2250", "Industrial Statistics", 2, 1, True),
    ("COMP 2603", "Object-Oriented Programming I", 2, 2, True),
    ("COMP 2604", "Operating Systems", 2, 2, True),
    ("COMP 2606", "Software Engineering I", 2, 2, True),
    ("INFO 2602", "Web Programming and Technologies I", 2, 2, True),
    ("INFO 2604", "Information Systems Security", 2, 2, True),

    # Level 3 (Year 3) - Core
    ("COMP 3602", "Theory of Computing", 3, 1, True),
    ("COMP 3603", "Human-Computer Interaction", 3, 1, True),
    ("COMP 3991", "Applied Mathematics for Scientific Computing", 3, 1, True),
    ("COMP 3601", "Design and Analysis of Algorithms", 3, 2, True),
    ("INFO 3604", "Project", 3, 2, True),

    # Level 3 (Year 3) - Electives
    ("COMP 3605", "Introduction to Data Analytics", 3, 1, False),
    ("COMP 3606", "Wireless and Mobile Computing", 3, 1, False),
    ("COMP 3607", "Object-Oriented Programming II", 3, 1, False),
    ("COMP 3613", "Software Engineering II", 3, 1, False),
    ("COMP 3608", "Intelligent Systems", 3, 2, False),
    ("COMP 3609", "Game Programming", 3, 2, False),
    ("COMP 3610", "Big Data Analytics", 3, 2, False),
]

# (university ID, gpa, has passed every course up to and including this year)
STUDENTS = [
    ("816012345", 3.67, 2),
    ("816012346", 2.85, 1),
    ("816012347", 3.20, 2),
    ("816012348", 1.95, 1),
]

# Plans already waiting for an advisor, for the current term. A plan's courses are not listed
# here: they are picked from what that student could really plan this term (their unpassed
# courses in the term's semester), so the seed follows CURRENT_TERM.
# (university ID, days since it was submitted, how many courses from the start of that list,
#  how many from the end of it (the Year 3 electives), comment from an earlier denial)
SUBMITTED_PLANS = [
    ("816012346", 5, 4, 0, None),
    ("816012347", 3, 3, 0, None),
    ("816012348", 1, 1, 2, "Finish your Year 2 core courses before taking Year 3 electives."),
]


def seed(session: Session) -> tuple[int, int]:
    """Insert the demo data. Safe to re-run. Returns users (created, skipped)."""
    users = UserRepository(session)
    created = skipped = 0
    for username, first_name, last_name, email, password, role in USERS:
        if users.get_by_username(username):
            skipped += 1
            continue
        users.create(UserBase(
            username=username,
            email=email,
            password=encrypt_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        ))
        created += 1

    # merge() upserts by primary key; flush parents before the rows that reference them.
    degree = session.merge(Degree(id=1, name=DEGREE))
    for code, name, *_ in COURSES:
        session.merge(Course(code=code, name=name))
    session.flush()

    for code, _, year, semester, is_core in COURSES:
        session.merge(DegreeCourse(
            degree_id=degree.id, course_code=code, is_core=is_core, year=year, semester=semester,
        ))
    for username, gpa, passed_years in STUDENTS:
        student_id = users.get_by_username(username).id
        session.merge(Student(id=student_id, degree_id=degree.id, gpa=gpa))
        session.flush()
        for code, _, year, *_ in COURSES:
            if year <= passed_years:
                session.merge(StudentPassedCourse(student_id=student_id, course_code=code))

    term = get_settings().current_term
    semester = int(term[-1])  # "2026-S1" -> 1
    passed_years = {username: years for username, _, years in STUDENTS}
    for username, days_ago, first, last, comment in SUBMITTED_PLANS:
        student_id = users.get_by_username(username).id
        if session.exec(select(Plan).where(Plan.student_id == student_id, Plan.year_semester == term)).first():
            continue
        plan = Plan(
            student_id=student_id, year_semester=term, status=STATUS_SUBMITTED, comment=comment,
            date_submitted=datetime.now() - timedelta(days=days_ago),
        )
        session.add(plan)
        session.flush()
        available = [
            code for code, _, year, course_semester, _ in COURSES
            if course_semester == semester and year > passed_years[username]
        ]
        codes = dict.fromkeys(available[:first] + available[len(available) - last:])
        session.add_all(PlanCourse(plan_id=plan.id, course_code=code) for code in codes)
    session.commit()
    return created, skipped
