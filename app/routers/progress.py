from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies import SessionDep, StudentDep
from app.repositories.student import StudentRepository
from app.services.progress_service import ProgressService
from . import router, templates

@router.get("/progress", response_class=HTMLResponse)
async def progress_view(request: Request, user: StudentDep, db: SessionDep):
    studentRepo = StudentRepository(db)
    progressService = ProgressService(studentRepo)
    progress = progressService.get_progress(user.id)

    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context={"user": user, "progress": progress},
    )
