import google.generativeai as genai
from retry import retry
import httpx
import base64

from core.config import settings

class Gemini:
    def __init__(self):
        genai.configure(api_key=settings.gemini_key)
        self.client = genai.GenerativeModel("gemini-1.5-flash")

    @retry(tries=3, delay=1, backoff=1)
    def completions(self, user_id, chat_completion):
        model = chat_completion.model
        messages = chat_completion.messages
        history_chats = []
        self.client = genai.GenerativeModel(model)
        for msg in messages[:-1]:
            t = self.claude2gemini(msg)
            history_chats.append(t)

        chat = self.client.start_chat(
            history=history_chats,
        )
        response = chat.send_message(
            self.claude2gemini(messages[-1]),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
            stream=True,
        )
        for chunk in response:
            yield chunk.text


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
