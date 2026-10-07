from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import AdvisorDep, SessionDep
from app.repositories.plan import PlanRepository
from app.repositories.student import StudentRepository
from app.services.plan_service import PlanError
from app.services.review_service import ReviewService
from app.utilities.flash import flash
from . import router, templates


@router.get("/submissions", response_class=HTMLResponse)
async def submissions_view(request: Request, user: AdvisorDep, db: SessionDep, q: str = ""):
    review_service = ReviewService(PlanRepository(db), StudentRepository(db))
    plans = review_service.get_pending(q)

    return templates.TemplateResponse(
        request=request,
        name="submissions.html",
        context={"user": user, "plans": plans, "q": q},
    )


@router.get("/submissions/{plan_id}", response_class=HTMLResponse)
async def submission_review(request: Request, plan_id: int, user: AdvisorDep, db: SessionDep):
    review_service = ReviewService(PlanRepository(db), StudentRepository(db))
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"user": user, **review_service.get_review(plan_id)},
    )


@router.post("/submissions/{plan_id}/approve")
async def submission_approve(request: Request, plan_id: int, user: AdvisorDep, db: SessionDep):
    try:
        review_service = ReviewService(PlanRepository(db), StudentRepository(db))
        review_service.approve(plan_id)
    except PlanError as e:
        flash(request, f"Error approving plan: {e}", "danger")
        return RedirectResponse(url=request.url_for("submissions_view"), status_code=status.HTTP_303_SEE_OTHER)

    flash(request, "Plan approved")
    return RedirectResponse(url=request.url_for("submissions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/submissions/{plan_id}/deny")
async def submission_deny(request: Request, plan_id: int, user: AdvisorDep, db: SessionDep, comment: str = Form("")):
    try:
        review_service = ReviewService(PlanRepository(db), StudentRepository(db))
        review_service.deny(plan_id, comment)
    except PlanError as e:
        flash(request, f"Error denying plan: {e}", "danger")
        return RedirectResponse(url=request.url_for("submissions_view"), status_code=status.HTTP_303_SEE_OTHER)

    flash(request, "Plan denied and returned to the student")
    return RedirectResponse(url=request.url_for("submissions_view"), status_code=status.HTTP_303_SEE_OTHER)
