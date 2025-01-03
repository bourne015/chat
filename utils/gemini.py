import google.generativeai as genai
from retry import retry

from core.config import settings

class Gemini:
    def __init__(self):
        genai.configure(api_key=settings.gemini_key)
        self.client = genai.GenerativeModel("gemini-1.5-flash")

    @retry(tries=3, delay=1, backoff=1)
    def completions(self, user_id, chat_completion):
        model = chat_completion.model
        messages = chat_completion.messages
        response = self.client.generateContent(
            tools=messages,

        )
        for chunk in response:
            yield chunk
        