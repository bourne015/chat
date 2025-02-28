from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
import requests

from utils import log
from core.config import settings


router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


@router.get("/google_search/")
async def search_google(query: str, num_results: int = 10):
    endpoint = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': query,
        'num': num_results,
        'key': settings.google_search_key,
        'cx': settings.google_search_cx,
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        json_response = response.json()
        results = json_response.get('items', [])

        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result.get('title'),
                'link': result.get('link'),
                'snippet': result.get('snippet')
            })
        # return {"results": formatted_results}
        return JSONResponse(status_code=200, content=formatted_results)
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Google API")
