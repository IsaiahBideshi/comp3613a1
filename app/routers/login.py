from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form
from app.dependencies import SessionDep, IsUserLoggedIn
from app.dependencies.auth import get_current_user
from . import router, templates, ROLE_HOME
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.utilities.security import access_token_cookie_kwargs


@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request, user_logged_in: IsUserLoggedIn, db: SessionDep):
    if user_logged_in:
        user = await get_current_user(request, db)
        if user.role in ROLE_HOME:
            return RedirectResponse(
                url=request.url_for(ROLE_HOME[user.role]),
                status_code=status.HTTP_303_SEE_OTHER,
            )
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@router.post("/login", response_class=HTMLResponse)
async def login_action_ajax(
    db: SessionDep,
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    access_token = auth_service.authenticate_user(username, password)
    dest = ROLE_HOME.get(user_repo.get_by_username(username).role) if access_token else None
    if not dest:
        message = "This account has no student or advisor role" if access_token else "Incorrect ID or password"
        flash(request, message, "danger")
        return RedirectResponse(
            url=request.url_for("login_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    response = RedirectResponse(
        url=request.url_for(dest),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        **access_token_cookie_kwargs(),
    )
    return response
