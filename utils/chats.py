from utils import log

from .claude import Claude
from .gpt import GPT


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class Chat:
    '''
    wrapper gpt and claude api
    '''
    def __init__(self) -> None:
        self.gpt = GPT()
        self.claude = Claude()

    def ask(self, prompt, model, stream = False):
        '''
        prompt without context
        '''
        if model in self.claude.supported_models:
            org = self.claude
        else:
            org = self.gpt
        res = org.ask(prompt, model, stream=stream)

        return res

    def asks(self, prompt_list, model, stream = True):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        if model in self.claude.supported_models:
            org = self.claude
        else:
            org = self.gpt
        res = org.asks(prompt_list, model, stream=stream)

        return res

    def gen_image(self, prompt, model = 'dall-e-3'):
        res = self.gpt.gen_image(prompt=prompt, model=model)

        return res

