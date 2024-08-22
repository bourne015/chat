from sqlalchemy.orm.attributes import flag_modified
from db.base import DBConnectorComponent
from db.model import Chat


class ChatDBConnectorComponent(DBConnectorComponent):
    '''
    Chat component which is used to manager all Chat db interface
    '''
    tbl = Chat

    def get_chat_by_user_id(self, user_id):
        def thd(conn):
            try:
                chats = conn.query(self.tbl).filter(
                    self.tbl.user_id == user_id).order_by(self.tbl.updated_at.desc()).all()
            except Exception as err:
                print(f"get chats err: {err}")
            return [chat.to_dict() for chat in chats]
        d = self.db.execute(thd)
        return d

    def get_chat_by_id(self, chat_id):
        def thd(conn):
            chat = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).first()
            return chat.to_dict() if chat else None
        d = self.db.execute(thd)
        return d

    def add_new_chat(self, **kwargs):
        def thd(conn):
            try:
                if kwargs.get("user_id", None) is None:
                    raise ValueError("user_id is required field")
                chat = self.tbl(
                    user_id=kwargs.get("user_id"),
                    page_id=kwargs.get("page_id"),
                    title=kwargs.get("title", "0"),
                    contents=kwargs.get("contents"),
                    model=kwargs.get("model"),
                    created_at=kwargs.get("created_at"),
                    updated_at=kwargs.get("updated_at"),
                    assistant_id=kwargs.get("assistant_id"),
                    thread_id=kwargs.get("thread_id"),
                    bot_id=kwargs.get("bot_id"),
                    artifact=kwargs.get("artifact", False),
                )
                conn.add(chat)
                conn.commit()
            except Exception as err:
                print("add chat err: ", err)
            return chat.id
        d = self.db.execute(thd)
        return d

    def update_chat_by_id(self, chat_id, **kwargs):
        def thd(conn):
            update_columns = [
                "title", "contents", "model", "created_at", "updated_at",
                "page_id", "assistant_id", "thread_id", "bot_id", "artifact",
            ]
            chat = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).first()
            for col in update_columns:
                val = kwargs.get(col, None)
                if val is not None:
                    setattr(chat, col, val)
                    flag_modified(chat, col)
            conn.commit()
            return chat.id #chat.to_dict()
        d = self.db.execute(thd)
        return d

    def delete_chat(self, chat_id):
        def thd(conn):
            result = conn.query(self.tbl).filter(
                self.tbl.id == chat_id).delete()
            conn.commit()
            return result
        d = self.db.execute(thd)
        return d
