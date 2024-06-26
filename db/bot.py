from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import Bot


class BotDBConnectorComponent(DBConnectorComponent):
    '''
    bot component which is used to manager all bot db interface
    '''
    tbl = Bot

    def get_all_bots(self):
        def thd(conn):
            try:
                bots = conn.query(self.tbl).all()
            except Exception as err:
                print(f"get all bots err: {err}")
            return [bot.to_dict() for bot in bots]
        d = self.db.execute(thd)
        return d

    def get_bot_by_author_id(self, author_id):
        def thd(conn):
            try:
                bots = conn.query(self.tbl).filter(
                    self.tbl.author_id == author_id).all()
            except Exception as err:
                print(f"get bot err: {err}")
            return [bot.to_dict() for bot in bots]
        d = self.db.execute(thd)
        return d

    def get_bot_by_id(self, bot_id):
        def thd(conn):
            bot = conn.query(self.tbl).filter(
                self.tbl.id == bot_id).first()
            return bot.to_dict() if bot else None
        d = self.db.execute(thd)
        return d

    def add_new_bot(self, **kwargs):
        def thd(conn):
            try:
                if kwargs.get("name", None) is None:
                    raise ValueError("name is required field")
                if kwargs.get("prompts", None) is None:
                    raise ValueError("prompts is required field")
                bot = self.tbl(
                    name=kwargs.get("name", None),
                    avatar=kwargs.get("avatar"),
                    description=kwargs.get("description", None),
                    prompts=kwargs.get("prompts", None),
                    author_id=kwargs.get("author_id", None),
                    author_name=kwargs.get("author_name", None),
                    likes=kwargs.get("likes", 0),
                    public=kwargs.get("public", True),
                    created_at=kwargs.get("created_at"),
                    updated_at=kwargs.get("updated_at"),
                )
                conn.add(bot)
                conn.commit()
            except Exception as err:
                print("err:", err)
            return bot.id
        d = self.db.execute(thd)
        return d

    def update_bot_by_id(self, bot_id, **kwargs):
        def thd(conn):
            update_columns = [
                "name", "avatar", "description", "prompts", "author_id",
                "author_name", "likes", "public", "updated_at"
            ]
            bot = conn.query(self.tbl).filter(
                self.tbl.id == bot_id).first()
            for col in update_columns:
                val = kwargs.get(col, None)
                if val is not None:
                    setattr(bot, col, val)
                    flag_modified(bot, col)
            conn.commit()
            return bot.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_bot(self, bot_id):
        def thd(conn):
            try:
                result = conn.query(self.tbl).filter(
                    self.tbl.id == bot_id).delete()
                conn.commit()
            except Exception as err:
                print("delete bot error: ", err)
            return result
        d = self.db.execute(thd)
        return d
