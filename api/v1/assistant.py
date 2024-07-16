import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import os
import time

from utils import assistant, log
from api.deps import db_client

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)
UPLOAD_DIR = './uploads'

class NewVectorStore(BaseModel):
    vs_name: Optional[str] = None
    files: List # files name list

class NewAssistant(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = "you are a helpful assistant"
    assistant_id: Optional[str] = None
    model: Optional[str] = None
    file_search: Optional[bool] = False
    vector_store_ids: Optional[dict] = {}
    code_interpreter: Optional[bool] = False
    code_interpreter_files: Optional[dict]  = {}
    functions: Optional[dict] = {}
    temperature: Optional[float] = 1.0

class NewMessage(BaseModel):
    role: str
    content: str|list
    instructions: Optional[str] = None
    attachments: Optional[list] = None


@router.post("/files", name="uoload client file")
async def get_client_file(file: UploadFile = File(...)) -> Any:
    """
    receive a file from client and save in this server
    """
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as err:
        log.debug(f"upload_file error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(content={"filename": file.filename}, status_code=200)


# @router.post("/assistant", name="create assistant")
# async def create_assistant() -> Any:
#     """
#     create assistant
#     """
#     new_assistant = None
#     try:
#         deletedfile = assistant.create_assistant(file_id)
#     except Exception as err:
#         log.debug(f"delete file in openai error:{err}")
#         return JSONResponse(status_code=500, content={"result": str(err)})      
#     return JSONResponse(content=deletedfile, status_code=200)


@router.post("/assistant/files", name="upload file")
async def openai_file(file_name: str) -> Any:
    """
    upload a file to openai
    """
    res = {}
    newfile = None
    try:
        newfile = assistant.file_upload(file_name)
        if newfile:
            res["id"] = newfile.id
            res["filename"] = newfile.filename
            res["bytes"] = newfile.bytes
            res["created_at"] = newfile.created_at
    except Exception as err:
        log.debug(f"upload file to openai error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(content=res, status_code=200)


@router.delete("/assistant/files/{file_id}", name="delete file")
async def openai_file(file_id: str) -> Any:
    """
    delete a file in openai
    """
    deletedfile = None
    try:
        deletedfile = assistant.file_delete(file_id)
    except Exception as err:
        log.debug(f"delete file in openai error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})      
    return JSONResponse(content=deletedfile, status_code=200)


@router.get("/assistant/files/{file_id}", name="download file")
async def download_file(file_id: str, file_name: str) -> Any:
    status = None
    try:
        status = await assistant.file_download(file_id, file_name)
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=file_name)
    except Exception as err:
        log.debug(f"download file error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=500, content={"result": status})


@router.post("/assistant/vs", name="create vector store")
async def create_vs(vs: NewVectorStore) -> Any:
    """
    create opanai vector store with uploaded files
        note: files should be uploaded to backend first
        paramater
    """
    vector_store_id = None
    try:
        vector_store_id = assistant.create_vs_with_files(vs.vs_name, vs.files)
        if vector_store_id is None:
            return JSONResponse(status_code=500, content={"result": "failed"})
    except Exception as err:
        og.debug(f"create vector store error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content={"vs_id": vector_store_id}, status_code=200)


@router.delete("/assistant/vs/{vector_store_id}", name="delete vector store")
async def delete_vs(vector_store_id: str) -> Any:
    """
    delete vector store
    """
    vs_del = None
    try:
        vs_del = assistant.vs_delete(vector_store_id)
        if vs_del is None:
            return JSONResponse(status_code=500, content={"result": "failed"})
    except Exception as err:
        log.debug(f"delete vector store error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content=vs_del, status_code=200)


@router.post("/assistant/vs/{vector_store_id}/files", name="create vector store file")
async def create_vs_file(vector_store_id: str, file_name: str) -> Any:
    """
    Create a vector store file by attaching a File to a vector store.
        1.upload a file to openai
        2.create it in vector store
    """
    new_vsfile = None
    res = {}
    try:
        new_vsfile = assistant.vs_upload_file(vector_store_id, file_name)
        if new_vsfile is not None:
            res["id"] = new_vsfile.id
            res["created_at"] = new_vsfile.created_at
    except Exception as err:
        log.debug(f"vs create file error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content=res, status_code=200)


@router.get("/assistant/vs/{vector_store_id}/files", name="list vector store files")
async def get_vector_store_files(vector_store_id: str) -> Any:
    """
    list vector store files
    """
    try:
        vs_file = assistant.vector_store_files(vector_store_id)
    except Exception as err:
        log.debug(f"vector_store_files error:{err}")
        return JSONResponse(content={"result": err}, status_code=200)
    return JSONResponse(content={"files": vs_file}, status_code=200)


@router.delete("/assistant/vs/{vector_store_id}/files/{file_id}", name="create vector store file")
async def create_vs_file(vector_store_id: str, file_id: str) -> Any:
    """
    upload a file to openai and then create it in vector store
    """
    del_vsfile = None
    try:
        del_vsfile = assistant.vs_delete_file(vector_store_id, file_id)
    except Exception as err:
        log.debug(f"vs delete file error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content=del_vsfile, status_code=200)


@router.post("/assistant/threads", name="create thread")
async def create_thread() -> Any:
    """
    Create threads that assistants can interact with.
    """
    thread_id = None
    try:
        thread_id = assistant.create_thread()
    except Exception as err:
        log.debug(f"create_thread error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content={"id": thread_id}, status_code=200)


@router.delete("/assistant/threads/{thread_id}", name="create thread")
async def delete_thread(thread_id: str) -> Any:
    """
    delete a threads
    """
    try:
        del_status = assistant.delete_thread(thread_id)
    except Exception as err:
        log.debug(f"delete_thread error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)}) 
    return JSONResponse(content={"deleted": del_status}, status_code=200)


@router.post(
    "/assistant/vs/{assistant_id}/threads/{thread_id}/messages",
    name="create message")
async def create_message(
        assistant_id: str,
        thread_id: str,
        msg: NewMessage) -> Any:
    """
    Create messages within threads
    """
    for x in msg.attachments:
        x.pop("downloading", None)
    log.debug(f"toassistantr: {msg}")
    assistant.add_thread_message(
        thread_id,
        msg.role,
        msg.content,
        msg.attachments)
    async def event_generator():
        try:
            messages = assistant.runs(assistant_id, thread_id, msg.instructions)
            for text in messages:
                yield text
        except Exception as err:
            log.debug(err)
            yield err
    return EventSourceResponse(event_generator())
