from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_swagger_ui_html,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import app.core.logging  # noqa
from app.servers.routes import router as server_router
from app.session_auth.routes import router as session_auth_router
from app.vk_auth.routes import router as vk_auth_router
from app.yandex_auth.routes import router as yandex_auth_router

title = "Auth API"
version = "1.0.0"
description = """
:3
#### 📝 Author:
- 🐰 **Daniil Kupryianchyk**
"""


app = FastAPI(
    docs_url=None, redoc_url=None, title=title, description=description, version=version
)

app.mount("/static", StaticFiles(directory="app/core/static"), name="static")

app.include_router(session_auth_router)
app.include_router(vk_auth_router)
app.include_router(yandex_auth_router)
app.include_router(server_router)


@app.get("/health", include_in_schema=False)
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = "app/core/static/favicon.ico"
    return FileResponse(favicon_path)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title,
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/favicon.ico",
        swagger_ui_parameters={
            "displayRequestDuration": True,  # Показывать время выполнения запросов
            "deepLinking": True,  # Позволяет ссылаться на конкретные секции API
            "defaultModelsExpandDepth": -1,  # Скрыть секцию моделей внизу
            "filter": True,  # Включить поиск по API
            "showExtensions": True,  # Показывать дополнительные расширения API
            "showCommonExtensions": True,  # Показывать стандартные расширения API
            "persistAuthorization": True,  # Сохранять введенные токены авторизации при перезагрузке страницы
            "operationsSorter": "method",  # Сортировать эндпоинты по HTTP-методу (GET, POST и т.д.)
            "tryItOutEnabled": True,  # Разрешить редактирование запросов (Try it out)
        },
    )
