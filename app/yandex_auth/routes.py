import logging

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.core.config import settings
from app.core.templating import templates

logger = logging.getLogger()

router = APIRouter(prefix="/yandex/auth", tags=["yandex-auth"], include_in_schema=False)

YANDEX_INFO_URL = "https://login.yandex.ru/info"

CLIENT_ID = settings.YANDEX_CLIENT_ID


@router.get("/")
async def yandex_auth():
    url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={CLIENT_ID}"
    return RedirectResponse(url)


@router.get("/callback", response_class=HTMLResponse)
async def yandex_callback(request: Request):
    return templates.TemplateResponse("yandex_auth.html", {"request": request})


@router.get("/token")
async def yandex_token(
    access_token: str, format: str = "json", jwt_secret: str | None = None
):
    headers = {"Authorization": f"OAuth {access_token}"}

    params = {"format": format}
    if jwt_secret:
        params["jwt_secret"] = jwt_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(YANDEX_INFO_URL, headers=headers, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"Yandex API returned error: {exc.response.status_code} {exc.response.text}"
            )

        except Exception as exc:
            logger.error(f"Ошибка запроса к Yandex API: {exc}")

    if format == "json":
        return JSONResponse(content=resp.json())
    else:
        return resp.text
