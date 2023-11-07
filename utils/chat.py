import openai
from retry import retry

from core import settings


class Chat:
    '''
    wrapper openai api
    '''
    supported_models = [
            "gpt-3.5-turbo-1106",
            "gpt-4-1106-preview"
    ]

    def __init__(self) -> None:
        #self.chat_list = []
        self.model = self.supported_models[0]
        openai.api_key = settings.openai_key
        print("Chat init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    def ask(
            self,
            question,
            model = "gpt-3.5-turbo-16k",
            stream = False):
        '''
        question without context
        '''
        if model == "gpt35":
            self.model = self.supported_models[0]
        elif model == 'gpt40':
            self.model = self.supported_models[1]

        res = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": question}],
            request_timeout=15,
            stream=stream
        )

        return res

    @retry(tries=3, delay=1, backoff=1)
    def asks(
            self,
            prompt_list,
            model = "gpt-3.5-turbo-16k",
            stream = False):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        if model == "gpt35":
            self.model = self.supported_models[0]
        elif model == 'gpt40':
            self.model = self.supported_models[1]

        res = openai.ChatCompletion.create(
            model=self.model,
            messages=prompt_list,
            request_timeout=15,
            stream=stream
        )

        return res

