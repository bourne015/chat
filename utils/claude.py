import anthropic
from retry import retry

from core import settings
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class Claude:
    '''
    wrapper claude api
    '''
    supported_models = [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = anthropic.Anthropic(api_key=settings.claude_key)
        print("claude init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    def ask(self, prompt, model, stream = False):
        '''
        question without context
        '''
        if model not in self.supported_models:
            model = self.supported_models[0]

        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            stream=stream
        )

        return response.content[0].text

    @retry(tries=3, delay=1, backoff=1)
    def asks(self, prompt_list, model, stream = True):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        if model not in self.supported_models:
            model = self.supported_models[1]

        with self.client.messages.stream(
            model=model,
            messages=prompt_list,
            max_tokens=4096,
        ) as stream:
            for text in stream.text_stream:
                yield text
