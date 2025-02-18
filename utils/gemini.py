from google import genai
from google.genai import types
from retry import retry
import httpx
import base64
import os
import io
import json

from core.config import settings


class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_key)
        print("Gemini init")

    @retry(tries=3, delay=1, backoff=1)
    async def ask(self, user_id, question, model, stream = False):
        '''
        chat without context
        '''
        chat = self.client.aio.chats.create(model=model)
        response = await chat.send_message(question)
        return response.text

    @retry(tries=3, delay=1, backoff=1)
    async def completions(self, user_id, chat_completion):
        model = chat_completion.model
        messages = chat_completion.messages
        g_config = {'thinking_config': {'include_thoughts': True}}

        for msg in messages:
            if not isinstance(msg['parts'], list):
                continue
            for i, _pt in enumerate(msg['parts']):
                if "inline_data" in _pt and _pt['inline_data']['data'].startswith('http'):
                    image = httpx.get(_pt['inline_data']['data'])
                    # _pt['inline_data']['data'] = base64.standard_b64encode(image.content).decode('utf-8')
                    msg['parts'][i] = types.Part.from_bytes(image.content, _pt['inline_data']['mime_type'])
                if "file_data" in _pt:
                    file_url = _pt["file_data"]["file_uri"]
                    doc_data = io.BytesIO(httpx.get(file_url).content)
                    myfile = await self.client.aio.files.upload(
                        path=doc_data,
                        config=dict(mime_type=_pt["file_data"]["mime_type"])
                    )
                    _pt['file_data']['file_uri'] = myfile.uri
        # history_chats = messages[:-1]
        # chat = self.client.aio.chats.create(
        #     model=model,
        #     history=history_chats,
        # )
        # response = chat.send_message_stream(
        #     # self.claude2gemini(messages[-1]),
        #     messages[-1],
        # )
        response = self.client.aio.models.generate_content_stream(
            model=model,
            contents=messages,
        )
        async for chunk in response:
            yield chunk.model_dump_json(exclude_unset=True)

    def claude2gemini(self, msg):
        '''
        transfer claude data schema to gemini schema
        '''
        t = {}
        t['role'] = 'model' if msg['role'] == 'assistant' else msg['role']
        if not isinstance(msg['content'], list):
            t['parts'] = msg['content']
        else:
            t['parts'] = []
            for _c in msg['content']:
                if _c["type"] == "text":
                    t["parts"].append({"text": _c["text"]})
                elif _c["type"] == "image":
                    img_url = _c["source"]["data"]
                    img_data = base64.standard_b64encode(httpx.get(img_url).content).decode("utf-8")
                    t["parts"].append({
                        "inline_data": {
                        "mime_type": _c["source"]["media_type"],
                        "data": img_data}
                    })
                elif _c["type"] == "document":
                    pdf_url = _c["source"]["data"]
                    pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")
                    t["parts"].append({
                        "inline_data": {
                        "mime_type": "application/pdf",
                        "data": pdf_data
                        }
                    })
        return t
