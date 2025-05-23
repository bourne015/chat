import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import assistant, log
from api.deps import db_client
from core.security import *

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class McpServer(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    command: Optional[str] = None
    args: Optional[str] = None
    isActive: Optional[bool] = None
    custom_environment: Optional[Dict[str, str]] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


@router.post("/mcp", name="add mcp server config")
async def mcp_new(mcp: McpServer, current_user = Depends(get_current_user)) -> Any:
    newmcp = None
    try:
        mcp_data = mcp.dict()
        updated_at = int(time.time())
        mcp_data["owner_id"] = current_user.id
        mcp_data["owner_name"] = current_user.name
        mcp_data["created_at"] = updated_at
        mcp_data["updated_at"] = updated_at
        newmcp = db_client.mcp.add_new_mcp(
            **mcp_data
        )
        update_shares(updated_at)
    except Exception as err:
        log.debug(f"add mcp error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content=newmcp)


@router.get("/mcps", name="get all mcp servers config")
async def mcp_all(current_user = Depends(get_current_user)) -> Any:
    mcps = []
    shares = None
    try:
        _data = db_client.mcp.get_all_mcps()
        for m in _data:
            if m.owner_id == current_user.id or m.is_public:
                mcps.append(m)
        shares = db_client.shares.get_all_shares()
    except Exception as err:
        log.debug(f"get mcps error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(
        status_code=200,
        content={"mcps": mcps, "date": shares.get("mcp_updated")})


@router.get("/mcp/{mcp_id}", name="get mcp info")
async def mcp_info(mcp_id: str) -> Any:
    mcp = None
    try:
        mcp = db_client.mcp.get_mcp_by_id(mcp_id)
    except Exception as err:
        return JSONResponse(status_code=500, content={"result": str(err)})
    if mcp is None:
        log.debug(f"mcp:{mcp_id} not found")
        return JSONResponse(status_code=200, content={"result": "mcp not found"})
    return JSONResponse(status_code=200, content=mcp)



@router.post("/mcp/{mcp_id}", name="edit mcp server")
async def mcp_edit(mcp_id: str, mcp: McpServer) -> Any:
    new_data = mcp.dict()
    try:
        new_data["updated_at"] = int(time.time())
        new_data = db_client.mcp.update_mcp_by_id(
            mcp_id,
            **new_data,
        )
        update_shares(new_data["updated_at"])
    except Exception as err:
        log.debug(f"edit mcp error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content=new_data)


@router.delete("/mcp/{mcp_id}", name="delete mcp server")
async def mcp_delete(mcp_id: str) -> Any:
    try:
        db_client.mcp.delete_mcp(mcp_id=mcp_id)
        update_shares(int(time.time()))
    except Exception as err:
        log.debug(f"delete mcp error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})

def update_shares(updated_at):
    try:
        shared = db_client.shares.get_all_shares()
        if shared:
            db_client.shares.update_shares_by_id(
                shared["id"],
                mcp_updated=updated_at)
    except Exception as err:
        log.debug(f"update_shared error:{err}")

