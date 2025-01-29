import time
from api.deps import db_client
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class Credit:
    EXCH_RATE = 7.4
    PRICE = {
        # key: model, value: $ per 1M token
        "gpt-3.5-turbo-1106":   {"input": 1.0, "output": 2.0},
        "gpt-4-1106-preview":   {"input": 10.0, "output": 30.0},
        "gpt-4-turbo":          {"input": 10.0, "output": 30.0},
        "gpt-4-vision-preview": {"input": 10.0, "output": 30.0},
        "gpt-4o":               {"input": 2.50, "output": 10.0},
        "gpt-4o-mini":          {"input": 0.15, "output": 0.6},
        "o1":                   {"input": 15.0, "output": 60.0},
        "o1-mini":              {"input": 3.00, "output": 12.0},
        "dall-e-3":             {"input": 10.0, "output": 30.0},
        "claude-3-haiku-20240307":    {"input": 0.25, "output": 1.25},
        "claude-3-5-haiku-20241022":  {"input": 0.8, "output": 4.0},
        "claude-3-sonnet-20240229":   {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20240620": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-opus-20240229":     {"input": 15.0, "output": 75.0},
        "deepseek-chat":              {"input": 0.27, "output": 1.10},
        "deepseek-reasoner":          {"input": 0.55, "output": 2.19},
        "gemini-1.5-pro":             {"input": 0.10, "output": 0.10}, # free
        "gemini-2.0-flash-exp":       {"input": 0.10, "output": 0.10}, # free
    }
    defalt_price = {"input": 10.0, "output": 30.0}

    def from_tokens(self, user_id, model, input_tokens, output_tokens):
        """
        """
        userinfo = None
        try:
            user = db_client.user.get_user_by_id(user_id)
            if user.credit is None:
                user.credit = 0
            price = self.PRICE.get(model, self.defalt_price)
            input_cost = self.EXCH_RATE * (input_tokens * price["input"])/1000000
            output_cost = self.EXCH_RATE * (output_tokens * price["output"])/1000000
            new_credit = user.credit - input_cost * 1.2 - output_cost * 1.2
            newdata = {
                "credit": new_credit,
                "updated_at": int(time.time())
            }
            userinfo = db_client.user.update_user_by_id(
                user_id,
                **newdata,
            )
            #log.debug(f"***from_tokens: model: {model}, {price}")
            log.debug(f"***from_tokens: {input_tokens}, {output_tokens}")
            #log.debug(f"***from_tokens: {user.credit}, {new_credit}")
        except Exception as err:
            log.debug(f"from_tokens error:{err}")
        return userinfo
    
    def from_costs(self, user_id, cost):
        """
        cost unit: $
        """
        userinfo = None
        try:
            user = db_client.user.get_user_by_id(user_id)
            if user.credit is None:
                user.credit = 0
            new_credit = user.credit - self.EXCH_RATE * cost
            newdata = {
                "credit": new_credit,
                "updated_at": int(time.time())
            }
            userinfo = db_client.user.update_user_by_id(
                user_id,
                **newdata,
            )
            log.debug(f"***from_costs: {user.credit}, {new_credit}")
        except Exception as err:
            log.debug(f"from_costs error:{err}")
        return userinfo
