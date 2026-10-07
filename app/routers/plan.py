from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.config import get_settings
from app.dependencies import SessionDep, StudentDep
from app.repositories.plan import PlanRepository
from app.repositories.student import StudentRepository
from app.services.plan_service import PlanError, PlanService
from app.utilities.flash import flash
from . import router, templates


def _panels(request: Request, plan: dict):
    """The Planned / Remaining panels on their own, swapped into the page after each autosave.

    ``plan`` is what a PlanService method returns.
    """
    return templates.TemplateResponse(request=request, name="_plan_panels.html", context=plan)


@router.get("/plan", response_class=HTMLResponse)
async def plan_view(request: Request, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    return templates.TemplateResponse(
        request=request,
        name="plan.html",
        context={"user": user, **plan_service.get_plan(user.id)},
    )


@router.put("/plan/courses/{course_code}", response_class=HTMLResponse)
async def plan_add_course(request: Request, course_code: str, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    plan = plan_service.add_course(user.id, course_code)

    return _panels(request, {"user": user, **plan})


@router.delete("/plan/courses/{course_code}", response_class=HTMLResponse)
async def plan_remove_course(request: Request, course_code: str, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    plan = plan_service.remove_course(user.id, course_code)
    
    return _panels(request, {"user": user, **plan})


@router.delete("/plan/courses", response_class=HTMLResponse)
async def plan_reset(request: Request, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    plan = plan_service.reset(user.id)

    return _panels(request, {"user": user, **plan})


@router.post("/plan/submit", response_class=HTMLResponse)
async def plan_submit(request: Request, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    try:
        plan_service.submit(user.id)
    except PlanError as e:
        flash(request, f"Error submitting plan: {e}", "danger")
    return RedirectResponse(url=request.url_for("plan_view"), status_code=303)


@router.post("/plan/withdraw")
async def plan_withdraw(request: Request, user: StudentDep, db: SessionDep):
    plan_service = PlanService(PlanRepository(db), StudentRepository(db), get_settings().current_term)
    try:
        plan_service.withdraw(user.id)
    except PlanError as e:
        flash(request, f"Error removing submission: {e}", "danger")
    return RedirectResponse(url=request.url_for("plan_view"), status_code=303)
