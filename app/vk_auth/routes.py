import base64
import hashlib
import logging
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select

from app.core.config import settings
from app.core.deps import db
from app.core.utils import generate_session_id
from app.session_auth.models import SessionUser
from app.vk_auth.models import VkUser
from app.vk_auth.schemas import VkUserIn, VkUserOut

logger = logging.getLogger()

router = APIRouter(prefix="/vk/auth", tags=["vk-auth"])


CLIENT_ID = settings.VK_CLIENT_ID
REDIRECT_URI = settings.VK_REDIRECT_URI
STATE = "secure_random_state_abc"

code_verifiers = {}


def generate_code_verifier():
    return (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    )


def generate_code_challenge(verifier: str):
    sha256 = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(sha256).rstrip(b"=").decode("ascii")


@router.get("/", include_in_schema=False)
async def vk_auth():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Сохраняем code_verifier по state
    code_verifiers[STATE] = code_verifier

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": STATE,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "scope": "openid email",
        "prompt": "consent",
        "lang_id": "ru",
        "scheme": "dark",
    }

    url = f"https://id.vk.com/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback", include_in_schema=False)
async def vk_callback(request: Request, db: db):
    query_params = request.query_params

    code = query_params.get("code")
    expires_in = query_params.get("expires_in")
    device_id = query_params.get("device_id")
    state = query_params.get("state")
    ext_id = query_params.get("ext_id")
    token_type = query_params.get("type")

    if not code or not state:
        raise HTTPException(
            status_code=400, detail="Missing 'code' or 'state' in query parameters"
        )

    # Получаем code_verifier по state
    code_verifier = code_verifiers.get(state)
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    # Обмениваем код на токены
    data = {
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "client_id": CLIENT_ID,
        "device_id": device_id,
        "state": state,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://id.vk.com/oauth2/auth", data=data, headers=headers
        )

    if resp.status_code != status.HTTP_200_OK:
        return JSONResponse(
            status_code=resp.status_code,
            content={"error": "Token request failed", "details": resp.text},
        )

    token_data = resp.json()

    code_verifiers.pop(state, None)

    id_token = token_data["id_token"]

    data = {
        "client_id": CLIENT_ID,
        "id_token": id_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://id.vk.com/oauth2/public_info", data=data, headers=headers
        )

    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=resp.status_code, detail=f"VK API error: {resp.text}"
        )

    data = resp.json()

    vk_user_in = VkUserIn(**data["user"])

    stmt = select(VkUser).where(VkUser.vk_id == vk_user_in.vk_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        await db.delete(existing_user)
        await db.flush()

    vk_user = VkUser(**vk_user_in.model_dump())
    db.add(vk_user)
    await db.flush()

    session_user = SessionUser(session_id=generate_session_id(), vk_user_id=vk_user.id)
    db.add(session_user)

    await db.commit()

    return {
        "success": True,
        "message": "New user created",
        "session_id": session_user.session_id,
    }


@router.get("/list", response_model=list[VkUserOut])
async def list_vk_users(db: db):
    result = await db.execute(select(VkUser))
    return result.scalars().all()


@router.get("/{vk_user_id}", response_model=VkUserOut)
async def get_vk_user(vk_user_id: int, db: db):
    result = await db.get(VkUser, vk_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="vk_user_id not found")
    return result


@router.delete("/{vk_user_id}")
async def delete_vk_user(vk_user_id: int, db: db):
    server = await db.get(VkUser, vk_user_id)
    if not server:
        raise HTTPException(status_code=404, detail="vk_user_id not found")

    await db.delete(server)
    await db.commit()
    return {"Deleted": True}
