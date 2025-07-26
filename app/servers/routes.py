from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import db
from app.servers.models import Server
from app.servers.schemas import ServerIn, ServerOptionalIn, ServerOut

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("/", response_model=ServerOut)
async def create_server(server_in: ServerIn, db: db):
    server = Server(**server_in.model_dump())
    db.add(server)
    await db.commit()
    await db.refresh(server)
    return server


@router.get("/", response_model=list[ServerOut])
async def list_servers(db: db):
    result = await db.execute(select(Server))
    return result.scalars().all()


@router.get("/{server_id}", response_model=ServerOut)
async def get_server(server_id: int, db: db):
    result = await db.get(Server, server_id)
    if not result:
        raise HTTPException(status_code=404, detail="Server not found")
    return result


@router.put("/{server_id}", response_model=ServerOut)
async def update_server(
    server_id: int,
    server_in: ServerIn,
    db: db,
):
    server = await db.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    for field, value in server_in.model_dump().items():
        setattr(server, field, value)

    await db.commit()
    await db.refresh(server)
    return server


@router.patch("/{server_id}", response_model=ServerOut)
async def update_server_optional(
    server_id: int,
    server_in: ServerOptionalIn,
    db: db,
):
    server = await db.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    for field, value in server_in.model_dump(exclude_unset=True).items():
        setattr(server, field, value)

    await db.commit()
    await db.refresh(server)
    return server


@router.delete("/{server_id}")
async def delete_server(server_id: int, db: db):
    server = await db.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    await db.delete(server)
    await db.commit()
    return {"Deleted": True}
