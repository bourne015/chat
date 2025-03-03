from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
import requests
from bs4 import BeautifulSoup

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
        raise JSONResponse(status_code=200, content=["Error fetching data from Google API"])


@router.get("/fetch_webpage/")
async def fetch_webpage(url: str):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print("fetch: ", url)
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # clear HTML
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        # get text content
        text = soup.get_text(separator="\n", strip=True)
        # limit length
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + "...(内容已截断)"

        return JSONResponse(status_code=200, content=text)
    except Exception as e:
        JSONResponse(status_code=200, content=f"error:{str(e)}")