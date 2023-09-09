import openai
from retry import retry

from core import settings


class Chat:
    '''
    wrapper openai api
    '''
    supported_models = [
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0613"
    ]

    def __init__(self) -> None:
        #self.chat_list = []
        self.model = self.supported_models[0]
        openai.api_key = settings.openai_key
        print("Chat init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    def ask(self, prompt_list, model, stream = False):
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
    def asks(self, prompt_list, model, stream = False):
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

'''
    def ask(self, prompt: str) -> str:
        self.chat_list.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.chat_list
        )
        answer = response.choices[0].message['content']
        self.chat_list.append(
            {"role": "assistant", "content": answer}
        )
        print("chat len:", len(self.chat_list))
        return answer
'''

