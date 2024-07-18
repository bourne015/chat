import time
from utils import log

from api.deps import db_client
from .claude import Claude
from .gpt import GPT


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class Chat:
    '''
    wrapper gpt and claude api
    '''
    EXCH_RATE = 7.4
    PRICE = {
        # key: model, value: $ per 1M token
        "gpt-3.5-turbo-1106":   {"input": 1.0, "output": 2.0},
        "gpt-4-1106-preview":   {"input": 10.0, "output": 30.0},
        "gpt-4-turbo":          {"input": 10.0, "output": 30.0},
        "gpt-4-vision-preview": {"input": 10.0, "output": 30.0},
        "gpt-4o":               {"input": 5.0, "output": 15.0},
        "dall-e-3":             {"input": 10.0, "output": 30.0},
        "claude-3-haiku-20240307":  {"input": 0.25, "output": 1.25},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-opus-20240229":   {"input": 15.0, "output": 75.0},
        "claude-3-5-sonnet-20240620": {"input": 3.0, "output": 15.0},
    }

    def __init__(self) -> None:
        self.gpt = GPT()
        self.claude = Claude()

    def get_org(self, model):
        log.debug(f"get model org: {model}")
        if model in self.claude.supported_models:
            return self.claude
        return self.gpt

    def ask(self, prompt, model, stream = False):
        '''
        prompt without context
        '''
        org = self.get_org(model)
        res = org.ask(prompt, model, stream=stream)

        return res

    def asks(self, user_id, prompt_list, model, stream = True):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        org = self.get_org(model)
        if model in self.claude.supported_models and prompt_list and prompt_list[0]['role'] == "system":
            prompt_list[0]['role'] = "user"
            # there's no system role in Claude, use system paramater instead
            # don't use system prompt in this mement
            # system_prompt = prompt_list[0]['content'] 
        res = org.asks(user_id, prompt_list, model, stream=stream)

        return res

    def gen_image(self, user_id, prompt, model = 'dall-e-3'):
        res = self.gpt.gen_image(user_id, prompt=prompt, model=model)

        return res

    def token_consume(self, model, messages):
        msg_n = len(messages)
        log.debug(f"token consume msg_n: {msg_n}")
        org = self.get_org(model)
        input_token = org.num_tokens_from_messages(messages[:-1], model)
        output_token = org.num_tokens_from_messages(messages[-1:], model)
        log.debug(f"token input: {input_token}, output: {output_token}")
        return input_token, output_token

    def credit_balance(self, user_id, chat, is_new):
        userinfo = None
        try:
            model, messages = chat.model, chat.contents
            input_token, output_token = self.token_consume(model, messages)
            input_price = (input_token * self.PRICE[model]["input"] / 1000000) * self.EXCH_RATE
            output_price = (output_token * self.PRICE[model]["output"] / 1000000) * self.EXCH_RATE
            log.debug(f"price input: {input_price}, output: {output_price}")
            user = db_client.user.get_user_by_id(user_id)
            if user.credit is None:
                user.credit = 0
            new_credit = user.credit - input_price * 1.2 - output_price * 1.2
            if is_new and chat.assistant_id is not None:
                new_credit = new_credit - 0.22
            newdata = {
                "credit": new_credit,
                "updated_at": int(time.time())
            }
            userinfo = db_client.user.update_user_by_id(
                user_id,
                **newdata,
            )
        except Exception as err:
            log.debug(f"credit_balance error:{err}")
        return userinfo
