import logging

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.config import settings
from app.core.deps import db
from app.core.templating import templates
from app.core.utils import generate_session_id
from app.session_auth.models import SessionUser
from app.yandex_auth.models import YandexUser
from app.yandex_auth.schemas import YandexUserIn, YandexUserOut

logger = logging.getLogger()

router = APIRouter(prefix="/yandex/auth", tags=["yandex-auth"])

YANDEX_INFO_URL = "https://login.yandex.ru/info"

CLIENT_ID = settings.YANDEX_CLIENT_ID


@router.get("/", include_in_schema=False)
async def yandex_auth():
    url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={CLIENT_ID}"
    return RedirectResponse(url)


@router.get("/callback", response_class=HTMLResponse, include_in_schema=False)
async def yandex_callback(request: Request):
    return templates.TemplateResponse("yandex_auth.html", {"request": request})


@router.get("/token", include_in_schema=False)
async def yandex_token(
    db: db, access_token: str, format: str = "json", jwt_secret: str | None = None
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
        data = resp.json()
    else:
        data = resp.text

    yandex_user_in = YandexUserIn(**data)

    stmt = select(YandexUser).where(YandexUser.yandex_id == yandex_user_in.yandex_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        await db.delete(existing_user)
        await db.flush()

    yandex_user = YandexUser(**yandex_user_in.model_dump())
    db.add(yandex_user)
    await db.flush()

    session_user = SessionUser(
        session_id=generate_session_id(), yandex_user_id=yandex_user.id
    )
    db.add(session_user)

    await db.commit()

    return {
        "success": True,
        "message": "New user created",
        "session_id": session_user.session_id,
    }


@router.get("/list", response_model=list[YandexUserOut])
async def list_yandex_users(db: db):
    result = await db.execute(select(YandexUser))
    return result.scalars().all()


@router.get("/{yandex_user_id}", response_model=YandexUserOut)
async def get_yandex_user(yandex_user_id: int, db: db):
    result = await db.get(YandexUser, yandex_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="yandex_user_id not found")
    return result


@router.delete("/{yandex_user_id}")
async def delete_yandex_user(yandex_user_id: int, db: db):
    server = await db.get(YandexUser, yandex_user_id)
    if not server:
        raise HTTPException(status_code=404, detail="yandex_user_id not found")

    await db.delete(server)
    await db.commit()
    return {"Deleted": True}
