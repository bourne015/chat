from openai import OpenAI
from retry import retry

from core import settings
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class GPT:
    '''
    wrapper openai api
    '''
    supported_models = [
            "gpt-3.5-turbo-1106",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "dall-e-3"
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = OpenAI(api_key=settings.openai_key)
        print("Chat init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    def ask(self, question, model, stream = False):
        '''
        question without context
        '''
        if model not in self.supported_models:
            model = self.supported_models[0]

        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            stream=stream
        )

        return response

    @retry(tries=3, delay=1, backoff=1)
    def asks(self, prompt_list, model, stream = True):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        if model not in self.supported_models:
            model = self.supported_models[1]

        response = self.client.chat.completions.create(
            model=model,
            messages=prompt_list,
            max_tokens=4096,
            stream=stream
        )
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            yield chunk_message

    def gen_image(self, prompt, model = 'dall-e-3'):
        """
        generate image
        """
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format='b64_json',
            n=1,
            )

        return response
