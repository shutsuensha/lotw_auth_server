import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.core.deps import db
from app.core.security import create_access_token
from app.session_auth.models import SessionUser
from app.session_auth.schemas import SessionToken, TokenOut, UserPayloadJWT
from app.vk_auth.models import VkUser
from app.yandex_auth.models import YandexUser

logger = logging.getLogger()
router = APIRouter(prefix="/session/auth", tags=["session-auth"])


@router.post("/", response_model=TokenOut)
async def generate_jwt_token(session_token: SessionToken, db: db):
    session_id = session_token.session_id

    stmt = select(SessionUser).where(
        SessionUser.session_id == session_id,
        or_(
            SessionUser.vk_user_id.is_not(None),
            SessionUser.yandex_user_id.is_not(None),
        ),
    )
    result = await db.execute(stmt)
    session_user = result.scalar_one_or_none()

    if not session_user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Session Id - 404"
        )

    if session_user.vk_user_id:
        vk_user = await db.get(VkUser, session_user.vk_user_id)
        if vk_user.first_name is not None and vk_user.last_name is not None:
            if vk_user.first_name.strip() or vk_user.last_name.strip():
                possible_username = f"{vk_user.first_name} {vk_user.last_name}"
            else:
                possible_username = None
        else:
            possible_username = None
        possible_avatar = (
            vk_user.avatar if vk_user.avatar and vk_user.avatar.strip() else None
        )
        user_payload = UserPayloadJWT(
            user_id=vk_user.user_id,
            possible_username=possible_username,
            possible_avatar=possible_avatar,
        )

    if session_user.yandex_user_id:
        yandex_user = await db.get(YandexUser, session_user.yandex_user_id)
        possible_username = (
            yandex_user.real_name
            if yandex_user.real_name and yandex_user.real_name.strip()
            else None
        )
        possible_avatar = (
            f"https://avatars.mds.yandex.net/get-yapic/{yandex_user.default_avatar_id}/"
            if yandex_user.default_avatar_id is not None
            else None
        )
        user_payload = UserPayloadJWT(
            user_id=yandex_user.user_id,
            possible_username=possible_username,
            possible_avatar=possible_avatar,
        )

    access_token = create_access_token(user_payload.model_dump())

    return TokenOut(access_token=access_token, token_type="bearer")
