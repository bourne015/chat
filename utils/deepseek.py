from openai import AsyncOpenAI
import tiktoken
from retry import retry

from core.config import settings
from .credit import Credit
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class DeepSeek:
    '''
    wrapper DeepSeek api
    '''
    supported_models = [
        "deepseek-chat",
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = AsyncOpenAI(api_key=settings.deepseek_key, base_url="https://api.deepseek.com")
        self.credit = Credit()
        print("Chat init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    async def ask(self, user_id, question, model, stream = False):
        '''
        question without context
        '''
        if model not in self.supported_models:
            model = self.supported_models[0]

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            stream=stream
        )

        input_tokens = output_tokens = 0
        if getattr(response, 'usage', None):
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
        self.credit.from_tokens(
                user_id, model, input_tokens, output_tokens)
        return response.choices[0].message.content

    @retry(tries=3, delay=1, backoff=1)
    async def completions(self, user_id, chat_completion):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        model = chat_completion.model
        messages = chat_completion.messages
        tools = chat_completion.tools
        stream = True
        # if model not in self.supported_models:
        #     model = self.supported_models[1]

        input_tokens = output_tokens = 0
        response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools if tools else None,
                max_tokens=4096,
                stream_options={"include_usage": True},
                stream=stream
            )
        async for chunk in response:
            if getattr(chunk, 'usage', None):
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens
                break
            yield chunk.model_dump_json(exclude_unset=True)
        self.credit.from_tokens(user_id, model, input_tokens, output_tokens)
