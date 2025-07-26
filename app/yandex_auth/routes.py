import logging

from fastapi import APIRouter

logger = logging.getLogger()

router = APIRouter(prefix="/yandex/auth", tags=["vk-auth"])

