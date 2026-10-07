from fastapi import Request, status
from fastapi.responses import RedirectResponse

from . import router


# No public landing: login_view sends a signed-in user on to their role page.
@router.get("/", name="index_view")
async def index_view(request: Request):
    return RedirectResponse(
        url=request.url_for("login_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
